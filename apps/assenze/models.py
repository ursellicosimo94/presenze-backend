from apps.contratti.models import Contratto, OrariContrattuali
from django.contrib.auth.models import User
from django.db import models

class TipoAssenza(models.Model):
    """
    Definizione dei tipi di assenza (Ferie, Malattia, Permesso, etc.).
    """
    nome = models.CharField(max_length=100, unique=True, verbose_name='Nome Tipo Assenza')
    richiede_approvazione = models.BooleanField(
        default=True,
        verbose_name='Richiede Approvazione Manageriale'
    )
    richiede_id_nazionale = models.BooleanField(
        default=False,
        verbose_name='Richiede un id nazionale'
    )
    codice_assenza = models.CharField(
        max_length=5,
        null=False,
        blank=False,
        verbose_name="Codice assenza",
        default="A"
    )

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Tipo di Assenza"
        verbose_name_plural = "Tipi di Assenza"

class Assenza(models.Model):
    """
    Registrazione di una singola giornata o intervallo di assenza.
    """
    contratto = models.ForeignKey(
        Contratto,
        on_delete=models.CASCADE,
        related_name='assenze',
        verbose_name='Contratto di Riferimento'
    )
    tipo_assenza = models.ForeignKey(
        TipoAssenza,
        on_delete=models.PROTECT, 
        related_name='assenze_associate',
        verbose_name='Tipo di Assenza'
    )
    data = models.DateField(verbose_name='Data Assenza')
    giornata_intera = models.BooleanField(
        default=True,
        verbose_name='Giornata Intera'
    )
    
    # Popolati solo se giornata_intera è False
    inizio = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Ora Inizio Assenza (se parziale)'
    )
    fine = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Ora Fine Assenza (se parziale)'
    )
    
    id_nazionale = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Codice Assenza Esterno (es. PUK Malattia)'
    )
    
    utente_inserimento = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assenze_inserite',
        verbose_name='Utente Inserimento'
    )
    approvata = models.BooleanField(
        default=False,
        verbose_name='Assenza Approvata'
    )
    utente_approvazione = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assenze_approvate',
        verbose_name='Utente Approvazione'
    )
    
    @property
    def dow(self) -> 'int|None':
        """Giorno della settimana (1=Lunedì, 7=Domenica) calcolato da 'data'."""
        return self.data.weekday() + 1 if self.data else None

    @property
    def ore(self) -> float:
        """Ore di assenza (calcolato dinamicamente)."""
        if not self.data:
            return 0.0

        if not self.giornata_intera and self.inizio and self.fine and self.fine > self.inizio:
            delta = self.fine - self.inizio
            return delta.total_seconds() / 3600.0

        if self.giornata_intera:
            try:
                OrariContrattuali = self.contratto.orari.model # type: ignore
                orario_giorno = self.contratto.orari.get(dow=self.dow) # type: ignore
                return orario_giorno.ore_giorno
            except OrariContrattuali.DoesNotExist: # type: ignore
                return 0.0
            except Exception:
                return 0.0

        return 0.0 
        
    def __str__(self):
        return f"Assenza {self.tipo_assenza.nome} il {self.data.strftime('%d/%m/%Y')} per {self.contratto.dipendente.cognome}"

    class Meta:
        verbose_name = "Assenza"
        verbose_name_plural = "Assenze"
        ordering = ['-data']