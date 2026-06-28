"""URL configuration for the client (API) application."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    register_view, login_view, me_view,
    password_reset_view, verify_2fa_view, generar_reporte_pdf_view,
    RolViewSet, UsuarioViewSet, TipoCasoViewSet,
    EstadoCasoViewSet, CasoViewSet, CodigoLegalViewSet,
    RequestPasswordResetView, ConfirmPasswordResetView,
    CasoNormativaViewSet, DocumentoViewSet,
    PlanViewSet, PagoViewSet, NotificacionViewSet,
)

router = DefaultRouter()
router.register(r'roles', RolViewSet, basename='rol')
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'tipos-caso', TipoCasoViewSet, basename='tipo-caso')
router.register(r'estados-caso', EstadoCasoViewSet, basename='estado-caso')
router.register(r'casos', CasoViewSet, basename='caso')
router.register(r'codigos', CodigoLegalViewSet, basename='codigo-legal')
router.register(r'caso-normativas', CasoNormativaViewSet, basename='caso-normativa')
router.register(r'documentos', DocumentoViewSet, basename='documento')
router.register(r'planes', PlanViewSet, basename='plan')
router.register(r'pagos', PagoViewSet, basename='pago')
router.register(r'notificaciones', NotificacionViewSet, basename='notificacion')

urlpatterns = [
    # Auth
    path('auth/register/', register_view, name='register'),
    path('auth/login/', login_view, name='login'),
    path('auth/me/', me_view, name='me'),
    path('auth/password-reset/', password_reset_view, name='password-reset'),
    path('auth/2fa/verify/', verify_2fa_view, name='2fa-verify'),
    path(
        'auth/password-reset-request/',
        RequestPasswordResetView.as_view(),
        name='password-reset-request',
    ),
    path(
        'auth/password-reset-confirm/',
        ConfirmPasswordResetView.as_view(),
        name='password-reset-confirm',
    ),
    # Reports
    path('reportes/caso/<int:caso_id>/pdf/', generar_reporte_pdf_view, name='reporte-pdf'),
    # API Router
    path('', include(router.urls)),
]
