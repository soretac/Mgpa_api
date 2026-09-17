from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from Client.models import Clients, Domain, AbonneClient
from Client.ClientSerializers import AbonneClientSerializer
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, BadHeaderError, send_mail
from django_tenants.utils import tenant_context,schema_context
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from templated_mail.mail import BaseEmailMessage
from datetime import datetime




@receiver(post_save, sender=Clients)
def CreateTenant(sender, instance, created, **kwargs):
    if not created:
        dom = Domain.objects.filter(tenant_id = instance.id_enreg).first()
        dom.domain = instance.nom_domaine + ".localhost"
        dom.save()

    else: 
        domain = Domain()
        domaine = instance.nom_domaine + ".localhost"   # LE SOUS DOMAINE DE L'ENTREPRISE #
        domain.domain = domaine
        domain.tenant = instance     # domain.tenant = client
        domain.is_primary = True
        domain.save()


    context={
        'nom_ese': instance.nom_ese,
        'adresse_ese': instance.adresse,
        'abrev_ese'  : instance.schema_sigle,
        "schema_name": instance.schema_name,
        "domaine_ese": instance.nom_domaine,
        'slogan_ese' : instance.slogan,
        'date_enreg': instance.created_on,
        'siege_ese'  : instance.ville_siege,
        'pays_ese'   : instance.pays,
        'email_ese'  : instance.email,
        'siteweb_ese': instance.siteweb,
        'user_admin_ese': instance.user_admin,
        'mdp_admin_ese': instance.mdp_admin,
        'description_ese' : instance.description_ese,
        'logo_ese'   : instance.logo_ese,
        'phone1_ese' : instance.phone1,
        'phone2_ese' : instance.phone2,
        'num_contrib_ese': instance.niu_ese,
         
    }

    try:
        text_html = render_to_string("Client/creationEse.html", context)
        msg = EmailMessage(
        "INSCRIPTION D'ENTREPRISE",
        text_html,
        "SORETAC <duparce.netzone@gmail.com>",
        [instance.email]
        )
        msg.content_subtype = "html"
        msg.send()

    except Exception as e:
        print("Erreur de connexion internet")



@receiver(post_save, sender=AbonneClient)
def CreateTenant(sender, instance, created, **kwargs):
    if created:

        eses = Clients.objects.filter(id_enreg=instance.ese_id).first()
        serializers = AbonneClientSerializer(instance)
        serialized_data = serializers.data

        context1={
            'nom_ese': eses.nom_ese,
            'date_saisie' : instance.date_saisie,             
            'date_debut' : instance.date_debut,                  
            'mensualite' :instance.mensualite,                   
            'date_fin' : instance.date_fin,    
            'code' : instance.code,            
            'nbre_man' : instance.nbre_man,                  
            'nbre_vl' : instance.nbre_vl,                     
            'nbre_pl1' :instance.nbre_pl1,                     
            'nbre_pl2' : instance.nbre_pl2,                    
            'nbre_autobus' : instance.nbre_autobus,               
            'nbre_gc' : instance.nbre_gc,                     
            'prcent_remise' :instance.prcent_remise,               
            'nusers_dg' :  instance.nusers_dg,                  
            'nusers_dop' : instance.nusers_dop,                 
            'nusers_dex' : instance.nusers_dex,                  
            'nusers_srm' : instance.nusers_srm,                  
            'nusers_reg' : instance.nusers_reg,                  
            'nusers_age' : instance.nusers_age,                  
            'nusers_ctq' : instance.nusers_ctq,                  
            'nusers_util' :instance.nusers_util,                  
            'nusers_gar' : instance.nusers_gar,                 
            'nusers_mag' : instance.nusers_mag,
            'nbre_users' : instance.nbre_users,
            'nbre_engins' : instance.nbre_engins,                                 
            'montant_engins' : serialized_data["montant_engins"],
            'montant_users' : serialized_data["montant_users"],
            'montant_ht' : serialized_data["montant_ht"],
            'montant_taxe' : serialized_data["montant_taxe"],
            'montant_ttc' : serialized_data["montant_ttc"],
            'montant_verse' : instance.montant_verse, 
            'montant_restant' : serialized_data["montant_restant"],            
            'is_active' :instance.is_active, 
        
        }

        try:
            text_html = render_to_string("Client/creationEse.html", context1)
            msg = EmailMessage(
            "CREATION D'ABONNEMENT ENTREPRISE",
            text_html,
            "SORETAC <duparce.netzone@gmail.com>",
            [instance.email]
            )
            msg.content_subtype = "html"
            msg.send()

        except Exception as e:
            print("Erreur de connexion internet")


        
        # AbonneClientSerializer.save(
        #     ese=instance.id_enreg,
        #     code_ab = str(instance.code),
        #     start_date = datetime.strptime(str(instance.created_on), "%Y-%m-%d").date(),
        #     periode_ab = int(instance.periode),
        #     nbre_users = int(instance.nbre_users),
        #     nbre_engin = int(instance.nbre_engin),
        # )

        # try:
        #     message = BaseEmailMessage(
        #         template_name="Client/creationEse.html",
        #         context={
        #             'nom_ese': instance.nom_ese,
        #             'code_ese': instance.code,
        #             'adresse_ese': instance.adresse,
        #             'abrev_ese'  : instance.schema_sigle,
        #             "schema_name": instance.schema_name,
        #             "domaine_ese": instance.nom_domaine,
        #             'slogan_ese' : instance.slogan,
        #             'date_enreg': instance.created_on,
        #             'periode': instance.periode,
        #             'siege_ese'  : instance.ville_siege,
        #             'pays_ese'   : instance.pays,
        #             'email_ese'  : instance.email,
        #             'siteweb_ese': instance.siteweb,
        #             'user_admin_ese': instance.user_admin,
        #             'mdp_admin_ese': instance.mdp_admin,
        #             'description_ese' : instance.description_ese,
        #             'logo_ese'   : instance.logo_ese,
        #             'phone1_ese' : instance.phone1,
        #             'phone2_ese' : instance.phone2,
        #             'num_contrib_ese': instance.niu_ese,
        #             'mont_dossier' : instance.mont_dossier,
        #             'nbre_users' : instance.nbre_users,
        #             'nbre_engin' : instance.nbre_engin,                                     
        #             'mont_check' : instance.mont_check,
                
        #         }
        #     )
        #     message.send([instance.email])
        
        # except BadHeaderError:
        #     pass



        # try:
        #     text_html = render_to_string("Client/creationEse.html", context)
        #     msg = EmailMessage(
        #     "CREATION DE COMPTE ENTREPRISE",
        #     text_html,
        #     "SORETAC <socamaryde@gmail.com>",
        #     [instance.email]
        #     )
        #     msg.content_subtype = "html"
        #     msg.send()

        # except Exception as e:
        #     print("Erreur de connexion internet")




        # try:
        #     message = BaseEmailMessage(
        #         template_name='Client/creationEse.html',
        #         context={
        #             'nom_ese': instance.nom_ese,
        #             'code_ese': instance.code,
        #             'adresse_ese': instance.adresse,
        #             'abrev_ese'  : instance.schema_sigle,
        #             "schema_name": instance.schema_name,
        #             "domaine_ese": instance.nom_domaine,
        #             'slogan_ese' : instance.slogan,
        #             'date_enreg': instance.created_on,
        #             'periode': instance.periode,
        #             'siege_ese'  : instance.ville_siege,
        #             'pays_ese'   : instance.pays,
        #             'email_ese'  : instance.email,
        #             'siteweb_ese': instance.siteweb,
        #             'user_admin_ese': instance.user_admin,
        #             'mdp_admin_ese': instance.mdp_admin,
        #             'description_ese' : instance.description_ese,
        #             'logo_ese'   : instance.logo_ese,
        #             'phone1_ese' : instance.phone1,
        #             'phone2_ese' : instance.phone2,
        #             'num_contrib_ese': instance.niu_ese,
        #             'mont_dossier' : instance.mont_dossier,
        #             'nbre_users' : instance.nbre_users,
        #             'nbre_engin' : instance.nbre_engin,                                     
        #             'mont_check' : instance.mont_check,
                
        #         }
        #     )
        # #     # message.attach_file('')
        #     message.send(['instance.email'])

        # except BadHeaderError:
        #     pass

        # try:
        #     data_ese = {}
        #     data_ese['nom_ese'] = instance.nom_ese
        #     data_ese['code_ese'] = instance.code
        #     data_ese['adresse_ese'] = instance.adresse
        #     data_ese['abrev_ese']   = instance.schema_sigle
        #     data_ese["schema_name"] = instance.schema_name
        #     data_ese["domaine_ese"] = instance.nom_domaine
        #     data_ese['slogan_ese']  = instance.slogan
        #     data_ese['date_enreg'] = instance.created_on
        #     data_ese['datexp_ese']  = instance.datexpiration
        #     data_ese['period_validation'] = instance.period_validation
        #     data_ese['siege_ese']   = instance.ville_siege
        #     data_ese['pays_ese']    = instance.pays
        #     data_ese['email_ese']   = instance.email
        #     data_ese['siteweb_ese'] = instance.siteweb
        #     data_ese['user_admin_ese'] = instance.user_admin
        #     data_ese['mdp_admin_ese'] = instance.mdp_admin
        #     data_ese['description_ese']  = instance.description_ese
        #     data_ese['logo_ese']    = instance.logo_ese
        #     data_ese['phone1_ese']  = instance.phone1
        #     data_ese['phone2_ese']  = instance.phone2
        #     data_ese['num_contrib_ese'] = instance.niu_ese
        #     data_ese['nbre_users']  = instance.nbre_licence
        #     data_ese['nbre_engin']  = instance.nbre_engin                   
        #     data_ese['mont_dossier']  = instance.mont_dossier
        #     data_ese['mont_check']  = instance.checking_parc
        #     data_ese['montant_engin']  = instance.nbre_engin * instance.period_validation * 2000
        #     data_ese['montant_licence']  = instance.nbre_licence * instance.period_validation * 5000
        #     data_ese['montant_total']  = instance.nbre_engin * instance.period_validation * 2000 + instance.nbre_licence * instance.period_validation * 5000 + instance.checking_parc + instance.mont_dossier



        


        #     text_html = render_to_string("creationEse.html", data_ese)
        #     msg = EmailMessage(
        #     "CREATION DE COMPTE ENTREPRISE",
        #     text_html,
        #     "SORETAC <duparce.netzone@gmail.com>",
        #     [instance.email]
        #     )
        #     msg.content_subtype = "html"
        #     msg.send()

        # except Exception as e:
        #     print("Erreur de connexion internet")
    
