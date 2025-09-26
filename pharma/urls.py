from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from stock.views import ProductoViewSet, LoteViewSet, MovimientoViewSet, scan, lotes_por_vencer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView  # <-- ya lo importaste


router = DefaultRouter()
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'lotes', LoteViewSet, basename='lote')
router.register(r'movimientos', MovimientoViewSet, basename='movimiento')

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/scan/<str:codigo>/', scan),
    path('api/reportes/por_vencer/', lotes_por_vencer),

    # JWT (login y refresh)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]