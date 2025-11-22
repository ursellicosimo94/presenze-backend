from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .serializers import (
    UtenteRegistrazioneSerializer, 
    UtenteDettaglioSerializer, 
    UtenteAggiornaPasswordSerializer
)
from .permissions import NonCancellareSuperuser

User = get_user_model()

class UtenteViewSet(
    mixins.RetrieveModelMixin,   # GET (singolo utente)
    mixins.UpdateModelMixin,     # PUT/PATCH (aggiornamento)
    mixins.DestroyModelMixin,    # DELETE (eliminazione)
    mixins.ListModelMixin,       # GET (lista utenti)
    viewsets.GenericViewSet
):
    """
    ViewSet per gestire le operazioni CRUD sugli utenti.
    """
    queryset = User.objects.all().order_by('username')
    serializer_class = UtenteDettaglioSerializer
    
    # Permission di default: richiedono l'autenticazione per ogni operazione.
    # Chiunque può vedere la lista o i dettagli.
    permission_classes = [IsAuthenticated, NonCancellareSuperuser] 
    
    def get_permissions(self):
        """
        Definisce le permission in base all'azione.
        Solo gli amministratori possono listare, aggiornare o eliminare altri utenti.
        """
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            # Per CRUD completo, richiediamo l'admin
            # Applichiamo anche la custom permission per impedire il delete del superuser
            self.permission_classes = [IsAdminUser, NonCancellareSuperuser] 
        elif self.action == 'me':
             # L'utente autenticato può vedere e aggiornare solo il suo profilo.
            self.permission_classes = [IsAuthenticated]
        
        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self): # type: ignore
        """
        Restituisce il serializer corretto in base all'azione.
        """
        if self.action == 'set_password':
            return UtenteAggiornaPasswordSerializer
        return self.serializer_class

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def registra(self, request):
        """
        Endpoint di registrazione pubblica (/api/utenti/registra/).
        Non richiede autenticazione.
        """
        serializer = UtenteRegistrazioneSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UtenteDettaglioSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get', 'put', 'patch'], url_path='me')
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(request.user, data=request.data, partial=request.method == 'PATCH')
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='activate')
    def activate(self, request, pk=None):
        """
        Endpoint per disattivare un utente
        URL: /api/utenti/{id}/activate/
        """
        if not request.user.is_superuser or request.user.id == int(pk): # type: ignore
            """
            Impedisce a utenti non admin di disattivare chiunque e all'admin di disattivare se stesso
            """
            return Response(
                {"detail": "Non hai il permesso di attivare questo utente."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"detail": "Utente non trovato."},
                status=status.HTTP_404_NOT_FOUND
            )

        user.is_active = True
        user.save()

        return Response(status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['delete'], url_path='deactivate')
    def deactivate(self, request, pk=None):
        """
        Endpoint per disattivare un utente
        URL: /api/utenti/{id}/deactivate/
        """
        if not request.user.is_superuser or request.user.id == int(pk): # type: ignore
            """
            Impedisce a utenti non admin di disattivare chiunque e all'admin di disattivare se stesso
            """
            return Response(
                {"detail": "Non hai il permesso di disattivare questo utente."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"detail": "Utente non trovato."},
                status=status.HTTP_404_NOT_FOUND
            )

        user.is_active = False
        user.save()

        return Response(status=status.HTTP_200_OK)
        
        
    @action(detail=True, methods=['post'], url_path='set-password')
    def set_password(self, request, pk=None):
        """
        Permette di cambiare la password di un utente specifico (richiede PK e Admin).
        URL: /api/utenti/{id}/set-password/
        """
        # Garantisce che solo l'admin possa cambiare la password degli altri
        if not request.user.is_superuser and request.user.id != int(pk): # type:ignore
            return Response(
                {"detail": "Non hai il permesso di cambiare la password di questo utente."},
                status=status.HTTP_403_FORBIDDEN
            )

        user = self.get_object()
        serializer = UtenteAggiornaPasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.update(user, serializer.validated_data)
            return Response({'detail': 'Password aggiornata con successo.'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)