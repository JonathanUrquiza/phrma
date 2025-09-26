from django.db import models, transaction
from django.core.exceptions import ValidationError

def validar_ean13(value: str):
    s = "".join(ch for ch in (value or "") if ch.isdigit())
    if len(s) != 13:
        raise ValidationError("GTIN/EAN-13 debe tener 13 dígitos")
    digits = list(map(int, s))
    check = digits.pop()
    calc = (10 - (sum(d if i % 2 == 0 else d * 3 for i, d in enumerate(digits)) % 10)) % 10
    if calc != check:
        raise ValidationError("GTIN/EAN-13 con dígito verificador inválido")

class Producto(models.Model):
    gtin = models.CharField(max_length=14, unique=True, validators=[validar_ean13])
    nombre = models.CharField(max_length=200)
    laboratorio = models.CharField(max_length=200, blank=True)
    estado = models.CharField(max_length=10, default='activo')  # activo/inactivo
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} ({self.gtin})"

class Lote(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='lotes')
    numero_lote = models.CharField(max_length=80)
    fecha_venc = models.DateField()
    stock = models.IntegerField(default=0)

    class Meta:
        unique_together = ('producto', 'numero_lote')

    def clean(self):
        if self.stock < 0:
            raise ValidationError("El stock inicial no puede ser negativo")

    def __str__(self):
        return f"Lote {self.numero_lote} - {self.producto.nombre}"


class MovimientoStock(models.Model):
    TIPOS = (('INGRESO','INGRESO'), ('EGRESO','EGRESO'), ('AJUSTE','AJUSTE'))
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=10, choices=TIPOS)
    cantidad = models.IntegerField()
    motivo = models.CharField(max_length=255, blank=True)
    documento_ref = models.CharField(max_length=100, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} {self.cantidad} en {self.lote}"

    @transaction.atomic
    def aplicar(self):
        """Aplica el movimiento al stock del lote, con validaciones."""
        l = Lote.objects.select_for_update().get(pk=self.lote_id)
        if self.tipo == 'INGRESO':
            l.stock += self.cantidad
        elif self.tipo == 'EGRESO':
            if self.cantidad > l.stock:
                raise ValidationError("Stock insuficiente en el lote")
            l.stock -= self.cantidad
        elif self.tipo == 'AJUSTE':
            # Ajuste puede ser positivo o negativo, pero nunca dejar negativo
            nuevo = l.stock + self.cantidad
            if nuevo < 0:
                raise ValidationError("El ajuste dejaría stock negativo")
            l.stock = nuevo
        l.save()

    def save(self, *args, **kwargs):
        is_new = self._state.adding  # True si el objeto se está creando
        super().save(*args, **kwargs)  # guardamos primero
        if is_new:  # aplicamos solo en creación
            self.aplicar()