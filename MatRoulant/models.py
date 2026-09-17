from django.db import models
from Entreprise.models import Organigramme
from django.db.models.signals import post_save
from django.conf import settings
from MgpaUsers.models import UserAccount




class VehiculesEses(models.Model):

    TypeCompt = [
        ("HORAIRE", "HORAIRE"),
        ("KILOMETRIQUE", "KILOMETRIQUE"),
    ]

    cateng = [
        ("PL1", "POIDS LOURD 1GEN"),
        ("PL2", "POIDS LOURD 2GEN"),
        ("VL", "VEHICULE LEGER"),
        ("MN", "MANUTENTION"),
    ]

    ENERGIES = [
        ("ESSENCE", "ESSENCE"),
        ("DIESEL", "DIESEL"),
        ("GAZ", "GAZ"),
        ("ELECTRIQUE", "ELECTRIQUE"),
    ]

    TypeStatut = [
        ("EN SERVICE", "EN SERVICE"),
        ("EN MAINTENANCE", "EN MAINTENANCE"),
        ("EN REFORMATION", "EN REFORMATION"),
        ("LITIGIEUX", "LITIGIEUX"),
        ("HORS SERVICE", "HORS SERVICE"),
        ("SINISTRE", "SINISTRE"),
        ("EN EP", "EN EP"),
    ]

    num_parc              = models.CharField("N° PARC", max_length=100, blank=True, null=True)
    immat                 = models.CharField("IMMATRICULATION", max_length=100, blank=True, null=True, unique=True)
    typecompteur          = models.CharField("Unite compteur", max_length=50, blank=True, choices=TypeCompt)
    categorie             = models.CharField("CATEGORIE", max_length=100, null=True, blank=True, choices=cateng)
    type                  = models.CharField("TYPE", max_length=50, null=True, blank=True)
    marque                = models.CharField("MARQUE", max_length=50, null=True, blank=True)
    model                 = models.CharField("MODEL", max_length=50, null=True, blank=True)
    energie               = models.CharField("ENERGIE", max_length=50, null=True, blank=True, choices=ENERGIES)
    puissance             = models.CharField("PUISSANCE", max_length=20, null=True, blank=True)
    serie                 = models.CharField("N° SERIE", max_length=255, null=True, blank=True)
    branding              = models.CharField("BRANDING", max_length=255, null=True, blank=True)
    date_mse              = models.CharField("DATE DE SERVICE", null=True, blank=True)
    statut                = models.CharField("STATUT", max_length=50, blank=True, choices=TypeStatut, default="En SERVICE")
    affectation           = models.ForeignKey(Organigramme, null=True, blank=True, on_delete=models.SET_NULL, related_name='affectations')
    # site_fonct            = models.ForeignKey(Organigramme, null=True, blank=True, on_delete=models.SET_NULL, related_name='veh_site_fonct')
    site_matrlt           = models.ForeignKey(Organigramme, null=True, blank=True, on_delete=models.SET_NULL, related_name='veh_site_matrlt')
    conducteurs           = models.ManyToManyField(UserAccount, blank=True, related_name="veh_conducteurs")
    identite              = models.CharField("IDENTITE", max_length=255, null=True, blank=True)



    def __str__(self):
        return self.identite
    


class AssurVeh(models.Model):
    vehicule = models.ForeignKey(VehiculesEses, null=True, on_delete=models.CASCADE, related_name="veh_assurance")
    ref      = models.CharField("ASSUREUR", max_length=255, null=True, blank=True)
    date     = models.CharField("DATE", null=True, blank=True)
    type     = models.CharField("TYPE", max_length=255, null=True, blank=True)
    montant  = models.IntegerField("MONTANT", default=0, blank=True)   
    duree    = models.CharField("DUREE", max_length=255, null=True, blank=True)
    date_fin = models.CharField("DATE FIN", max_length=255, null=True, blank=True)


    def __str__(self):
        return f"{self.vehicule.immat}-{self.type}-{self.date_fin}"
    


class VisiteVeh(models.Model):
    vehicule = models.ForeignKey(VehiculesEses, null=True, on_delete=models.CASCADE, related_name="veh_visitech")
    ref      = models.CharField("REFERENCE", max_length=255, null=True, blank=True)
    centre   = models.CharField("CENTRE TECHNIQUE", max_length=255, null=True, blank=True)
    date     = models.CharField("DATE", null=True, blank=True)
    resultat = models.CharField("RESULTAT", max_length=255, null=True, blank=True)
    montant  = models.IntegerField("MONTANT", default=0, blank=True)
    date_fin = models.CharField("DATE FIN", max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.vehicule.immat}-{self.resultat}-{self.date_fin}"


class CGVeh(models.Model):

    vehicule = models.ForeignKey(VehiculesEses, null=True, on_delete=models.CASCADE, related_name="cartegrise")
    ref      = models.CharField("REFERENCE", max_length=255, null=True, blank=True)
    date     = models.CharField("DATE", null=True, blank=True)
    montant  = models.IntegerField("MONTANT", default=0, blank=True)
    date_fin = models.CharField("DATE FIN", max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.vehicule.immat}-{self.ref}-{self.date_fin}"

