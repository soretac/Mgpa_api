from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from MatRoulant.models import VehiculesEses
from CompteurApps.models import Compteurs, AlerteEp
from .SerializerPrevent import SuiviEpSerializer
from PreventApps.models import Eps, SuiviEp
from django.db.models import Q



@receiver(post_save, sender=AlerteEp)
def createSuiviEp(sender, instance, created, **kwargs):

    if created:
        list_250h = ["MN", "GC"]
        list_5000km = ["VL", "VT"]
        list_150h = ["PL1"]
        list_200h = ["PL2"]
        compt = Compteurs.objects.filter(vehicule_id=instance.vehicule_id).last()

        try:
            anc_suivi = SuiviEp.objects.filter(Q(session_alerte=instance.session_alert) & ~Q(statut_ep="EFFECTUE")).first()

            anc_suivi.prochain_ep = instance.alerte
            anc_suivi.type_alert = instance.type_alert
            anc_suivi.ecart = instance.ecart
            anc_suivi.compt_act = instance.compt
            anc_suivi.save()

            
        except:

            try:
                ep = Eps.objects.filter(Q(vehicule_id=instance.vehicule_id) & Q(etat_ep="EFFECTUE")).last()
                last_ep = ep.type_ep
                last_date = ep.date_ep
                last_compt = ep.compt
                categ = instance.vehicule.categorie
                if categ in list_150h:
                    compt_cible = last_compt + 150
                elif categ in list_250h:
                    compt_cible = last_compt + 250
                elif categ in list_5000km:
                    compt_cible = last_compt + 5000
                elif categ in list_200h:
                    compt_cible = last_compt + 200

                

            except:
                
                categ = instance.vehicule.categorie
                if categ in list_150h:
                    last_ep = "150 H"
                    last_compt = compt.start_compt
                    last_date = None
                    compt_cible = last_compt + 150

                elif categ in list_250h:
                    last_ep = "250 H"
                    last_compt = compt.start_compt
                    last_date = None
                    compt_cible = last_compt + 250

                elif categ in list_5000km:
                    last_ep = "5000 KM"
                    last_compt = compt.start_compt
                    last_date = ''
                    compt_cible = last_compt + 5000

                elif categ in list_200h:
                    last_ep = "200 H"
                    last_compt = compt.start_compt
                    last_date = None
                    compt_cible = last_compt + 200
            

                    

            data_ep = {}
            data_ep['vehicule'] = instance.vehicule_id
            data_ep['statut_ep'] = instance.statut
            # data_ep['site_fonct'] = instance.site_fonct_id
            data_ep['dernier_ep'] = last_ep
            data_ep['comptlast_ep'] = last_compt
            data_ep['datelast_ep'] = last_date
            data_ep['compt_act'] = instance.compt
            data_ep['compt_cible'] = compt_cible
            data_ep['ecart'] = instance.ecart
            data_ep['type_alert'] = instance.type_alert
            data_ep['prochain_ep'] = instance.alerte
            data_ep['statut_dt'] = ''
            data_ep['site_matrlt'] = instance.chef_smrlt_id
            data_ep['session_alerte'] = instance.session_alert

            serializer = SuiviEpSerializer(data=data_ep)
            serializer.is_valid(raise_exception=True)
            serializer.save()



        