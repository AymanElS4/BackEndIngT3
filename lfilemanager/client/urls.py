from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    register_view, login_view, me_view,
    RolViewSet, UsuarioViewSet, TipoCasoViewSet,
    EstadoCasoViewSet, CasoViewSet, CodigoLegalViewSet,
    CasoNormativaViewSet, DocumentoViewSet
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

urlpatterns = [
    # Auth
    path('auth/register/', register_view, name='register'),
    path('auth/login/', login_view, name='login'),
    path('auth/me/', me_view, name='me'),
    
    # API Router
    path('', include(router.urls)),
]
