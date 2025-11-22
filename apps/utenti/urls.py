from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UtenteViewSet

router = DefaultRouter()
router.register(r'', UtenteViewSet, basename='utente')

urlpatterns = [
    path('', include(router.urls)), 
]