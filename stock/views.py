from datetime import date

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Producto, Lote, MovimientoStock
from .serializers import ProductoSerializer, LoteSerializer, MovimientoStockSerializer
from .permissions import IsStaffOrReadOnly


# ---------------------------------------
# ProductoViewSet
# ---------------------------------------
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all().order_by('-id')
    serializer_class = ProductoSerializer
    permission_classes = [IsStaffOrReadOnly]  # default del viewset

    @action(
        detail=True,
        methods=['post'],
        url_path='egreso-fefo',
        permission_classes=[IsAuthenticated],
        authentication_classes=[JWTAuthentication],
    )
    def egreso_fefo(self, request, pk=None):
        """
        POST /api/productos/{id}/egreso-fefo/
        Body: {"cantidad": 5, "motivo": "...", "documento_ref": "..."}
        Toma el lote con fecha de vencimiento más próxima que tenga stock suficiente.
        """
        prod = self.get_object()
        try:
            cantidad = int(request.data.get('cantidad', 0))
        except (TypeError, ValueError):
            return Response({"detail": "cantidad inválida"}, status=400)
        if cantidad <= 0:
            return Response({"detail": "cantidad debe ser > 0"}, status=400)

        lote = Lote.objects.filter(producto=prod, stock__gte=cantidad).order_by('fecha_venc').first()
        if not lote:
            return Response({"detail": "No hay lote con stock suficiente"}, status=400)

        ser = MovimientoStockSerializer(data={
            "lote": lote.id,
            "tipo": "EGRESO",
            "cantidad": cantidad,
            "motivo": request.data.get("motivo", "Egreso FEFO"),
            "documento_ref": request.data.get("documento_ref", ""),
        })
        ser.is_valid(raise_exception=True)
        ser.save()

        return Response({
            "ok": True,
            "producto": {"id": prod.id, "gtin": prod.gtin, "nombre": prod.nombre},
            "lote_usado": {
                "id": lote.id,
                "numero_lote": lote.numero_lote,
                "fecha_venc": lote.fecha_venc,
                "stock_actual": lote.stock,
            }
        }, status=200)

    @action(
        detail=False,
        methods=['post'],
        url_path='ingreso-scan',
        permission_classes=[IsAuthenticated],
        authentication_classes=[JWTAuthentication],
    )
    def ingreso_scan(self, request):
        """
        Crea o busca Producto + Lote a partir de un scan
        y suma 1 (o 'cantidad') al stock.
        """
        # DEBUG: ver si llega el header Authorization
        print("DEBUG AUTH >>>", request.META.get("HTTP_AUTHORIZATION"))

        gtin = str(request.data.get('gtin', '')).strip()
        if not gtin:
            return Response({'detail': 'gtin requerido'}, status=400)

        producto, _ = Producto.objects.get_or_create(
            gtin=gtin,
            defaults={'nombre': f'Producto {gtin}', 'laboratorio': '', 'estado': 'activo'}
        )

        numero_lote = (request.data.get('lote') or 'SIN-LOTE').strip()
        fecha_venc = request.data.get('fecha_venc')
        if fecha_venc:
            try:
                y, m, d = map(int, fecha_venc.split('-'))
                fecha_venc = date(y, m, d)
            except Exception:
                return Response({'detail': 'fecha_venc inválida (usar YYYY-MM-DD)'}, status=400)
        else:
            fecha_venc = date(2099, 12, 31)

        lote, _ = Lote.objects.get_or_create(
            producto=producto,
            numero_lote=numero_lote,
            defaults={'fecha_venc': fecha_venc, 'stock': 0}
        )

        try:
            cantidad = int(request.data.get('cantidad', 1))
        except (TypeError, ValueError):
            cantidad = 1
        if cantidad <= 0:
            return Response({'detail': 'cantidad debe ser > 0'}, status=400)

        movimiento = MovimientoStockSerializer(data={
            'lote': lote.id, 'tipo': 'INGRESO',
            'cantidad': cantidad,
            'motivo': request.data.get('motivo', 'Ingreso SCAN'),
            'documento_ref': request.data.get('documento_ref', 'SCAN'),
        })
        movimiento.is_valid(raise_exception=True)
        movimiento.save()

        return Response({
            'ok': True,
            'producto': ProductoSerializer(producto).data,
            'lote': LoteSerializer(lote).data
        })


# ---------------------------------------
# LoteViewSet
# ---------------------------------------
class LoteViewSet(viewsets.ModelViewSet):
    queryset = Lote.objects.select_related('producto').all().order_by('-id')
    serializer_class = LoteSerializer
    permission_classes = [IsStaffOrReadOnly]

    @action(detail=True, methods=['post'])
    def ingreso(self, request, pk=None):
        lote = self.get_object()
        ser = MovimientoStockSerializer(data={
            'lote': lote.id, 'tipo': 'INGRESO',
            'cantidad': request.data.get('cantidad'),
            'motivo': request.data.get('motivo', ''),
            'documento_ref': request.data.get('documento_ref', ''),
        })
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response({'ok': True, 'lote': LoteSerializer(lote).data})

    @action(detail=True, methods=['post'])
    def egreso(self, request, pk=None):
        lote = self.get_object()
        ser = MovimientoStockSerializer(data={
            'lote': lote.id, 'tipo': 'EGRESO',
            'cantidad': request.data.get('cantidad'),
            'motivo': request.data.get('motivo', ''),
            'documento_ref': request.data.get('documento_ref', ''),
        })
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response({'ok': True, 'lote': LoteSerializer(lote).data})

    @action(detail=True, methods=['post'])
    def ajuste(self, request, pk=None):
        lote = self.get_object()
        ser = MovimientoStockSerializer(data={
            'lote': lote.id, 'tipo': 'AJUSTE',
            'cantidad': request.data.get('cantidad'),
            'motivo': request.data.get('motivo', ''),
            'documento_ref': request.data.get('documento_ref', ''),
        })
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response({'ok': True, 'lote': LoteSerializer(lote).data})


# ---------------------------------------
# MovimientoViewSet (solo lectura)
# ---------------------------------------
class MovimientoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MovimientoStock.objects.select_related('lote', 'lote__producto').all().order_by('-id')
    serializer_class = MovimientoStockSerializer


# ---------------------------------------
# Endpoints sueltos
# ---------------------------------------
@api_view(['GET'])
def scan(request, codigo):
    code = (codigo or '').replace(' ', '').replace('-', '')
    p = Producto.objects.filter(gtin=code).first()
    if not p:
        return Response({'detail': 'No encontrado'}, status=404)
    return Response(ProductoSerializer(p).data, status=200)


@api_view(['GET'])
def lotes_por_vencer(request):
    """
    /api/reportes/por_vencer/?dias=60
    Devuelve lotes con stock>0 que vencen en <= N días (default 60).
    """
    try:
        dias = int(request.GET.get('dias', 60))
    except ValueError:
        dias = 60
    hoy = timezone.now().date()
    limite = hoy + timezone.timedelta(days=dias)

    qs = (Lote.objects
          .select_related('producto')
          .filter(stock__gt=0, fecha_venc__lte=limite)
          .order_by('fecha_venc', 'producto__nombre'))

    data = [{
        "lote_id": l.id,
        "producto_id": l.producto_id,
        "gtin": l.producto.gtin,
        "producto": l.producto.nombre,
        "numero_lote": l.numero_lote,
        "fecha_venc": l.fecha_venc,
        "stock": l.stock,
        "dias_restantes": (l.fecha_venc - hoy).days
    } for l in qs]

    return Response({"hoy": str(hoy), "dias": dias, "items": data}, status=200)