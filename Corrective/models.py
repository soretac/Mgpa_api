from django.db import models
from Travaux.models import DTPrev, DTCurative



class ActionCorrective(models.Model):

    dt_ep = models.ForeignKey(DTPrev, null=True, on_delete=models.SET_NULL, related_name="dtep_ac")
    dt_cur = models.ForeignKey(DTCurative, null=True, on_delete=models.SET_NULL, related_name="dtcur_ac")
    session = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField()
    organe = models.CharField(max_length=100, blank=True, null=True)
    anomalie = models.CharField(max_length=255, blank=True, null=True)
    statut = models.CharField()
