from django.db import models
from MatRoulant.models import VehiculesEses
from django.contrib.auth import get_user_model
from django.conf import settings
import uuid
from Entreprise.models import Organigramme
from decimal import Decimal

User = get_user_model()

class Compteurs(models.Model):

    STATUT_COMPT = [
        ("USUEL", "USUEL"),
        ("EP", "EP"),
        
    ]

    vehicule            = models.ForeignKey(VehiculesEses, null=True, on_delete= models.SET_NULL, related_name='veh_compteur')
    start_compt         = models.FloatField(null=True)
    last_compt          = models.FloatField(null=True)
    compt_act           = models.FloatField(null=True)
    date_compt          = models.DateTimeField(auto_now_add=True)
    releveur            = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,  on_delete=models.SET_NULL)
    ecart               = models.FloatField(null=True)
    statut_compt        = models.CharField(max_length=15, choices=STATUT_COMPT, default="USUEL")


    def __str__(self):
        return f"{self.vehicule.num_parc} - {self.compt_act} - {self.date_compt}"
    

class AlerteEp(models.Model):
    
    ALTEP = [
        ("0", "0"),
        ("250 H", "250 H"),
        ("500 H", "500 H"),
        ("750 H", "750 H"),
        ("1000 H", "1000 H"),
        ("1250 H", "1250 H"),
        ("1500 H", "1500 H"),
        ("1750 H", "1750 H"),
        ("2000 H", "2000 H"),
        ("5000 KM", "5000 KM"),
        ("10000 KM", "10000 KM"),
        ("15000 KM", "15000 KM"),
        ("20000 KM", "20000 H"),
        ("25000 KM", "25000 KM"),
        ("30000 KM", "30000 KM"),
        ("40000 KM", "40000 KM"),
        ("50000 KM", "50000 KM"),
        ("60000 KM", "60000 KM"),
        ("150 H", "150 H"),
        ("300 H", "300 H"),
        ("450 H", "450 H"),
        ("600 H", "600 H"),
        ("750 H", "750 H"),
        ("900 H", "900 H"),
        ("1050 H", "1050 H"),
        ("1200 H", "1200 H"),
        
    ]

    STATUT_ALERTE = [
        ("EN ATTENTE", "EN ATTENTE"),
        ("EN DEMANDE", "EN DEMANDE"),
        ("EFFECTUEE", "EFFECTUEE")
    ]

    TYPEALERT = [
        ("A VIDANGER", "A VIDANGER"),
        ("EN DEPASSEMENT", "EN DEPASSEMENT"),
        ("EN DEPASSEMENT DANGER", "EN DEPASSEMENT DANGER"),
        ("EN DEPASSEMENT CRITIQUE", "EN DEPASSEMENT CRITIQUE"),
    ]

    destinataires = models.ManyToManyField(User, blank=True, related_name="alertep_utilisateur")
    alerte = models.CharField("Alerte", max_length=50, blank=True, choices=ALTEP, default="0")
    message = models.CharField("Message", max_length=255, null=True, blank=True) 
    compt = models.FloatField()
    type_alert = models.CharField(max_length=50, blank=True, choices=TYPEALERT, default="A VIDANGER")
    date_alert = models.DateTimeField(auto_now_add=True)
    ecart = models.FloatField(blank=True, null=True, default=0.0)
    nbalert = models.PositiveIntegerField(default=0)
    vehicule = models.ForeignKey(VehiculesEses, null=True,  on_delete=models.SET_NULL)
    statut = models.CharField(max_length=50, blank=True, choices=STATUT_ALERTE, default="EN ATTENTE")    
    chef_smrlt = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='user_matrlt')
    session_alert = models.CharField(max_length=255, blank=True, null=True)


    def __str__(self):
        return "Alerte {} -- vehicule : {}".format(self.alerte, self.vehicule.num_parc)
    



class CptAlert(models.Model):

    nbalert = models.PositiveIntegerField()
    ecart = models.FloatField()
    date_alert = models.DateTimeField(auto_now_add=True)
    alertep = models.ForeignKey(AlerteEp, on_delete=models.SET_NULL, blank=True, null=True, related_name='alert_cpt')


# Table des comptes des dépassement effectué
class CountCritique(models.Model):

    OPTION = [
        ("OUVERT", "OUVERT"),
        ("FERME", "FERME"),
    ]

    date_count = models.DateTimeField(auto_now_add=True)
    vehicule = models.ForeignKey(VehiculesEses, null=True, on_delete=models.SET_NULL, related_name="veh_critique")
    n_depassement = models.PositiveIntegerField() 
    n_danger = models.PositiveIntegerField()
    n_critique = models.PositiveIntegerField()
    ecart = models.FloatField()
    type_ep = models.CharField(max_length=20, blank=True, null=True)
    session = models.CharField(max_length=100, blank=True, null=True)
    statut = models.CharField(max_length=25, choices=OPTION, default="OUVERT")