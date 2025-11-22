from rest_framework import serializers
from django.contrib.auth import get_user_model

# Otteniamo il modello User attualmente attivo (di solito django.contrib.auth.models.User)
User = get_user_model()

class UtenteRegistrazioneSerializer(serializers.ModelSerializer):
    """
    Serializer per la registrazione di un nuovo utente.
    """
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        # Campi richiesti per la registrazione
        fields = ('id', 'username', 'email', 'password', 'password2', 'first_name', 'last_name')
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}}
        }

    def validate(self, attrs):
        """Controlla che le password coincidano."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "I campi password devono corrispondere."})
        return attrs
    
    def create(self, validated_data):
        """Crea un nuovo utente e cripta la password."""
        # Rimuove password2, che non è un campo del modello User
        validated_data.pop('password2')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''), # L'email non è obbligatoria per tutti i User model
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        return user


class UtenteDettaglioSerializer(serializers.ModelSerializer):
    """
    Serializer per la lettura e l'aggiornamento dei dati utente (esclusa la password).
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined', 'last_login')
        read_only_fields = ('id', 'is_active', 'is_staff', 'date_joined', 'last_login')


class UtenteAggiornaPasswordSerializer(serializers.Serializer):
    """
    Serializer per cambiare la password di un utente esistente.
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, attrs):
        """Controlla che le password coincidano."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "I campi password devono corrispondere."})
        return attrs
    
    def update(self, instance, validated_data):
        """Imposta la nuova password sull'istanza dell'utente."""
        instance.set_password(validated_data['password'])
        instance.save()
        return instance