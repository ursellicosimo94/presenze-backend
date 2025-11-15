from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

TIPO_INDIRIZZO = (
    ('R', 'Residenza'),
    ('D', 'Domicilio'),
)

class Dipendente(models.Model):
    """
    Modello principale per i dati anagrafici del Dipendente.
    """
    utente = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dipendente_profilo',
        verbose_name='Utente Django (Login)'
    )

    nome = models.CharField(max_length=100, verbose_name='Nome')
    cognome = models.CharField(max_length=100, verbose_name='Cognome')
    codice_fiscale = models.CharField(
        max_length=16,
        unique=True,
        verbose_name='Codice Fiscale',
        validators=[RegexValidator(r'^[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]$')]
    )
    data_nascita = models.DateField(verbose_name='Data di Nascita')
    comune_nascita = models.CharField(max_length=150, verbose_name='Comune di Nascita')

    note = models.TextField(
        blank=True,
        null=True,
        verbose_name='Note Varie (Patente, Invalidità, ecc.)'
    )

    def __str__(self):
        return f"{self.nome} {self.cognome} ({self.codice_fiscale})"

    class Meta:
        verbose_name = "Dipendente"
        verbose_name_plural = "Dipendenti"
        ordering = ['cognome', 'nome']

class IbanDipendente(models.Model):
    """
    Gestisce gli IBAN associati a un Dipendente con validità temporale.
    """
    dipendente = models.ForeignKey(
        Dipendente,
        on_delete=models.CASCADE,
        related_name='ibans',
        verbose_name='Dipendente'
    )
    iban = models.CharField(
        max_length=34,
        verbose_name='IBAN',
    )
    dal = models.DateField(verbose_name='Data Inizio Validità')
    al = models.DateField(
        null=True,
        blank=True,
        verbose_name='Data Fine Validità'
    )

    def __str__(self):
        return f"IBAN per {self.dipendente.cognome} - {self.iban}"

    class Meta:
        verbose_name = "IBAN Dipendente"
        verbose_name_plural = "IBAN Dipendenti"
        constraints = [
            models.UniqueConstraint(fields=['dipendente', 'iban', 'dal'], name='unique_dipendente_iban_dal')
        ]


class IndirizzoDipendente(models.Model):
    """
    Gestisce gli indirizzi (Residenza/Domicilio) con validità temporale.
    """
    dipendente = models.ForeignKey(
        Dipendente,
        on_delete=models.CASCADE,
        related_name='indirizzi',
        verbose_name='Dipendente'
    )
    tipo = models.CharField(
        max_length=1,
        choices=TIPO_INDIRIZZO,
        verbose_name='Tipo di Indirizzo'
    )
    
    nazione = models.CharField(
        max_length=100,
        default='Italia',
        verbose_name='Nazione'
    )
    regione = models.CharField(max_length=100, blank=True, null=True, verbose_name='Regione')
    provincia = models.CharField(max_length=100, blank=True, null=True, verbose_name='Provincia')
    citta = models.CharField(max_length=150, verbose_name='Città')
    cap = models.CharField(
        max_length=10,
        verbose_name='CAP',
    )

    indirizzo = models.CharField(max_length=255, verbose_name='Via/Piazza')
    civico = models.CharField(max_length=20, blank=True, verbose_name='Numero Civico')
    
    dal = models.DateField(verbose_name='Data Inizio Validità')
    al = models.DateField(
        null=True,
        blank=True,
        verbose_name='Data Fine Validità'
    )
    
    def get_tipo_display(self)->str:
        return dict(TIPO_INDIRIZZO).get(self.tipo, 'Sconosciuto')

    def __str__(self):
        return f"{self.get_tipo_display()} per {self.dipendente.cognome}: {self.indirizzo}"

    class Meta:
        verbose_name = "Indirizzo Dipendente"
        verbose_name_plural = "Indirizzi Dipendenti"
        constraints = [
            models.UniqueConstraint(fields=['dipendente', 'tipo', 'dal'], name='unique_dipendente_tipo_dal')
        ]

class EmailDipendente(models.Model):
    """
    Gestisce gli indirizzi email associati al Dipendente.
    """
    dipendente = models.ForeignKey(
        Dipendente,
        on_delete=models.CASCADE,
        related_name='emails',
        verbose_name='Dipendente'
    )
    email = models.EmailField(unique=True, verbose_name='Indirizzo Email')
    attivo = models.BooleanField(default=True, verbose_name='Attivo')
    principale = models.BooleanField(default=False, verbose_name='Email Principale')
    
    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Email Dipendente"
        verbose_name_plural = "Email Dipendenti"
        constraints = [
             models.UniqueConstraint(
                fields=['dipendente'],
                condition=models.Q(principale=True, attivo=True),
                name='unico_email_principale_attiva'
            )
        ]


class CellulareDipendente(models.Model):
    dipendente = models.ForeignKey(
        Dipendente,
        on_delete=models.CASCADE,
        related_name='cellulari',
        verbose_name='Dipendente'
    )
    cellulare = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Numero di Cellulare'
    )
    attivo = models.BooleanField(default=True, verbose_name='Attivo')
    principale = models.BooleanField(default=False, verbose_name='Cellulare Principale')
    
    def __str__(self):
        return self.cellulare

    class Meta:
        verbose_name = "Cellulare Dipendente"
        verbose_name_plural = "Cellulari Dipendenti"
        constraints = [
             models.UniqueConstraint(
                fields=['dipendente'],
                condition=models.Q(principale=True, attivo=True),
                name='unico_cellulare_principale_attivo'
            )
        ]