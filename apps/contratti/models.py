from django.db import models
from apps.dipendenti.models import Dipendente
from django.contrib.auth.models import User
from datetime import datetime, timedelta, time

TIPO_CONTRATTO = (
    ('IND', 'Indeterminato'),
    ('DET', 'Determinato'),
    ('SOST', 'Sostituzione'),
    ('OCC', 'Occasionale'),
    ('PIVA', 'Partita IVA'),
)

TIPO_BUSTA_PAGA = (
    ('PAGA', 'Busta Paga'),
    ('13', 'Tredicesima'),
    ('14', 'Quattordicesima'),
    ('TFR', 'TFR'),
    ('ATFR', 'Anticipo TFR'),
    ('FATT', 'Fattura'),
    ('ALTRO', 'Altro'),
)

class Ccnl(models.Model):
    """
    Definizione dei contratti collettivi nazionali di lavoro.
    """
    nome = models.CharField(max_length=150, unique=True, verbose_name='Nome CCNL')
    n_mensilita = models.SmallIntegerField(default=13, verbose_name='Numero Mensilità Annuali')

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "CCNL"
        verbose_name_plural = "CCNL"

class Contratto(models.Model):
    """
    Dati del contratto in vigore per un Dipendente, con validità temporale.
    """
    dipendente = models.ForeignKey(
        Dipendente,
        on_delete=models.CASCADE,
        related_name='contratti',
        verbose_name='Dipendente'
    )
    ore_settimanali = models.SmallIntegerField(
        null=True,
        blank=True,
        verbose_name='Ore Settimanali (1-40, Null per P.IVA/Occasionale)'
    )
    tipo = models.CharField(
        max_length=4,
        choices=TIPO_CONTRATTO,
        default='IND',
        verbose_name='Tipo di Contratto'
    )
    dal = models.DateField(verbose_name='Data Inizio Contratto')
    al = models.DateField(
        null=True,
        blank=True,
        verbose_name='Data Fine Contratto'
    )
    note = models.TextField(
        blank=True,
        null=True,
        verbose_name='Note Contratto'
    )
    ccnl = models.ForeignKey(
        Ccnl,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contratti_associati',
        verbose_name='CCNL di Riferimento'
    )
    
    def get_tipo_display(self)->str:
        """Restituisce la descrizione testuale del tipo di contratto."""
        return dict(TIPO_CONTRATTO).get(self.tipo, 'Sconosciuto')
    
    def __str__(self):
        return f"Contratto {self.get_tipo_display()} per {self.dipendente.cognome} ({self.dal})"

    class Meta:
        verbose_name = "Contratto"
        verbose_name_plural = "Contratti"
        ordering = ['-dal']

class OrariContrattuali(models.Model):
    """
    Definizione degli orari standard associati a un Contratto specifico, giorno per giorno.
    Gestisce fino a tre fasce orarie spezzate (f1, f2, f3).
    """
    contratto = models.ForeignKey(
        Contratto,
        on_delete=models.CASCADE,
        related_name='orari',
        verbose_name='Contratto di Riferimento'
    )
    dow = models.SmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 8)], # 1=Lunedì a 7=Domenica
        verbose_name='Giorno della Settimana (DOW)'
    )
    
    f1_start = models.TimeField(null=True, blank=True, verbose_name='Fascia 1 Inizio')
    f1_end = models.TimeField(null=True, blank=True, verbose_name='Fascia 1 Fine')
    
    f2_start = models.TimeField(null=True, blank=True, verbose_name='Fascia 2 Inizio')
    f2_end = models.TimeField(null=True, blank=True, verbose_name='Fascia 2 Fine')
    
    f3_start = models.TimeField(null=True, blank=True, verbose_name='Fascia 3 Inizio')
    f3_end = models.TimeField(null=True, blank=True, verbose_name='Fascia 3 Fine')

    def _calculate_duration(self, start: time, end: time) -> timedelta:
        """Calcola la durata tra due orari TimeField."""
        if start is None or end is None:
            return timedelta(0)
        
        dt_start = datetime.combine(datetime.min.date(), start)
        dt_end = datetime.combine(datetime.min.date(), end)
        
        if dt_end < dt_start:
            dt_end += timedelta(days=1)
            
        return dt_end - dt_start

    @property
    def delta_f1(self) -> timedelta:
        """Durata della Fascia 1 (proprietà virtuale)"""
        return self._calculate_duration(self.f1_start, self.f1_end) # type: ignore

    @property
    def delta_f2(self) -> timedelta:
        """Durata della Fascia 2 (proprietà virtuale)"""
        return self._calculate_duration(self.f2_start, self.f2_end) # type: ignore

    @property
    def delta_f3(self) -> timedelta:
        """Durata della Fascia 3 (proprietà virtuale)"""
        return self._calculate_duration(self.f3_start, self.f3_end) # type: ignore

    @property
    def ore_giorno(self) -> float:
        """Totale ore calcolate per il giorno (proprietà virtuale, in float)"""
        total_delta = self.delta_f1 + self.delta_f2 + self.delta_f3
        return total_delta.total_seconds() / 3600.0

    def __str__(self):
        return f"Orario Giorno {self.dow} per Contratto ID {self.contratto.id}" # type: ignore

    class Meta:
        verbose_name = "Orario Contrattuale"
        verbose_name_plural = "Orari Contrattuali"
        unique_together = ('contratto', 'dow')
        ordering = ['contratto', 'dow']

class Straordinario(models.Model):
    """
    Registrazione delle ore di straordinario effettuate.
    """
    contratto = models.ForeignKey(
        Contratto,
        on_delete=models.CASCADE,
        related_name='straordinari',
        verbose_name='Contratto di Riferimento'
    )
    inizio = models.DateTimeField(verbose_name='Data e Ora Inizio Straordinario')
    fine = models.DateTimeField(verbose_name='Data e Ora Fine Straordinario')
    
    utente_richiedente = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Utente Richiedente/Registrante'
    )
    
    @property
    def delta(self) -> timedelta:
        """Durata totale dello straordinario (proprietà virtuale: fine - inizio)"""
        if self.fine and self.inizio and self.fine > self.inizio:
            return self.fine - self.inizio
        return timedelta(0)

    @property
    def ore_svolte(self) -> float:
        """Durata dello straordinario in ore decimali (proprietà virtuale)."""
        return self.delta.total_seconds() / 3600.0
        
    def __str__(self):
        return f"Straordinario dal {self.inizio.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = "Straordinario"
        verbose_name_plural = "Straordinari"
        ordering = ['-inizio']

class BustaPaga(models.Model):
    """
    Registro delle buste paga/documenti di pagamento emessi.
    """
    contratto = models.ForeignKey(
        Contratto,
        on_delete=models.CASCADE,
        related_name='buste_paga_emesse',
        verbose_name='Contratto di Riferimento'
    )
    anno = models.SmallIntegerField(verbose_name='Anno di Riferimento')
    mese = models.SmallIntegerField(verbose_name='Mese di Riferimento (1-12)')
    data_caricamento = models.DateTimeField(auto_now_add=True, verbose_name='Data Caricamento Documento')
    nome = models.CharField(max_length=255, verbose_name='Descrizione del Documento')
    tipo = models.CharField(
        max_length=5,
        choices=TIPO_BUSTA_PAGA,
        default='PAGA',
        verbose_name='Tipo di Documento'
    )
    
    file_documento = models.FileField(
        upload_to='buste_paga/',
        null=True,
        blank=True,
        verbose_name='File Busta Paga/Fattura (PDF, ecc.)'
    )
        
    def __str__(self):
        return f"{self.tipo} per {self.contratto.dipendente.cognome} ({self.anno}/{self.mese})"

    class Meta:
        verbose_name = "Busta Paga/Documento di Pagamento"
        verbose_name_plural = "Buste Paga/Documenti di Pagamento"
        unique_together = ('contratto', 'anno', 'mese', 'tipo')
        ordering = ['-anno', '-mese']