from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()

class NonCancellareSuperuser(permissions.BasePermission):
    """
    Permette l'azione solo se l'utente target NON è un superuser.
    Impedisce l'eliminazione dell'admin tramite API.
    """

    def has_permission(self, request, view):
        # Permette tutte le azioni per l'admin, tranne DELETE
        if request.method in permissions.SAFE_METHODS or request.method == 'POST':
            return True
        
        # Per le operazioni come PUT/PATCH/DELETE a livello di lista,
        # applichiamo la regola a livello di oggetto (has_object_permission)
        return True

    def has_object_permission(self, request, view, obj):
        # La regola si applica solo al metodo DELETE
        if request.method == 'DELETE':
            # Se l'utente target (obj) è un superuser, NEGA l'accesso (return False)
            if obj.is_superuser:
                raise PermissionError("Non è permesso cancellare un superuser.")
        
        return True