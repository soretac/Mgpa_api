from django.db import models
from MatRoulant.models import VehiculesEses
from django.conf import settings
import uuid
from Entreprise.models import Organigramme
from django.contrib.auth import get_user_model
from Entreprise.models import Prestations, PieceRechange



User = get_user_model()


class SuiviEp(models.Model):

    STATUTEP = [
        ("EFFECTUE", "EFFECTUE"),
        ("EN ATTENTE", "EN ATTENTE"),
        ("EN DEMANDE", "EN DEMANDE"),
        
    ]


    vehicule = models.ForeignKey(VehiculesEses, null=True, on_delete=models.SET_NULL, related_name='vehicule_suiviep')
    statut_ep = models.CharField(max_length=50, null=True, blank=True, choices=STATUTEP)
    # site_fonct = models.ForeignKey(Organigramme, null=True, blank=True, on_delete=models.SET_NULL, related_name='suivi_site_fonct')
    dernier_ep = models.CharField(max_length=50, null=True, blank=True)
    comptlast_ep = models.FloatField()
    datelast_ep = models.DateField(null=True, blank=True)
    compt_act = models.FloatField()
    compt_cible = models.FloatField()
    ecart = models.FloatField()
    type_alert = models.CharField(max_length=255, blank=True, null=True)
    prochain_ep = models.CharField(max_length=50, null=True, blank=True)
    statut_dt = models.CharField(max_length=100, blank=True, null=True)
    site_matrlt = models.ForeignKey(Organigramme, null=True, blank=True, on_delete=models.SET_NULL, related_name='suivi_site_matrlt')
    session_alerte = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "{} - {} - {}".format(self.vehicule.immat, self.prochain_ep, self.statut_ep)
    


class Eps(models.Model):

    ETATEP = [
        ("EFFECTUE", "EFFECTUE"),
        ("NON EFFECTUE", "NON EFFECTUE"),   
    ]

    vehicule = models.ForeignKey(VehiculesEses, null=True, on_delete=models.SET_NULL, related_name='vehicule_eps')
    statut_dt = models.CharField(max_length=100, blank=True, null=True)
    type_ep = models.CharField(max_length=255, blank=True, null=True)
    compt_alert = models.FloatField()
    date_recept = models.DateField(auto_now_add=True)
    date_ep = models.DateField(null=True)
    compt_ep = models.FloatField(null=True)
    etat_ep = models.CharField(max_length=20, choices=ETATEP, default="NON EFFECTUE")
    observation = models.TextField()
    garagiste = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='garagiste_eps')

    def __str__(self):
        return "{} - {} - {}".format(self.vehicule.immat, self.type_ep, self.etat_ep)




    



    

    











