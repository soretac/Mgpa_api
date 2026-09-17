from django.db import models
import uuid
from django.core import validators
from django.utils import timezone
import datetime
from dateutil.relativedelta import relativedelta
from Client.models import Clients

    
class Eses(models.Model):

    STATUT = [
        ("ACTIF", "ACTIF"),
        ("ALERTE ABONNEMENT", "ALERTE ABONNEMENT"),
    ]

    id_ese                  = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)  # A AMELIORER
    nom_ese                 = models.CharField("Nom Entreprise", max_length=100, blank=False)
    adresse_ese             = models.CharField("Adresse Entreprise", max_length=255, blank=True)
    abrev_ese               = models.CharField("Sigle Entreprise", max_length=100, blank=False)
    domaine_ese             = models.CharField("Nom domaine Entreprise", max_length=255, unique=True)
    description_ese         = models.TextField("Descriptif Entreprise", null=True, blank=True, default="Faire une description")
    schema_name             = models.CharField("Nom location BD", max_length=255, blank=False)
    slogan_ese              = models.CharField("Slogan Entreprise", max_length=255, blank=True)
    datecreat_ese           = models.DateField("Date création", default=timezone.now, blank=False) 
    siege_ese               = models.CharField("Siège Entreprise", max_length=100, blank=True)
    pays_ese                = models.CharField("Pays Entreprise", max_length=255, blank=True)
    email_ese               = models.EmailField("Email Entreprise", max_length=100, blank=True, validators=[validators.EmailValidator(message="Email invalide")],)
    user_admin_ese          = models.EmailField("Nom admin Entreprise", max_length=100, blank=False, default="admin@admin.com",  validators=[validators.EmailValidator(message="Email invalide")],)
    mdp_admin_ese           = models.CharField("Mot de passe admin", max_length=255, default="admin")
    siteweb_ese             = models.CharField("SIte web Entreprise", max_length=100, blank=True)
    phone1_ese              = models.CharField("Téléphone 1 entreprise", blank=True)
    phone2_ese              = models.CharField("Téléphone 2 entreprise", blank=True)
    logo_ese                = models.ImageField("Logo Entreprise", null=True, blank=True, default="logo.jpeg")
    num_contrib_ese         = models.CharField("N° contribuable Entreprise", max_length=255, blank=True)
    statut_ese              = models.CharField("Statut Entreprise", max_length=255, choices=STATUT, default="ACTIF")
    
    

    
    class Meta:
        verbose_name = 'Entreprise'
        verbose_name_plural = 'Entreprises'
    

    def __str__(self):
        return "{} ({})".format(self.nom_ese, self.abrev_ese)




class AbonnementEse(models.Model):
    ese                         = models.ForeignKey(Clients, on_delete=models.SET_NULL, null=True, related_name="ese_ese")
    num_abon                    = models.CharField(max_length=15)
    code                        = models.CharField("Code Entreprise", max_length=128, unique=True, blank=True, null=True)
    schema_name                 = models.CharField(max_length=255, unique=True, default="rien")     
    date_saisie                 = models.DateField(auto_now_add=True)
    date_debut                  = models.DateField()
    mensualite                  = models.PositiveIntegerField()
    date_fin                    = models.DateField()
    nbre_man                    = models.PositiveIntegerField("Nbre manutention", default=0)
    nbre_vl                     = models.PositiveIntegerField("Nbre Véhicule Léger", default=0)
    nbre_pl1                    = models.PositiveIntegerField("Nbre Poids Lourd 1", default=0)
    nbre_pl2                    = models.PositiveIntegerField("Nbre Poids Lourd 2", default=0)
    nbre_autobus                = models.PositiveIntegerField("Nbre Autobus", default=0)
    nbre_gc                     = models.PositiveIntegerField("Nbre Engin Génie civil", default=0)
    prcent_remise               = models.FloatField()
    nusers_dg                   = models.PositiveIntegerField("Direction Générale", default=0)
    nusers_dop                  = models.PositiveIntegerField("Département Opérations", default=0)
    nusers_dex                  = models.PositiveIntegerField("Département Exploitation", default=0)
    nusers_srm                  = models.PositiveIntegerField("Service Maintenance", default=0)
    nusers_reg                  = models.PositiveIntegerField("Région", default=0)
    nusers_age                  = models.PositiveIntegerField("Agence", default=0)
    nusers_ctq                  = models.PositiveIntegerField("Centre Technique", default=0)
    nusers_util                 = models.PositiveIntegerField("Utilisateur", default=0)
    nusers_gar                  = models.PositiveIntegerField("Garage", default=0)
    nusers_mag                  = models.PositiveIntegerField("Magasinier", default=0)  
    montant_verse               = models.PositiveIntegerField()
    date_next_versement         = models.DateField()
    is_active                   = models.BooleanField(default=True)
    nbre_users                  = models.PositiveIntegerField(default=0)
    nbre_engins                 = models.PositiveIntegerField(default=0)
    montant_engins              = models.PositiveIntegerField(default=0)
    montant_users               = models.PositiveIntegerField(default=0)
    montant_ht                  = models.PositiveIntegerField(default=0)
    montant_taxe                = models.PositiveIntegerField(default=0)
    montant_ttc                 = models.PositiveIntegerField(default=0)
    montant_restant             = models.PositiveIntegerField(default=0)
    is_active                   = models.BooleanField(default=True)

    @property
    def is_valid(self):
        return self.is_active and self.date_fin > datetime.date.today()
    
    def __str__(self):
        return f"{self.num_abonne} - {self.is_active} - {self.date_fin}"



class Newsubscribe(models.Model):
    code_ab = models.CharField(max_length=255)




class ValidationElement(models.Model):
    nom_ese = models.CharField(max_length=255, null=False, blank=False)
    code_ese = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return self.nom_ese


class Organigramme(models.Model):
    direction_gen = models.CharField(max_length=255, null=True, blank=False)
    direction_fonct = models.CharField(max_length=255, null=True, blank=True)
    service = models.CharField(max_length=255, null=True, blank=True)
    agence = models.CharField(max_length=255, null=True, blank=True)
    site = models.CharField(max_length=255, null=True, blank=True)
    sous_site = models.CharField(max_length=255, null=True, blank=True)
    organigramme = models.CharField(max_length=255)

    def __str__(self):
        return self.organigramme



# Base de donnée des Prestations

class Prestations(models.Model):
    code_prest = models.CharField(max_length=255, null=True, blank=True)
    libelle_prest = models.CharField(max_length=255)
    organe = models.CharField(max_length=255, null=True, blank=True)  
    duree_prest = models.IntegerField(default=0)
    montant_prest = models.IntegerField(default=0)


    def __str__(self):
        return f"{self.libelle_prest} - {self.organe} - {self.duree_prest}"
    
# Base de donnée des PR

class PieceRechange(models.Model):
    code_pr = models.CharField(max_length=255, null=True, blank=True)
    libelle_pr  = models.CharField(max_length=255, null=True, blank=True)
    prix_pr  = models.IntegerField(default=0)
    ref_usine = models.CharField(max_length=255, null=True, blank=True)
    cat_pr = models.CharField(max_length=255, null=True, blank=True)
    

    def __str__(self):
        return f"{self.libelle_art} - {self.cat_art} - {self.ref_usine} - {self.prix_art}"
    

# class PieceRechange(models.Model):

#     TYPE_PRS = [
#         ("Neuve", "Neuve"),
#         ("Occasion", "Occasion"),
#         ("Recuperation", "Recuperation"),
#         ("Permutation", "Permutation"),
#     ]


#     code_pr = models.CharField(max_length=255, null=True, blank=True)
#     libelle_pr  = models.CharField(max_length=255, null=True, blank=True)
#     quantite_pr = models.PositiveIntegerField()
#     type_pr = models.CharField(max_length=25, choices=TYPE_PRS, default="Neuve")
#     prix_pr  = models.PositiveIntegerField()
#     ref_usine = models.CharField(max_length=255, null=True, blank=True)
#     cat_pr = models.CharField(max_length=255, null=True, blank=True)
#     demand_ep = models.ForeignKey(DemandEp, on_delete=models.SET_NULL, related_name="prech_ep", blank=True)
#     # demand_curatif =models.ForeignKey(DemandCuratif, on_delete=models.SET_NULL, related_name="prech_curatif", blank=True)



# class Prestations(models.Model):
#     code_prest = models.CharField(max_length=255, null=True, blank=True)
#     libelle_prest = models.CharField(max_length=255)
#     organe = models.CharField(max_length=255, null=True, blank=True)  
#     duree_prest = models.IntegerField()
#     montant_prest = models.IntegerField()


#     def __str__(self):
#         return f"{self.libelle_prest} - {self.organe} - {self.duree_prest}"