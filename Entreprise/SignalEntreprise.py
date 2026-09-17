from django.db.models.signals import post_save, pre_save
from django.shortcuts import get_object_or_404
from django.dispatch import receiver
from django_tenants.utils import tenant_context,schema_context
from Entreprise.models import Organigramme, Eses
from Entreprise.SerializerEses import OrganigramSerializer, PrestationSerializer, PieceRechangeSerializer
from MgpaUsers.models import UserAccount
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from Parameters.models import ParamComptAlert
from Parameters.paramserializer import ParamComptAlertSerializer
import pandas as pd
import os
from .models import AbonnementEse
from Client.models import Clients
from .SerializerEses import AbonnementSerializer
from django.conf import settings
import datetime





@receiver(post_save, sender=AbonnementEse)
def CreateEses(sender, instance, created, **kwargs):
    if created: 
        
        # erese = get_object_or_404(Clients, code=instance.code_ese)
        if instance.is_valid == True: 
            clese = Clients.objects.filter(id_enreg=instance.ese.id_enreg).first()       
            clese.ese_activate = True
            clese.save()
    
        # else:
        #     clese.ese_activate = False
        #     clese.save()

        # check_abonnement.delay(instance)


@receiver(post_save, sender=Eses)
def CreateEses(sender, instance, created, **kwargs):
    if created:

        ese = Eses.objects.filter(schema_name=instance.schema_name).first()

        with tenant_context(ese):
            path_prest = os.path.join(settings.MEDIA_ROOT, "fichiers/Prestations.xlsx") 
            path_prech =  os.path.join(settings.MEDIA_ROOT, "fichiers/Pieces_Rechanges.xlsx")
            

            df_prest = pd.read_excel(path_prest, sheet_name=0)
            for k in range(len(df_prest)):
                prest = {}
                prest['code_prest'] = str(df_prest.iloc[k, 0]).upper()
                prest['organe'] = str(df_prest.iloc[k, 1]).upper()
                prest['libelle_prest'] = str(df_prest.iloc[k, 2]).upper()
                prest['duree_prest'] = str(df_prest.iloc[k, 3]).upper()
                prest['montant_prest'] = str(df_prest.iloc[k, 4]).upper()

                serializer_prest = PrestationSerializer(data = prest)
                serializer_prest.is_valid(raise_exception=True)
                serializer_prest.save()


            df_prech = pd.read_excel(path_prech, sheet_name=0)
            for k in range(len(df_prech)):
                prech = {}
                prech['code_pr'] = str(df_prech.iloc[k, 0]).upper()
                prech['libelle_pr'] = str(df_prech.iloc[k, 1]).upper()
                prech['cat_pr'] = str(df_prech.iloc[k, 2]).upper()
                prech['ref_usine'] = str(df_prech.iloc[k, 3]).upper()
                prech['prix_pr'] = str(df_prech.iloc[k, 4]).upper()

                serializer_prech = PieceRechangeSerializer(data = prech)
                serializer_prech.is_valid(raise_exception=True)
                serializer_prech.save()



            data_org = {}
            data_org['direction_gen'] = 'DG'
            data_org['direction_fonct'] = ""
            data_org['service'] = ""
            data_org['agence'] = ""
            data_org['site'] = ""
            data_org['sous_site'] = ""
            pos = ese.abrev_ese
            pos += "".join("_")
            pos += "".join("DG")
            data_org['organigramme'] = pos.replace(" ", "-").strip()
            orgserializer = OrganigramSerializer(data=data_org)
            orgserializer.is_valid(raise_exception=True)
            orgserializer.save()
        
            User = get_user_model()

            User.objects.create_superuser(
                email=instance.user_admin_ese,
                password=instance.mdp_admin_ese,
                username="admin",
                last_name="Admin",
                first_name="",
                genre="",
                matricule="",
                mobile="",
                type="MASTER_DATA",
                poste="Administrateur",
                site = Organigramme.objects.filter(organigramme="DG").first(), 
                date_nais = "2026-01-01", 
                matrimonial = "",
                address = "",
                avatar = "", 
                permis = "", 
                num_cni = "",  
                document = "",          

            )


            try:

                data_ese = {}
                data_ese['nom_ese'] = instance.nom_ese
                data_ese['abrev_ese'] = instance.abrev_ese
                data_ese['slogan_ese'] = instance.slogan_ese
                data_ese['abrev_ese']   = instance.abrev_ese
                data_ese["siege_ese"] = instance.siege_ese
                data_ese["pays_ese"] = instance.pays_ese
                data_ese['phone1_ese']  = instance.phone1_ese
                data_ese['email_ese']  = instance.email_ese
                data_ese['email']  = instance.user_admin_ese
                data_ese['password']  = instance.mdp_admin_ese
                data_ese['access']  = "Master Data"
                data_ese['full_name']  = ""

                

                text_html = render_to_string("user_mail_notif.html", data_ese)
                msg = EmailMessage(
                "Création de compte d'utilisateur",
                text_html,
                "SORETAC <duparce.netzone@gmail.com>",
                [instance.user_admin_ese]
                )
                msg.content_subtype = "html"
                msg.send()
                

            except Exception as e:
                print("Erreur de connexion internet")
    
        










# @receiver(post_save, sender=NiveauOrganisation)
# def CreateOrganigramme(sender, instance, created, **kwargs):
#     if created:
        
#         niveau_orgs = NiveauOrganisation.objects.all()
#         liste_niv = []
#         for niveau_org in niveau_orgs:
#             if niveau_org.niveau != 0:
#                 liste_niv.append(niveau_org.niveau)           
#         liste_niv = list(set(liste_niv))
#         liste_niv.sort()
        
#         pos = ""
#         liste_org = []
#         for m in range(len(liste_niv)):
#             nivorgs = NiveauOrganisation.objects.filter(niveau=liste_niv[m])
#             liste = []
#             for nivorg in nivorgs:
#                 tup = (nivorg.niveau, nivorg.nom)
#                 liste.append(tup)
                
#             liste_org.append(liste)

#         for ind, tups in enumerate(liste_org[0]):
#             pos += "".join(tups[1])
#             for n in range(1, len(liste_org)):
#                 for nind, ntups in enumerate(liste_org[n]):            
#                     pos += "_".join(ntups[1])




        
