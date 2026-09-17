from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from MatRoulant.models import VehiculesEses
from CompteurApps.models import Compteurs, AlerteEp, CptAlert, CountCritique
from Parameters.models import ParamComptAlert
from CompteurApps.SerializerComptApps import AlerteEpSerializer, CptAlertSerializer, CountCritiqSerializer
from PreventApps.models import SuiviEp
from django.contrib.auth import get_user_model
from Mgpa_api.middleware import get_tenant
from decimal import Decimal
from crum import get_current_request
from django.db.models import Q
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist
from Client.pwd_generator import SessionGenerator


User = get_user_model()

# <div>


@receiver(post_save, sender=Compteurs)
def AlertEpCreate(sender, instance, created, **kwargs):
    
    if created:
        list_250h = ["MN", "GC"]
        list_5000km = ["VL", "VT"]
        list_150h = ["PL1"]
        list_200h = ["PL2"]
        EP_MN_GC = ['250 H', '500 H', '750 H', '1000 H', '1250 H', '1500 H', '1750 H', '2000 H']
        EP_VL_VT = ['5000 KM', '10000 KM', '15000 KM', '20000 KM', '25000 KM', '30000 KM']
        EP_PL1 = ['150 H', '300 H', '450 H', '600 H', '750 H', '900 H', '1050 H', '1200 H']
        EP_PL2 = ['10000 KM', '20000 KM', '30000 KM', '40000 KM', '50000 KM', '60000 KM']
        cat = instance.vehicule.categorie
        ese = str(instance.vehicule.identite).lower().split('_')[0]
        
        alt = ParamComptAlert.objects.filter(schema_name=ese, vehicule=instance.vehicule.immat).first().alert
        
        list_dest = ["DIR_EXPLOIT", "MASTER_DATA", "DIR_GEN"]

        dest_alert =[user for user in User.objects.filter(Q(type__in=list_dest))]
        veh = VehiculesEses.objects.filter(id=instance.vehicule_id).first()

        user_matrlt = User.objects.filter(Q(site=veh.site_matrlt) & Q(type="CHEF_SMRLT")).first()
        user_region = User.objects.filter(Q(type="CHEF_REGION") & Q(site__organigramme=veh.affectation)).first()
        user_agence = User.objects.filter(Q(type="CHEF_AGENCE") & Q(site__organigramme=veh.affectation)).first()
        user_ctech = User.objects.filter(Q(type="CHEF_CTECH") & Q(site__organigramme=veh.affectation)).first()
        user_site = User.objects.filter(Q(type="CHEF_SITE") & Q(site__organigramme=veh.affectation)).first()
        user_dirop = User.objects.filter(Q(type="DIR_OPER") & Q(site__organigramme=veh.affectation)).first()
        user_garage = User.objects.filter(Q(site=veh.site_matrlt) & Q(type="CHEF GARAGE")).first()

        for dest in [user_matrlt, user_region, user_agence, user_ctech, user_site, user_dirop]:
            if dest != None:
                dest_alert.append(dest)
        conds = veh.conducteurs.prefetch_related().all()               # TOUS LES DIFFERENTS CONDUCTEURS DU VEHICULES
        for cond in conds:
            dest_alert.append(cond)

        # ALERTES DES ENGINS DE MANUTENTION

        if cat in list_250h:

            if alt <= instance.ecart <= 250.0:
                data_alert = {}
                # SI LA DERNIERE ALERTE EST DANS LA PHASE "A VIDANGER"

                last_enrg = AlerteEp.objects.filter(Q(vehicule=instance.vehicule)).last()
                if last_enrg != None:
                    anc_ep = last_enrg.alerte                   

                    if last_enrg.statut == "EFFECTUEE":            # SI LA VIDANGE A ETE FAITE
                        i = int(EP_MN_GC.index(anc_ep)) + 9

                        data_alert['compt'] = instance.compt_act
                        data_alert['alerte'] = EP_MN_GC[i % 8]
                        data_alert['type_alert'] = "A VIDANGER"
                        data_alert["ecart"] = instance.ecart
        
                        data_alert['message'] = "Alerte pour Entretien Préventif : La " + str(data_alert['alerte']) + " doit être effectuée bientôt dans moins de "+ str(250.0-instance.ecart) + " heures de fonctionnement"
                        data_alert['vehicule'] = instance.vehicule_id
                        
                        data_alert['chef_smrlt'] = user_matrlt.id
                        data_alert["nbalert"] = 1
                        data_alert['session_alert'] = SessionGenerator()

                        serializer = AlerteEpSerializer(data=data_alert)
                        serializer.is_valid(raise_exception=True)
                        alert = serializer.save()
                        alert.destinataires.add(*dest_alert) 

                    else:            # SI LA VIDANGE  N'A PAS ETE FAITE
                        
                        data_alert['compt'] = instance.compt_act
                        data_alert['alerte'] = last_enrg.alerte
                        data_alert['type_alert'] = "A VIDANGER"
        
                        data_alert['message'] = "Alerte pour Entretien Préventif : La " + str(last_enrg.alerte) + " doit être effectuée bientôt dans moins de "+ str(250.0-instance.ecart) + " heures de fonctionnement"
                        data_alert['vehicule'] = instance.vehicule_id
                        
                        data_alert['chef_smrlt'] = user_matrlt.id
                        data_alert['session_alert'] = last_enrg.session_alert
                        data_alert["ecart"] = instance.ecart
                        data_alert["nbalert"] = last_enrg.nbalert + 1

                        serializer = AlerteEpSerializer(data=data_alert)
                        serializer.is_valid(raise_exception=True)
                        alert = serializer.save()
                        alert.destinataires.add(*dest_alert) 



                # S'IL N'YA PAS D'ALERTE DANS CET INTERVALLE
                else:
                    
                    data_alert['compt'] = instance.compt_act
                    data_alert['alerte'] = "250 H"
                    data_alert['type_alert'] = "A VIDANGER"
                    data_alert['message'] = "Alerte pour Entretien Préventif : La " + str(data_alert['alerte']) + " doit être effectuée bientôt dans moins de "+ str(250.0-instance.ecart) + " heures de fonctionnement"
                    data_alert['vehicule'] = instance.vehicule_id
                    
                    data_alert['chef_smrlt'] = user_matrlt.id
                    data_alert["ecart"] = instance.ecart
                    data_alert["nbalert"] = 1
                    data_alert['session_alert'] = SessionGenerator()
                    serializer = AlerteEpSerializer(data=data_alert)
                    serializer.is_valid(raise_exception=True)
                    alert = serializer.save()
                    alert.destinataires.add(*dest_alert)
                    

            # POUR LES DEPASSEMENTS DES ENGIN DE MANUTENTION
            if 250.0 < instance.ecart <= 275.0:
                data_alert = {}

                last_enrg = AlerteEp.objects.filter(Q(vehicule=instance.vehicule)).last()
                if last_enrg != None:
                    anc_ep = last_enrg.alerte 

                    if last_enrg.statut != "EFFECTUEE":
                        if last_enrg.type_alert == "A VIDANGER":
                            # i = int(EP_MN_GC.index(anc_ep)) + 9
                            i = int(EP_MN_GC.index(anc_ep))

                            data_alert['compt'] = instance.compt_act
                            data_alert['alerte'] = EP_MN_GC[i % 8]
                            data_alert['type_alert'] = "EN DEPASSEMENT"
                            data_alert['ecart'] = instance.ecart
                            data_alert['message'] = "Compteur pour vidange En dépassement de "+ str(instance.ecart-250.0) + " heure(s). l'EP "+ str(data_alert['alerte']) + " doit être effectué immédiatement "
                            data_alert['vehicule'] = instance.vehicule_id
                            data_alert['chef_smrlt'] = user_matrlt.id
                            data_alert["nbalert"] = last_enrg.nbalert + 1
                            data_alert['session_alert'] = last_enrg.session_alert

                            serializer = AlerteEpSerializer(data=data_alert)
                            serializer.is_valid(raise_exception=True)
                            alert = serializer.save()
                            alert.destinataires.add(*dest_alert) 

                            counts = {}
                            counts["vehicule"]=instance.vehicule_id
                            counts["n_depassement"]= 1
                            counts["n_danger"]=0
                            counts["n_critique"]=0
                            counts["ecart"]=instance.ecart 
                            counts["type_ep"]=EP_MN_GC[i % 8] 
                            counts["session"] = last_enrg.session_alert
                            serializercount = CountCritiqSerializer(data=counts)                  
                            serializercount.is_valid(raise_exception=True)
                            serializercount.save()
                        
                        elif last_enrg.type_alert == "EN DEPASSEMENT":
                            
                            data_alert['compt'] = instance.compt_act
                            data_alert['alerte'] = last_enrg.alerte
                            data_alert['type_alert'] = "EN DEPASSEMENT"
                            data_alert['ecart'] = instance.ecart
                            data_alert['message'] = "Compteur pour vidange En dépassement de "+ str(instance.ecart-250.0) + " heure(s). l'EP "+ str(data_alert['alerte']) + " doit être effectué immédiatement "
                            data_alert['vehicule'] = instance.vehicule_id
                            data_alert['chef_smrlt'] = user_matrlt.id
                            data_alert["nbalert"] = last_enrg.nbalert + 1
                            data_alert['session_alert'] = last_enrg.session_alert

                            serializer = AlerteEpSerializer(data=data_alert)
                            serializer.is_valid(raise_exception=True)
                            alert = serializer.save()
                            alert.destinataires.add(*dest_alert)


                            counts = {}
                            counts["vehicule"]=instance.vehicule_id
                            counts["n_depassement"]= 1
                            counts["n_danger"]=0
                            counts["n_critique"]=0
                            counts["ecart"]=instance.ecart
                            counts["type_ep"]=last_enrg.alerte
                            counts["session"] = last_enrg.session_alert
                            serializercount = CountCritiqSerializer(data=counts)                  
                            serializercount.is_valid(raise_exception=True)
                            serializercount.save()

                    else:
                        i = int(EP_MN_GC.index(anc_ep))

                        data_alert['compt'] = instance.compt_act
                        data_alert['alerte'] = EP_MN_GC[i % 8]
                        data_alert['type_alert'] = "EN DEPASSEMENT"
                        data_alert['ecart'] = instance.ecart
                        data_alert['message'] = "Compteur pour vidange En dépassement de "+ str(instance.ecart-250.0) + " heure(s). l'EP "+ str(data_alert['alerte']) + " doit être effectué immédiatement "
                        data_alert['vehicule'] = instance.vehicule_id
                        data_alert['chef_smrlt'] = user_matrlt.id
                        data_alert["nbalert"] = 1
                        sess = SessionGenerator()
                        data_alert['session_alert'] = sess

                        serializer = AlerteEpSerializer(data=data_alert)
                        serializer.is_valid(raise_exception=True)
                        alert = serializer.save()
                        alert.destinataires.add(*dest_alert) 

                        counts = {}
                        counts["vehicule"]=instance.vehicule_id
                        counts["n_depassement"]= 1
                        counts["n_danger"]=0
                        counts["n_critique"]=0
                        counts["ecart"]=instance.ecart
                        counts["type_ep"]=EP_MN_GC[i % 8]
                        counts["session"] = sess
                        serializercount = CountCritiqSerializer(data=counts)                  
                        serializercount.is_valid(raise_exception=True)
                        serializercount.save()

                else:
                    data_alert['compt'] = instance.compt_act
                    data_alert['alerte'] = "250 H"
                    data_alert['type_alert'] = "EN DEPASSEMENT"
                    data_alert['message'] = "Compteur pour vidange En dépassement de "+ str(instance.ecart-250.0) + " heure(s). l'EP "+ str(data_alert['alerte']) + " doit être effectué immédiatement "
                    data_alert['vehicule'] = instance.vehicule_id
                    data_alert['chef_smrlt'] = user_matrlt.id
                    data_alert["nbalert"] = 1
                    sess = SessionGenerator()
                    data_alert['session_alert'] = sess
                    data_alert["ecart"] = instance.ecart

                    serializer = AlerteEpSerializer(data=data_alert)
                    serializer.is_valid(raise_exception=True)
                    alert = serializer.save()
                    alert.destinataires.add(*dest_alert) 


                    counts = {}
                    counts["vehicule"]=instance.vehicule_id
                    counts["n_depassement"]= 1
                    counts["n_danger"]=0
                    counts["n_critique"]=0
                    counts["ecart"]=instance.ecart
                    counts["type_ep"]="250 H"
                    counts["session"] = sess
                    serializercount = CountCritiqSerializer(data=counts)                  
                    serializercount.is_valid(raise_exception=True)
                    serializercount.save()
                    

            
            if 275.0 < instance.ecart <= 375.0:
                data_alert = {}           

                last_enrg = AlerteEp.objects.filter(Q(vehicule=instance.vehicule)).last()
                if last_enrg != None:
                    anc_ep = last_enrg.alerte

                    if last_enrg.statut != "EFFECTUEE":
                        if last_enrg.type_alert == "A VIDANGER":
                            # i = int(EP_MN_GC.index(anc_ep)) + 9
                            i = int(EP_MN_GC.index(anc_ep)) 

                            data_alert['compt'] = instance.compt_act
                            data_alert['alerte'] = EP_MN_GC[i % 8]
                            data_alert['type_alert'] = "EN DEPASSEMENT DANGER"
                            data_alert['message'] = "Danger! Le compteur montre un gros dépassement de "+ str(instance.ecart-250.0) + " heure(s). l'EP "+ str(data_alert['alerte']) + " doit être effectué immédiatement "
                            data_alert['vehicule'] = instance.vehicule_id
                            data_alert['chef_smrlt'] = user_matrlt.id
                            data_alert["nbalert"] = last_enrg.nbalert + 1
                            data_alert['session_alert'] = last_enrg.session_alert
                            data_alert["ecart"] = instance.ecart

                            serializer = AlerteEpSerializer(data=data_alert)
                            serializer.is_valid(raise_exception=True)
                            alert = serializer.save()
                            alert.destinataires.add(*dest_alert) 

                            counts = {}
                            counts["vehicule"]=instance.vehicule_id
                            counts["n_depassement"]= 0
                            counts["n_danger"]=1
                            counts["n_critique"]=0
                            counts["ecart"]=instance.ecart
                            counts["type_ep"]=EP_MN_GC[i % 8]
                            counts["session"] = last_enrg.session_alert 
                            serializercount = CountCritiqSerializer(data=counts)                  
                            serializercount.is_valid(raise_exception=True)
                            serializercount.save()



                        elif last_enrg.type_alert == "EN DEPASSEMENT":
                        
                        
                            data_alert['compt'] = instance.compt_act
                            data_alert['alerte'] = last_enrg.alerte
                            data_alert['type_alert'] = "EN DEPASSEMENT DANGER"
                            data_alert['message'] = "Danger! Le compteur montre un gros dépassement de "+ str(instance.ecart-250.0) + " heure(s). l'EP "+ str(data_alert['alerte']) + " doit être effectué immédiatement "
                            data_alert['vehicule'] = instance.vehicule_id
                            data_alert['chef_smrlt'] = user_matrlt.id
                            data_alert["ecart"] = instance.ecart
                            data_alert["nbalert"] = last_enrg.nbalert + 1
                            data_alert['session_alert'] = last_enrg.session_alert
                            
                            serializer = AlerteEpSerializer(data=data_alert)
                            serializer.is_valid(raise_exception=True)
                            alert = serializer.save()
                            alert.destinataires.add(*dest_alert)


                            counts = {}
                            counts["vehicule"]=instance.vehicule_id
                            counts["n_depassement"]= 0
                            counts["n_danger"]=1
                            counts["n_critique"]=0
                            counts["ecart"]=instance.ecart 
                            counts["type_ep"]=last_enrg.alerte
                            counts["session"] = last_enrg.session_alert 
                            serializercount = CountCritiqSerializer(data=counts)                  
                            serializercount.is_valid(raise_exception=True)
                            serializercount.save()

            
                        elif last_enrg.type_alert == "EN DEPASSEMENT DANGER":


                            data_alert['compt'] = instance.compt_act
                            data_alert['alerte'] = last_enrg.alerte
                            data_alert['type_alert'] = "EN DEPASSEMENT DANGER"
                            data_alert['message'] = "Danger! Le compteur montre un gros dépassement de "+ str(instance.ecart-250.0) + " heure(s). l'EP "+ str(data_alert['alerte']) + " doit être effectué immédiatement "
                            data_alert['vehicule'] = instance.vehicule_id
                            data_alert['chef_smrlt'] = user_matrlt.id
                            data_alert["ecart"] = instance.ecart
                            data_alert["nbalert"] = last_enrg.nbalert + 1
                            data_alert['session_alert'] = last_enrg.session_alert
                            
                            serializer = AlerteEpSerializer(data=data_alert)
                            serializer.is_valid(raise_exception=True)
                            alert = serializer.save()
                            alert.destinataires.add(*dest_alert)


                            counts = {}
                            counts["vehicule"]=instance.vehicule_id
                            counts["n_depassement"]= 0
                            counts["n_danger"]=1
                            counts["n_critique"]=0
                            counts["ecart"]=instance.ecart
                            counts["type_ep"]=last_enrg.alerte
                            counts["session"] = last_enrg.session_alert  
                            serializercount = CountCritiqSerializer(data=counts)                  
                            serializercount.is_valid(raise_exception=True)
                            serializercount.save()
            
                else:

                    data_alert['compt'] = instance.compt_act
                    data_alert['alerte'] = "250 H"
                    data_alert['type_alert'] = "EN DEPASSEMENT DANGER"
                    data_alert['message'] = "Danger! Le compteur montre un gros dépassement de "+ str(instance.ecart-250.0) + " heure(s). l'EP "+ str(data_alert['alerte']) + " doit être effectué immédiatement "
                    data_alert['vehicule'] = instance.vehicule_id
                    data_alert['chef_smrlt'] = user_matrlt.id
                    data_alert["ecart"] = instance.ecart
                    data_alert["nbalert"] = 1
                    sess = SessionGenerator()
                    data_alert['session_alert'] = sess

                    serializer = AlerteEpSerializer(data=data_alert)
                    serializer.is_valid(raise_exception=True)
                    alert = serializer.save()
                    alert.destinataires.add(*dest_alert) 

                    counts = {}
                    counts["vehicule"]=instance.vehicule_id
                    counts["n_depassement"]= 0
                    counts["n_danger"]=1
                    counts["n_critique"]=0
                    counts["ecart"]=instance.ecart 
                    counts["type_ep"]="250 H"
                    counts["session"] = sess
                    serializercount = CountCritiqSerializer(data=counts)                  
                    serializercount.is_valid(raise_exception=True)
                    serializercount.save()


            if 375.0 < instance.ecart: 
                data_alert = {}

                last_enrg = AlerteEp.objects.filter(Q(vehicule=instance.vehicule)).last()
                if last_enrg != None:
                    anc_ep = last_enrg.alerte 

                    if anc_ep in ['250 H', '750 H', '1250 H', '1750 H']:                    
                        i = int(EP_MN_GC.index(anc_ep)) + 9
                    if anc_ep in ['500 H', '1000 H', '1500 H', '2000 H']:
                        i = int(EP_MN_GC.index(anc_ep))

                    if last_enrg.statut != "EFFECTUEE":
                        list_typalert = ["A VIDANGER", "EN DEPASSEMENT", "EN DEPASSEMENT DANGER"]
                        if last_enrg.type_alert in list_typalert:

                            data_alert['compt'] = instance.compt_act
                            data_alert['alerte'] = EP_MN_GC[i % 8]
                            data_alert['type_alert'] = "EN DEPASSEMENT CRITIQUE"
                            data_alert['message'] = "Dépassement critique de "+ str(instance.ecart-250.0) + " heure(s). Arrêtez immédiatement l'activité et allez pour entretien préventif de "+ str(data_alert['alerte'])
                            data_alert['vehicule'] = instance.vehicule_id
                            data_alert['chef_smrlt'] = user_matrlt.id
                            data_alert["ecart"] = instance.ecart
                            data_alert["nbalert"] = last_enrg.nbalert + 1
                            data_alert['session_alert'] =last_enrg.session_alert

                            serializer = AlerteEpSerializer(data=data_alert)
                            serializer.is_valid(raise_exception=True)
                            alert = serializer.save()
                            alert.destinataires.add(*dest_alert) 

                            counts = {}
                            counts["vehicule"]=instance.vehicule_id
                            counts["n_depassement"]= 0
                            counts["n_danger"]=0
                            counts["n_critique"]=1
                            counts["ecart"]=instance.ecart 
                            counts["type_ep"]=EP_MN_GC[i % 8]
                            counts["session"] = last_enrg.session_alert
                            serializercount = CountCritiqSerializer(data=counts)                  
                            serializercount.is_valid(raise_exception=True)
                            serializercount.save()
                        
                        

                        elif last_enrg.type_alert == "EN DEPASSEMENT CRITIQUE":


                            data_alert['compt'] = instance.compt_act
                            data_alert['alerte'] = last_enrg.alerte
                            data_alert['type_alert'] = "EN DEPASSEMENT CRITIQUE"
                            data_alert['message'] = "Dépassement critique de "+ str(instance.ecart-250.0) + " heure(s). Arrêtez immédiatement l'activité et allez pour entretien préventif de "+ str(data_alert['alerte'])
                            data_alert['vehicule'] = instance.vehicule_id
                            data_alert['chef_smrlt'] = user_matrlt.id
                            data_alert["ecart"] = instance.ecart
                            data_alert["nbalert"] = last_enrg.nbalert + 1
                            data_alert['session_alert'] =last_enrg.session_alert
                            
                            serializer = AlerteEpSerializer(data=data_alert)
                            serializer.is_valid(raise_exception=True)
                            alert = serializer.save()
                            alert.destinataires.add(*dest_alert) 


                            counts = {}
                            counts["vehicule"]=instance.vehicule_id
                            counts["n_depassement"]= 0
                            counts["n_danger"]=0
                            counts["n_critique"]=1
                            counts["ecart"]=instance.ecart 
                            counts["type_ep"]=last_enrg.alerte
                            counts["session"] = last_enrg.session_alert
                            serializercount = CountCritiqSerializer(data=counts)                  
                            serializercount.is_valid(raise_exception=True)
                            serializercount.save()

                    else:                        
                        data_alert['compt'] = instance.compt_act
                        data_alert['alerte'] = EP_MN_GC[i % 8]
                        data_alert['type_alert'] = "EN DEPASSEMENT CRITIQUE"
                        data_alert['message'] = "Dépassement critique de "+ str(instance.ecart-250.0) + " heure(s). Arrêtez immédiatement l'activité et allez pour entretien préventif de "+ str(data_alert['alerte'])
                        data_alert['vehicule'] = instance.vehicule_id
                        data_alert['chef_smrlt'] = user_matrlt.id
                        data_alert["nbalert"] = 1
                        data_alert["ecart"] = instance.ecart
                        sess = SessionGenerator()
                        data_alert['session_alert'] = sess

                        serializer = AlerteEpSerializer(data=data_alert)
                        serializer.is_valid(raise_exception=True)
                        alert = serializer.save()
                        alert.destinataires.add(*dest_alert) 

                        counts = {}
                        counts["vehicule"]=instance.vehicule_id
                        counts["n_depassement"]= 0
                        counts["n_danger"]=0
                        counts["n_critique"]=1
                        counts["ecart"]=instance.ecart 
                        counts["type_ep"]= EP_MN_GC[i % 8]
                        counts["session"] = sess
                        serializercount = CountCritiqSerializer(data=counts)                  
                        serializercount.is_valid(raise_exception=True)
                        serializercount.save()
            
                else:

                    data_alert['compt'] = instance.compt_act
                    data_alert['alerte'] = "500 H"
                    data_alert['type_alert'] = "EN DEPASSEMENT CRITIQUE"
                    data_alert['message'] = "Dépassement critique de "+ str(instance.ecart-250.0) + " heure(s). Arrêtez immédiatement l'activité et allez pour entretien préventif de "+ str(data_alert['alerte'])
                    data_alert['vehicule'] = instance.vehicule_id
                    data_alert['chef_smrlt'] = user_matrlt.id
                    data_alert["nbalert"] = 1
                    data_alert["ecart"] = instance.ecart
                    sess = SessionGenerator()
                    data_alert['session_alert'] = sess

                    serializer = AlerteEpSerializer(data=data_alert)
                    serializer.is_valid(raise_exception=True)
                    alert = serializer.save()
                    alert.destinataires.add(*dest_alert) 


                    counts = {}
                    counts["vehicule"]=instance.vehicule_id
                    counts["n_depassement"]= 0
                    counts["n_danger"]=0
                    counts["n_critique"]=1
                    counts["ecart"]=instance.ecart 
                    counts["type_ep"]= "500 H"
                    counts["session"] = sess
                    serializercount = CountCritiqSerializer(data=counts)                  
                    serializercount.is_valid(raise_exception=True)
                    serializercount.save()









        # POUR LES VEHICULES LEGERS

        
        if cat in list_5000km:

            if alt <= instance.ecart <= 5000.0:
                data_alert = {}
                # SI LA DERNIERE ALERTE EST DANS LA PHASE "A VIDANGER"

                last_enrg = AlerteEp.objects.filter(Q(vehicule=instance.vehicule)).last()
                if last_enrg != None:
                    anc_ep = last_enrg.alerte                   

                    if last_enrg.statut == "EFFECTUEE":            # SI LA VIDANGE A ETE FAITE
                        i = int(EP_VL_VT.index(anc_ep)) + 7

                        data_alert['compt'] = instance.compt_act
                        data_alert['alerte'] = EP_VL_VT[i % 6]
                        data_alert['type_alert'] = "A VIDANGER"
                        data_alert["ecart"] = instance.ecart

                        data_alert['message'] = "Alerte pour Entretien Préventif : La " + str(data_alert['alerte']) + " doit être effectuée bientôt dans moins de "+ str(5000.0-instance.ecart) + " kilomètres de fonctionnement"
                        data_alert['vehicule'] = instance.vehicule_id
                        
                        data_alert['chef_smrlt'] = user_matrlt.id
                        data_alert["nbalert"] = 1
                        data_alert['session_alert'] = SessionGenerator()

                        serializer = AlerteEpSerializer(data=data_alert)
                        serializer.is_valid(raise_exception=True)
                        alert = serializer.save()
                        alert.destinataires.add(*dest_alert) 

                    else:            # SI LA VIDANGE  N'A PAS ETE FAITE
                        
                        data_alert['compt'] = instance.compt_act
                        data_alert['alerte'] = last_enrg.alerte
                        data_alert['type_alert'] = "A VIDANGER"

                        data_alert['message'] = "Alerte pour Entretien Préventif : La " + str(last_enrg.alerte) + " doit être effectuée bientôt dans moins de "+ str(5000.0-instance.ecart) + " kilomètres de fonctionnement"
                        data_alert['vehicule'] = instance.vehicule_id
                        
                        data_alert['chef_smrlt'] = user_matrlt.id
                        data_alert['session_alert'] = last_enrg.session_alert
                        data_alert["ecart"] = instance.ecart
                        data_alert["nbalert"] = last_enrg.nbalert + 1

                        serializer = AlerteEpSerializer(data=data_alert)
                        serializer.is_valid(raise_exception=True)
                        alert = serializer.save()
                        alert.destinataires.add(*dest_alert) 



                # S'IL N'YA PAS D'ALERTE DANS CET INTERVALLE
                else:
                    
                    data_alert['compt'] = instance.compt_act
                    data_alert['alerte'] = "5000 KM"
                    data_alert['type_alert'] = "A VIDANGER"
                    data_alert['message'] = "Alerte pour Entretien Préventif : La " + str(data_alert['alerte']) + " doit être effectuée bientôt dans moins de "+ str(5000.0-instance.ecart) + " kilomètres de fonctionnement"
                    data_alert['vehicule'] = instance.vehicule_id
                    
                    data_alert['chef_smrlt'] = user_matrlt.id
                    data_alert["ecart"] = instance.ecart
                    data_alert["nbalert"] = 1
                    data_alert['session_alert'] = SessionGenerator()
                    serializer = AlerteEpSerializer(data=data_alert)
                    serializer.is_valid(raise_exception=True)
                    alert = serializer.save()
                    alert.destinataires.add(*dest_alert)
                    

            # POUR LES DEPASSEMENTS DES ENGIN DE MANUTENTION
            if 5000.0 < instance.ecart <= 5500.0:
                data_alert = {}

                last_enrg = AlerteEp.objects.filter(Q(vehicule=instance.vehicule)).last()
                if last_enrg != None:
                    anc_ep = last_enrg.alerte 

                    if last_enrg.statut != "EFFECTUEE":
                        if last_enrg.type_alert == "A VIDANGER":
                            
                            i = int(EP_VL_VT.index(anc_ep))

                            data_alert['compt'] = instance.compt_act
                            data_alert['alerte'] = EP_VL_VT[i % 6]
                            data_alert['type_alert'] = "EN DEPASSEMENT"
                            data_alert['ecart'] = instance.ecart
                            data_alert['message'] = "Compteur pour vidange En dépassement de "+ str(instance.ecart-5000.0) + " kilomètre(s). l'EP "+ str(data_alert['alerte']) + " doit être effectué immédiatement "
                            data_alert['vehicule'] = instance.vehicule_id
                            data_alert['chef_smrlt'] = user_matrlt.id
                            data_alert["nbalert"] = last_enrg.nbalert + 1
                            data_alert['session_alert'] = last_enrg.session_alert

                            serializer = AlerteEpSerializer(data=data_alert)
                            serializer.is_valid(raise_exception=True)
                            alert = serializer.save()
                            alert.destinataires.add(*dest_alert) 

                            counts = {}
                            counts["vehicule"]=instance.vehicule_id
                            counts["n_depassement"]= 1
                            counts["n_danger"]=0
                            counts["n_critique"]=0
                            counts["ecart"]=instance.ecart 
                            counts["type_ep"]=EP_VL_VT[i % 6]
                            counts["session"] = last_enrg.session_alert
                            serializercount = CountCritiqSerializer(data=counts)                  
                            serializercount.is_valid(raise_exception=True)
                            serializercount.save()
                        
                        elif last_enrg.type_alert == "EN DEPASSEMENT":
                            
                            data_alert['compt'] = instance.compt_act
                            data_alert['alerte'] = last_enrg.alerte
                            data_alert['type_alert'] = "EN DEPASSEMENT"
                            data_alert['ecart'] = instance.ecart
                            data_alert['message'] = "Compteur pour vidange En dépassement de "+ str(instance.ecart-5000.0) + " kilomètre(s). l'EP "+ str(data_alert['alerte']) + " doit être effectué immédiatement "
                            data_alert['vehicule'] = instance.vehicule_id
                            data_alert['chef_smrlt'] = user_matrlt.id
                            data_alert["nbalert"] = last_enrg.nbalert + 1
                            data_alert['session_alert'] = last_enrg.session_alert

                            serializer = AlerteEpSerializer(data=data_alert)
                            serializer.is_valid(raise_exception=True)
                            alert = serializer.save()
                            alert.destinataires.add(*dest_alert)


                            counts = {}
                            counts["vehicule"]=instance.vehicule_id
                            counts["n_depassement"]= 1
                            counts["n_danger"]=0
                            counts["n_critique"]=0
                            counts["ecart"]=instance.ecart
                            counts["type_ep"]=last_enrg.alerte
                            counts["session"] = last_enrg.session_alert
                            serializercount = CountCritiqSerializer(data=counts)                  
                            serializercount.is_valid(raise_exception=True)
                            serializercount.save()

                    else:
                        i = int(EP_VL_VT.index(anc_ep))

                        data_alert['compt'] = instance.compt_act
                        data_alert['alerte'] = EP_VL_VT[i % 6]
                        data_alert['type_alert'] = "EN DEPASSEMENT"
                        data_alert['ecart'] = instance.ecart
                        data_alert['message'] = "Compteur pour vidange En dépassement de "+ str(instance.ecart-5000.0) + " kilomètre(s). l'EP "+ str(data_alert['alerte']) + " doit être effectué immédiatement "
                        data_alert['vehicule'] = instance.vehicule_id
                        data_alert['chef_smrlt'] = user_matrlt.id
                        data_alert["nbalert"] = 1
                        sess = SessionGenerator()
                        data_alert['session_alert'] = sess

                        serializer = AlerteEpSerializer(data=data_alert)
                        serializer.is_valid(raise_exception=True)
                        alert = serializer.save()
                        alert.destinataires.add(*dest_alert) 

                        counts = {}
                        counts["vehicule"]=instance.vehicule_id
                        counts["n_depassement"]= 1
                        counts["n_danger"]=0
                        counts["n_critique"]=0
                        counts["ecart"]=instance.ecart
                        counts["type_ep"]=EP_VL_VT[i % 6]
                        counts["session"] = sess
                        serializercount = CountCritiqSerializer(data=counts)                  
                        serializercount.is_valid(raise_exception=True)
                        serializercount.save()

                else:
                    data_alert['compt'] = instance.compt_act
                    data_alert['alerte'] = "5000 KM"
                    data_alert['type_alert'] = "EN DEPASSEMENT"
                    data_alert['message'] = "Compteur pour vidange En dépassement de "+ str(instance.ecart-5000.0) + " kilomètre(s). l'EP "+ str(data_alert['alerte']) + " doit être effectué immédiatement "
                    data_alert['vehicule'] = instance.vehicule_id
                    data_alert['chef_smrlt'] = user_matrlt.id
                    data_alert["nbalert"] = 1
                    sess = SessionGenerator()
                    data_alert['session_alert'] = sess
                    data_alert["ecart"] = instance.ecart

                    serializer = AlerteEpSerializer(data=data_alert)
                    serializer.is_valid(raise_exception=True)
                    alert = serializer.save()
                    alert.destinataires.add(*dest_alert) 


                    counts = {}
                    counts["vehicule"]=instance.vehicule_id
                    counts["n_depassement"]= 1
                    counts["n_danger"]=0
                    counts["n_critique"]=0
                    counts["ecart"]=instance.ecart
                    counts["type_ep"]="5000 KM"
                    counts["session"] = sess
                    serializercount = CountCritiqSerializer(data=counts)                  
                    serializercount.is_valid(raise_exception=True)
                    serializercount.save()
                    

            
            if 5500.0 < instance.ecart <= 7500.0:
                data_alert = {}           

                last_enrg = AlerteEp.objects.filter(Q(vehicule=instance.vehicule)).last()
                if last_enrg != None:
                    anc_ep = last_enrg.alerte

                    if last_enrg.statut != "EFFECTUEE":
                        if last_enrg.type_alert == "A VIDANGER":
                            
                            i = int(EP_VL_VT.index(anc_ep)) 

                            data_alert['compt'] = instance.compt_act
                            data_alert['alerte'] = EP_VL_VT[i % 6]
                            data_alert['type_alert'] = "EN DEPASSEMENT DANGER"
                            data_alert['message'] = "Danger! Le compteur montre un gros dépassement de "+ str(instance.ecart-5000.0) + " kilomètre(s). l'EP "+ str(data_alert['alerte']) + " doit être effectué immédiatement "
                            data_alert['vehicule'] = instance.vehicule_id
                            data_alert['chef_smrlt'] = user_matrlt.id
                            data_alert["nbalert"] = last_enrg.nbalert + 1
                            data_alert['session_alert'] = last_enrg.session_alert
                            data_alert["ecart"] = instance.ecart

                            serializer = AlerteEpSerializer(data=data_alert)
                            serializer.is_valid(raise_exception=True)
                            alert = serializer.save()
                            alert.destinataires.add(*dest_alert) 

                            counts = {}
                            counts["vehicule"]=instance.vehicule_id
                            counts["n_depassement"]= 0
                            counts["n_danger"]=1
                            counts["n_critique"]=0
                            counts["ecart"]=instance.ecart
                            counts["type_ep"]=EP_VL_VT[i % 6]
                            counts["session"] = last_enrg.session_alert 
                            serializercount = CountCritiqSerializer(data=counts)                  
                            serializercount.is_valid(raise_exception=True)
                            serializercount.save()



                        elif last_enrg.type_alert == "EN DEPASSEMENT":
                        
                        
                            data_alert['compt'] = instance.compt_act
                            data_alert['alerte'] = last_enrg.alerte
                            data_alert['type_alert'] = "EN DEPASSEMENT DANGER"
                            data_alert['message'] = "Danger! Le compteur montre un gros dépassement de "+ str(instance.ecart-5000.0) + " kilomètre(s). l'EP "+ str(data_alert['alerte']) + " doit être effectué immédiatement "
                            data_alert['vehicule'] = instance.vehicule_id
                            data_alert['chef_smrlt'] = user_matrlt.id
                            data_alert["ecart"] = instance.ecart
                            data_alert["nbalert"] = last_enrg.nbalert + 1
                            data_alert['session_alert'] = last_enrg.session_alert
                            
                            serializer = AlerteEpSerializer(data=data_alert)
                            serializer.is_valid(raise_exception=True)
                            alert = serializer.save()
                            alert.destinataires.add(*dest_alert)


                            counts = {}
                            counts["vehicule"]=instance.vehicule_id
                            counts["n_depassement"]= 0
                            counts["n_danger"]=1
                            counts["n_critique"]=0
                            counts["ecart"]=instance.ecart 
                            counts["type_ep"]=last_enrg.alerte
                            counts["session"] = last_enrg.session_alert 
                            serializercount = CountCritiqSerializer(data=counts)                  
                            serializercount.is_valid(raise_exception=True)
                            serializercount.save()

            
                        elif last_enrg.type_alert == "EN DEPASSEMENT DANGER":


                            data_alert['compt'] = instance.compt_act
                            data_alert['alerte'] = last_enrg.alerte
                            data_alert['type_alert'] = "EN DEPASSEMENT DANGER"
                            data_alert['message'] = "Danger! Le compteur montre un gros dépassement de "+ str(instance.ecart-5000.0) + " kilomètre(s). l'EP "+ str(data_alert['alerte']) + " doit être effectué immédiatement "
                            data_alert['vehicule'] = instance.vehicule_id
                            data_alert['chef_smrlt'] = user_matrlt.id
                            data_alert["ecart"] = instance.ecart
                            data_alert["nbalert"] = last_enrg.nbalert + 1
                            data_alert['session_alert'] = last_enrg.session_alert
                            
                            serializer = AlerteEpSerializer(data=data_alert)
                            serializer.is_valid(raise_exception=True)
                            alert = serializer.save()
                            alert.destinataires.add(*dest_alert)


                            counts = {}
                            counts["vehicule"]=instance.vehicule_id
                            counts["n_depassement"]= 0
                            counts["n_danger"]=1
                            counts["n_critique"]=0
                            counts["ecart"]=instance.ecart
                            counts["type_ep"]=last_enrg.alerte
                            counts["session"] = last_enrg.session_alert  
                            serializercount = CountCritiqSerializer(data=counts)                  
                            serializercount.is_valid(raise_exception=True)
                            serializercount.save()
            
                else:

                    data_alert['compt'] = instance.compt_act
                    data_alert['alerte'] = "5000 KM"
                    data_alert['type_alert'] = "EN DEPASSEMENT DANGER"
                    data_alert['message'] = "Danger! Le compteur montre un gros dépassement de "+ str(instance.ecart-5000.0) + " kilomètre(s). l'EP "+ str(data_alert['alerte']) + " doit être effectué immédiatement "
                    data_alert['vehicule'] = instance.vehicule_id
                    data_alert['chef_smrlt'] = user_matrlt.id
                    data_alert["ecart"] = instance.ecart
                    data_alert["nbalert"] = 1
                    sess = SessionGenerator()
                    data_alert['session_alert'] = sess

                    serializer = AlerteEpSerializer(data=data_alert)
                    serializer.is_valid(raise_exception=True)
                    alert = serializer.save()
                    alert.destinataires.add(*dest_alert) 

                    counts = {}
                    counts["vehicule"]=instance.vehicule_id
                    counts["n_depassement"]= 0
                    counts["n_danger"]=1
                    counts["n_critique"]=0
                    counts["ecart"]=instance.ecart 
                    counts["type_ep"]="5000 KM"
                    counts["session"] = sess
                    serializercount = CountCritiqSerializer(data=counts)                  
                    serializercount.is_valid(raise_exception=True)
                    serializercount.save()


            if 7500.0 < instance.ecart: 
                data_alert = {}

                last_enrg = AlerteEp.objects.filter(Q(vehicule=instance.vehicule)).last()
                if last_enrg != None:
                    anc_ep = last_enrg.alerte 

                    if anc_ep in ['5000 KM', '15000 KM', '25000 KM']:                    
                        i = int(EP_VL_VT.index(anc_ep)) + 7
                    if anc_ep in ['10000 KM', '20000 KM', '30000 KM']:
                        i = int(EP_VL_VT.index(anc_ep))

                    if last_enrg.statut != "EFFECTUEE":
                        list_typalert = ["A VIDANGER", "EN DEPASSEMENT", "EN DEPASSEMENT DANGER"]
                        if last_enrg.type_alert in list_typalert:

                            data_alert['compt'] = instance.compt_act
                            data_alert['alerte'] = EP_VL_VT[i % 6]
                            data_alert['type_alert'] = "EN DEPASSEMENT CRITIQUE"
                            data_alert['message'] = "Dépassement critique de "+ str(instance.ecart-5000.0) + " kilomètre(s). Arrêtez immédiatement l'activité et allez pour entretien préventif de "+ str(data_alert['alerte'])
                            data_alert['vehicule'] = instance.vehicule_id
                            data_alert['chef_smrlt'] = user_matrlt.id
                            data_alert["ecart"] = instance.ecart
                            data_alert["nbalert"] = last_enrg.nbalert + 1
                            data_alert['session_alert'] =last_enrg.session_alert

                            serializer = AlerteEpSerializer(data=data_alert)
                            serializer.is_valid(raise_exception=True)
                            alert = serializer.save()
                            alert.destinataires.add(*dest_alert) 

                            counts = {}
                            counts["vehicule"]=instance.vehicule_id
                            counts["n_depassement"]= 0
                            counts["n_danger"]=0
                            counts["n_critique"]=1
                            counts["ecart"]=instance.ecart 
                            counts["type_ep"]=EP_VL_VT[i % 6]
                            counts["session"] = last_enrg.session_alert
                            serializercount = CountCritiqSerializer(data=counts)                  
                            serializercount.is_valid(raise_exception=True)
                            serializercount.save()
                        
                        

                        elif last_enrg.type_alert == "EN DEPASSEMENT CRITIQUE":


                            data_alert['compt'] = instance.compt_act
                            data_alert['alerte'] = last_enrg.alerte
                            data_alert['type_alert'] = "EN DEPASSEMENT CRITIQUE"
                            data_alert['message'] = "Dépassement critique de "+ str(instance.ecart-5000.0) + " kilomètre(s). Arrêtez immédiatement l'activité et allez pour entretien préventif de "+ str(data_alert['alerte'])
                            data_alert['vehicule'] = instance.vehicule_id
                            data_alert['chef_smrlt'] = user_matrlt.id
                            data_alert["ecart"] = instance.ecart
                            data_alert["nbalert"] = last_enrg.nbalert + 1
                            data_alert['session_alert'] =last_enrg.session_alert
                            
                            serializer = AlerteEpSerializer(data=data_alert)
                            serializer.is_valid(raise_exception=True)
                            alert = serializer.save()
                            alert.destinataires.add(*dest_alert) 


                            counts = {}
                            counts["vehicule"]=instance.vehicule_id
                            counts["n_depassement"]= 0
                            counts["n_danger"]=0
                            counts["n_critique"]=1
                            counts["ecart"]=instance.ecart 
                            counts["type_ep"]=last_enrg.alerte
                            counts["session"] = last_enrg.session_alert
                            serializercount = CountCritiqSerializer(data=counts)                  
                            serializercount.is_valid(raise_exception=True)
                            serializercount.save()

                    else:                        
                        data_alert['compt'] = instance.compt_act
                        data_alert['alerte'] = EP_VL_VT[i % 6]
                        data_alert['type_alert'] = "EN DEPASSEMENT CRITIQUE"
                        data_alert['message'] = "Dépassement critique de "+ str(instance.ecart-5000.0) + " kilomètre(s). Arrêtez immédiatement l'activité et allez pour entretien préventif de "+ str(data_alert['alerte'])
                        data_alert['vehicule'] = instance.vehicule_id
                        data_alert['chef_smrlt'] = user_matrlt.id
                        data_alert["nbalert"] = 1
                        data_alert["ecart"] = instance.ecart
                        sess = SessionGenerator()
                        data_alert['session_alert'] = sess

                        serializer = AlerteEpSerializer(data=data_alert)
                        serializer.is_valid(raise_exception=True)
                        alert = serializer.save()
                        alert.destinataires.add(*dest_alert) 

                        counts = {}
                        counts["vehicule"]=instance.vehicule_id
                        counts["n_depassement"]= 0
                        counts["n_danger"]=0
                        counts["n_critique"]=1
                        counts["ecart"]=instance.ecart 
                        counts["type_ep"]= EP_VL_VT[i % 6]
                        counts["session"] = sess
                        serializercount = CountCritiqSerializer(data=counts)                  
                        serializercount.is_valid(raise_exception=True)
                        serializercount.save()
            
                else:

                    data_alert['compt'] = instance.compt_act
                    data_alert['alerte'] = "10000 KM"
                    data_alert['type_alert'] = "EN DEPASSEMENT CRITIQUE"
                    data_alert['message'] = "Dépassement critique de "+ str(instance.ecart-5000.0) + " kilomètre(s). Arrêtez immédiatement l'activité et allez pour entretien préventif de "+ str(data_alert['alerte'])
                    data_alert['vehicule'] = instance.vehicule_id
                    data_alert['chef_smrlt'] = user_matrlt.id
                    data_alert["nbalert"] = 1
                    data_alert["ecart"] = instance.ecart
                    sess = SessionGenerator()
                    data_alert['session_alert'] = sess

                    serializer = AlerteEpSerializer(data=data_alert)
                    serializer.is_valid(raise_exception=True)
                    alert = serializer.save()
                    alert.destinataires.add(*dest_alert) 


                    counts = {}
                    counts["vehicule"]=instance.vehicule_id
                    counts["n_depassement"]= 0
                    counts["n_danger"]=0
                    counts["n_critique"]=1
                    counts["ecart"]=instance.ecart 
                    counts["type_ep"]= "10000 KM"
                    counts["session"] = sess
                    serializercount = CountCritiqSerializer(data=counts)                  
                    serializercount.is_valid(raise_exception=True)
                    serializercount.save()



        # POUR LES POIDS LOURDS GENERATION 1


        
        if cat in list_150h:

            if alt <= instance.ecart <= 150.0:
                data_alert = {}
                # SI LA DERNIERE ALERTE EST DANS LA PHASE "A VIDANGER"

                last_enrg = AlerteEp.objects.filter(Q(vehicule=instance.vehicule)).last()
                if last_enrg != None:
                    anc_ep = last_enrg.alerte                   

                    if last_enrg.statut == "EFFECTUEE":            # SI LA VIDANGE A ETE FAITE
                        i = int(EP_PL1.index(anc_ep)) + 9

                        data_alert['compt'] = instance.compt_act
                        data_alert['alerte'] = EP_PL1[i % 8]
                        data_alert['type_alert'] = "A VIDANGER"
                        data_alert["ecart"] = instance.ecart

                        data_alert['message'] = "Alerte pour Entretien Préventif : La " + str(data_alert['alerte']) + " doit être effectuée bientôt dans moins de "+ str(150.0-instance.ecart) + " heures de fonctionnement"
                        data_alert['vehicule'] = instance.vehicule_id
                        
                        data_alert['chef_smrlt'] = user_matrlt.id
                        data_alert["nbalert"] = 1
                        data_alert['session_alert'] = SessionGenerator()

                        serializer = AlerteEpSerializer(data=data_alert)
                        serializer.is_valid(raise_exception=True)
                        alert = serializer.save()
                        alert.destinataires.add(*dest_alert) 

                    else:            # SI LA VIDANGE  N'A PAS ETE FAITE
                        
                        data_alert['compt'] = instance.compt_act
                        data_alert['alerte'] = last_enrg.alerte
                        data_alert['type_alert'] = "A VIDANGER"

                        data_alert['message'] = "Alerte pour Entretien Préventif : La " + str(last_enrg.alerte) + " doit être effectuée bientôt dans moins de "+ str(150.0-instance.ecart) + " heures de fonctionnement"
                        data_alert['vehicule'] = instance.vehicule_id
                        
                        data_alert['chef_smrlt'] = user_matrlt.id
                        data_alert['session_alert'] = last_enrg.session_alert
                        data_alert["ecart"] = instance.ecart
                        data_alert["nbalert"] = last_enrg.nbalert + 1

                        serializer = AlerteEpSerializer(data=data_alert)
                        serializer.is_valid(raise_exception=True)
                        alert = serializer.save()
                        alert.destinataires.add(*dest_alert) 



                # S'IL N'YA PAS D'ALERTE DANS CET INTERVALLE
                else:
                    
                    data_alert['compt'] = instance.compt_act
                    data_alert['alerte'] = "150 H"
                    data_alert['type_alert'] = "A VIDANGER"
                    data_alert['message'] = "Alerte pour Entretien Préventif : La " + str(data_alert['alerte']) + " doit être effectuée bientôt dans moins de "+ str(150.0-instance.ecart) + " heures de fonctionnement"
                    data_alert['vehicule'] = instance.vehicule_id
                    
                    data_alert['chef_smrlt'] = user_matrlt.id
                    data_alert["ecart"] = instance.ecart
                    data_alert["nbalert"] = 1
                    data_alert['session_alert'] = SessionGenerator()
                    serializer = AlerteEpSerializer(data=data_alert)
                    serializer.is_valid(raise_exception=True)
                    alert = serializer.save()
                    alert.destinataires.add(*dest_alert)
                    

            # POUR LES DEPASSEMENTS DES ENGIN DE MANUTENTION
            if 150.0 < instance.ecart <= 165.0:
                data_alert = {}

                last_enrg = AlerteEp.objects.filter(Q(vehicule=instance.vehicule)).last()
                if last_enrg != None:
                    anc_ep = last_enrg.alerte 

                    if last_enrg.statut != "EFFECTUEE":
                        if last_enrg.type_alert == "A VIDANGER":
                            
                            i = int(EP_PL1.index(anc_ep))

                            data_alert['compt'] = instance.compt_act
                            data_alert['alerte'] = EP_PL1[i % 8]
                            data_alert['type_alert'] = "EN DEPASSEMENT"
                            data_alert['ecart'] = instance.ecart
                            data_alert['message'] = "Compteur pour vidange En dépassement de "+ str(instance.ecart-150.0) + " heure(s). l'EP "+ str(data_alert['alerte']) + " doit être effectué immédiatement "
                            data_alert['vehicule'] = instance.vehicule_id
                            data_alert['chef_smrlt'] = user_matrlt.id
                            data_alert["nbalert"] = last_enrg.nbalert + 1
                            data_alert['session_alert'] = last_enrg.session_alert

                            serializer = AlerteEpSerializer(data=data_alert)
                            serializer.is_valid(raise_exception=True)
                            alert = serializer.save()
                            alert.destinataires.add(*dest_alert) 

                            counts = {}
                            counts["vehicule"]=instance.vehicule_id
                            counts["n_depassement"]= 1
                            counts["n_danger"]=0
                            counts["n_critique"]=0
                            counts["ecart"]=instance.ecart 
                            counts["type_ep"]=EP_PL1[i % 8]
                            counts["session"] = last_enrg.session_alert
                            serializercount = CountCritiqSerializer(data=counts)                  
                            serializercount.is_valid(raise_exception=True)
                            serializercount.save()
                        
                        elif last_enrg.type_alert == "EN DEPASSEMENT":
                            
                            data_alert['compt'] = instance.compt_act
                            data_alert['alerte'] = last_enrg.alerte
                            data_alert['type_alert'] = "EN DEPASSEMENT"
                            data_alert['ecart'] = instance.ecart
                            data_alert['message'] = "Compteur pour vidange En dépassement de "+ str(instance.ecart-150.0) + " heure(s). l'EP "+ str(data_alert['alerte']) + " doit être effectué immédiatement "
                            data_alert['vehicule'] = instance.vehicule_id
                            data_alert['chef_smrlt'] = user_matrlt.id
                            data_alert["nbalert"] = last_enrg.nbalert + 1
                            data_alert['session_alert'] = last_enrg.session_alert

                            serializer = AlerteEpSerializer(data=data_alert)
                            serializer.is_valid(raise_exception=True)
                            alert = serializer.save()
                            alert.destinataires.add(*dest_alert)


                            counts = {}
                            counts["vehicule"]=instance.vehicule_id
                            counts["n_depassement"]= 1
                            counts["n_danger"]=0
                            counts["n_critique"]=0
                            counts["ecart"]=instance.ecart
                            counts["type_ep"]=last_enrg.alerte
                            counts["session"] = last_enrg.session_alert
                            serializercount = CountCritiqSerializer(data=counts)                  
                            serializercount.is_valid(raise_exception=True)
                            serializercount.save()

                    else:
                        i = int(EP_PL1.index(anc_ep))

                        data_alert['compt'] = instance.compt_act
                        data_alert['alerte'] = EP_PL1[i % 8]
                        data_alert['type_alert'] = "EN DEPASSEMENT"
                        data_alert['ecart'] = instance.ecart
                        data_alert['message'] = "Compteur pour vidange En dépassement de "+ str(instance.ecart-150.0) + " heure(s). l'EP "+ str(data_alert['alerte']) + " doit être effectué immédiatement "
                        data_alert['vehicule'] = instance.vehicule_id
                        data_alert['chef_smrlt'] = user_matrlt.id
                        data_alert["nbalert"] = 1
                        sess = SessionGenerator()
                        data_alert['session_alert'] = sess

                        serializer = AlerteEpSerializer(data=data_alert)
                        serializer.is_valid(raise_exception=True)
                        alert = serializer.save()
                        alert.destinataires.add(*dest_alert) 

                        counts = {}
                        counts["vehicule"]=instance.vehicule_id
                        counts["n_depassement"]= 1
                        counts["n_danger"]=0
                        counts["n_critique"]=0
                        counts["ecart"]=instance.ecart
                        counts["type_ep"]=EP_PL1[i % 8]
                        counts["session"] = sess
                        serializercount = CountCritiqSerializer(data=counts)                  
                        serializercount.is_valid(raise_exception=True)
                        serializercount.save()

                else:
                    data_alert['compt'] = instance.compt_act
                    data_alert['alerte'] = "150 H"
                    data_alert['type_alert'] = "EN DEPASSEMENT"
                    data_alert['message'] = "Compteur pour vidange En dépassement de "+ str(instance.ecart-150.0) + " heure(s). l'EP "+ str(data_alert['alerte']) + " doit être effectué immédiatement "
                    data_alert['vehicule'] = instance.vehicule_id
                    data_alert['chef_smrlt'] = user_matrlt.id
                    data_alert["nbalert"] = 1
                    sess = SessionGenerator()
                    data_alert['session_alert'] = sess
                    data_alert["ecart"] = instance.ecart

                    serializer = AlerteEpSerializer(data=data_alert)
                    serializer.is_valid(raise_exception=True)
                    alert = serializer.save()
                    alert.destinataires.add(*dest_alert) 


                    counts = {}
                    counts["vehicule"]=instance.vehicule_id
                    counts["n_depassement"]= 1
                    counts["n_danger"]=0
                    counts["n_critique"]=0
                    counts["ecart"]=instance.ecart
                    counts["type_ep"]="150 H"
                    counts["session"] = sess
                    serializercount = CountCritiqSerializer(data=counts)                  
                    serializercount.is_valid(raise_exception=True)
                    serializercount.save()
                    

            
            if 165.0 < instance.ecart <= 225.0:
                data_alert = {}           

                last_enrg = AlerteEp.objects.filter(Q(vehicule=instance.vehicule)).last()
                if last_enrg != None:
                    anc_ep = last_enrg.alerte

                    if last_enrg.statut != "EFFECTUEE":
                        if last_enrg.type_alert == "A VIDANGER":
                            
                            i = int(EP_PL1.index(anc_ep)) 

                            data_alert['compt'] = instance.compt_act
                            data_alert['alerte'] = EP_PL1[i % 8]
                            data_alert['type_alert'] = "EN DEPASSEMENT DANGER"
                            data_alert['message'] = "Danger! Le compteur montre un gros dépassement de "+ str(instance.ecart-150.0) + " heure(s). l'EP "+ str(data_alert['alerte']) + " doit être effectué immédiatement "
                            data_alert['vehicule'] = instance.vehicule_id
                            data_alert['chef_smrlt'] = user_matrlt.id
                            data_alert["nbalert"] = last_enrg.nbalert + 1
                            data_alert['session_alert'] = last_enrg.session_alert
                            data_alert["ecart"] = instance.ecart

                            serializer = AlerteEpSerializer(data=data_alert)
                            serializer.is_valid(raise_exception=True)
                            alert = serializer.save()
                            alert.destinataires.add(*dest_alert) 

                            counts = {}
                            counts["vehicule"]=instance.vehicule_id
                            counts["n_depassement"]= 0
                            counts["n_danger"]=1
                            counts["n_critique"]=0
                            counts["ecart"]=instance.ecart
                            counts["type_ep"]=EP_PL1[i % 8]
                            counts["session"] = last_enrg.session_alert 
                            serializercount = CountCritiqSerializer(data=counts)                  
                            serializercount.is_valid(raise_exception=True)
                            serializercount.save()



                        elif last_enrg.type_alert == "EN DEPASSEMENT":
                        
                        
                            data_alert['compt'] = instance.compt_act
                            data_alert['alerte'] = last_enrg.alerte
                            data_alert['type_alert'] = "EN DEPASSEMENT DANGER"
                            data_alert['message'] = "Danger! Le compteur montre un gros dépassement de "+ str(instance.ecart-150.0) + " heure(s). l'EP "+ str(data_alert['alerte']) + " doit être effectué immédiatement "
                            data_alert['vehicule'] = instance.vehicule_id
                            data_alert['chef_smrlt'] = user_matrlt.id
                            data_alert["ecart"] = instance.ecart
                            data_alert["nbalert"] = last_enrg.nbalert + 1
                            data_alert['session_alert'] = last_enrg.session_alert
                            
                            serializer = AlerteEpSerializer(data=data_alert)
                            serializer.is_valid(raise_exception=True)
                            alert = serializer.save()
                            alert.destinataires.add(*dest_alert)


                            counts = {}
                            counts["vehicule"]=instance.vehicule_id
                            counts["n_depassement"]= 0
                            counts["n_danger"]=1
                            counts["n_critique"]=0
                            counts["ecart"]=instance.ecart 
                            counts["type_ep"]=last_enrg.alerte
                            counts["session"] = last_enrg.session_alert 
                            serializercount = CountCritiqSerializer(data=counts)                  
                            serializercount.is_valid(raise_exception=True)
                            serializercount.save()

            
                        elif last_enrg.type_alert == "EN DEPASSEMENT DANGER":


                            data_alert['compt'] = instance.compt_act
                            data_alert['alerte'] = last_enrg.alerte
                            data_alert['type_alert'] = "EN DEPASSEMENT DANGER"
                            data_alert['message'] = "Danger! Le compteur montre un gros dépassement de "+ str(instance.ecart-150.0) + " heure(s). l'EP "+ str(data_alert['alerte']) + " doit être effectué immédiatement "
                            data_alert['vehicule'] = instance.vehicule_id
                            data_alert['chef_smrlt'] = user_matrlt.id
                            data_alert["ecart"] = instance.ecart
                            data_alert["nbalert"] = last_enrg.nbalert + 1
                            data_alert['session_alert'] = last_enrg.session_alert
                            
                            serializer = AlerteEpSerializer(data=data_alert)
                            serializer.is_valid(raise_exception=True)
                            alert = serializer.save()
                            alert.destinataires.add(*dest_alert)


                            counts = {}
                            counts["vehicule"]=instance.vehicule_id
                            counts["n_depassement"]= 0
                            counts["n_danger"]=1
                            counts["n_critique"]=0
                            counts["ecart"]=instance.ecart
                            counts["type_ep"]=last_enrg.alerte
                            counts["session"] = last_enrg.session_alert  
                            serializercount = CountCritiqSerializer(data=counts)                  
                            serializercount.is_valid(raise_exception=True)
                            serializercount.save()
            
                else:

                    data_alert['compt'] = instance.compt_act
                    data_alert['alerte'] = "150 H"
                    data_alert['type_alert'] = "EN DEPASSEMENT DANGER"
                    data_alert['message'] = "Danger! Le compteur montre un gros dépassement de "+ str(instance.ecart-150.0) + " heure(s). l'EP "+ str(data_alert['alerte']) + " doit être effectué immédiatement "
                    data_alert['vehicule'] = instance.vehicule_id
                    data_alert['chef_smrlt'] = user_matrlt.id
                    data_alert["ecart"] = instance.ecart
                    data_alert["nbalert"] = 1
                    sess = SessionGenerator()
                    data_alert['session_alert'] = sess

                    serializer = AlerteEpSerializer(data=data_alert)
                    serializer.is_valid(raise_exception=True)
                    alert = serializer.save()
                    alert.destinataires.add(*dest_alert) 

                    counts = {}
                    counts["vehicule"]=instance.vehicule_id
                    counts["n_depassement"]= 0
                    counts["n_danger"]=1
                    counts["n_critique"]=0
                    counts["ecart"]=instance.ecart 
                    counts["type_ep"]="150 H"
                    counts["session"] = sess
                    serializercount = CountCritiqSerializer(data=counts)                  
                    serializercount.is_valid(raise_exception=True)
                    serializercount.save()


            if 225.0 < instance.ecart: 
                data_alert = {}

                last_enrg = AlerteEp.objects.filter(Q(vehicule=instance.vehicule)).last()
                if last_enrg != None:
                    anc_ep = last_enrg.alerte 

                    if anc_ep in ['150 H', '450 H', '750 H', '1050 H']:                    
                        i = int(EP_PL1.index(anc_ep)) + 9
                    if anc_ep in ['300 H', '600 H', '900 H', '1200 H']:
                        i = int(EP_PL1.index(anc_ep))

                    if last_enrg.statut != "EFFECTUEE":
                        list_typalert = ["A VIDANGER", "EN DEPASSEMENT", "EN DEPASSEMENT DANGER"]
                        if last_enrg.type_alert in list_typalert:

                            data_alert['compt'] = instance.compt_act
                            data_alert['alerte'] = EP_PL1[i % 8]
                            data_alert['type_alert'] = "EN D_enrEPASSEMENT CRITIQUE"
                            data_alert['message'] = "Dépassement critique de "+ str(instance.ecart-150.0) + " heure(s). Arrêtez immédiatement l'activité et allez pour entretien préventif de "+ str(data_alert['alerte'])
                            data_alert['vehicule'] = instance.vehicule_id
                            data_alert['chef_smrlt'] = user_matrlt.id
                            data_alert["ecart"] = instance.ecart
                            data_alert["nbalert"] = last_enrg.nbalert + 1
                            data_alert['session_alert'] =last_enrg.session_alert

                            serializer = AlerteEpSerializer(data=data_alert)
                            serializer.is_valid(raise_exception=True)
                            alert = serializer.save()
                            alert.destinataires.add(*dest_alert) 

                            counts = {}
                            counts["vehicule"]=instance.vehicule_id
                            counts["n_depassement"]= 0
                            counts["n_danger"]=0
                            counts["n_critique"]=1
                            counts["ecart"]=instance.ecart 
                            counts["type_ep"]=EP_PL1[i % 8]
                            counts["session"] = last_enrg.session_alert
                            serializercount = CountCritiqSerializer(data=counts)                  
                            serializercount.is_valid(raise_exception=True)
                            serializercount.save()
                        
                        

                        elif last_enrg.type_alert == "EN DEPASSEMENT CRITIQUE":


                            data_alert['compt'] = instance.compt_act
                            data_alert['alerte'] = last_enrg.alerte
                            data_alert['type_alert'] = "EN DEPASSEMENT CRITIQUE"
                            data_alert['message'] = "Dépassement critique de "+ str(instance.ecart-150.0) + " heure(s). Arrêtez immédiatement l'activité et allez pour entretien préventif de "+ str(data_alert['alerte'])
                            data_alert['vehicule'] = instance.vehicule_id
                            data_alert['chef_smrlt'] = user_matrlt.id
                            data_alert["ecart"] = instance.ecart
                            data_alert["nbalert"] = last_enrg.nbalert + 1
                            data_alert['session_alert'] =last_enrg.session_alert
                            
                            serializer = AlerteEpSerializer(data=data_alert)
                            serializer.is_valid(raise_exception=True)
                            alert = serializer.save()
                            alert.destinataires.add(*dest_alert) 


                            counts = {}
                            counts["vehicule"]=instance.vehicule_id
                            counts["n_depassement"]= 0
                            counts["n_danger"]=0
                            counts["n_critique"]=1
                            counts["ecart"]=instance.ecart 
                            counts["type_ep"]=last_enrg.alerte
                            counts["session"] = last_enrg.session_alert
                            serializercount = CountCritiqSerializer(data=counts)                  
                            serializercount.is_valid(raise_exception=True)
                            serializercount.save()

                    else:                        
                        data_alert['compt'] = instance.compt_act
                        data_alert['alerte'] = EP_PL1[i % 8]
                        data_alert['type_alert'] = "EN DEPASSEMENT CRITIQUE"
                        data_alert['message'] = "Dépassement critique de "+ str(instance.ecart-150.0) + " heure(s). Arrêtez immédiatement l'activité et allez pour entretien préventif de "+ str(data_alert['alerte'])
                        data_alert['vehicule'] = instance.vehicule_id
                        data_alert['chef_smrlt'] = user_matrlt.id
                        data_alert["nbalert"] = 1
                        data_alert["ecart"] = instance.ecart
                        sess = SessionGenerator()
                        data_alert['session_alert'] = sess

                        serializer = AlerteEpSerializer(data=data_alert)
                        serializer.is_valid(raise_exception=True)
                        alert = serializer.save()
                        alert.destinataires.add(*dest_alert) 

                        counts = {}
                        counts["vehicule"]=instance.vehicule_id
                        counts["n_depassement"]= 0
                        counts["n_danger"]=0
                        counts["n_critique"]=1
                        counts["ecart"]=instance.ecart 
                        counts["type_ep"]= EP_PL1[i % 8]
                        counts["session"] = sess
                        serializercount = CountCritiqSerializer(data=counts)                  
                        serializercount.is_valid(raise_exception=True)
                        serializercount.save()
            
                else:

                    data_alert['compt'] = instance.compt_act
                    data_alert['alerte'] = "300 H"
                    data_alert['type_alert'] = "EN DEPASSEMENT CRITIQUE"
                    data_alert['message'] = "Dépassement critique de "+ str(instance.ecart-150.0) + " heure(s). Arrêtez immédiatement l'activité et allez pour entretien préventif de "+ str(data_alert['alerte'])
                    data_alert['vehicule'] = instance.vehicule_id
                    data_alert['chef_smrlt'] = user_matrlt.id
                    data_alert["nbalert"] = 1
                    data_alert["ecart"] = instance.ecart
                    sess = SessionGenerator()
                    data_alert['session_alert'] = sess

                    serializer = AlerteEpSerializer(data=data_alert)
                    serializer.is_valid(raise_exception=True)
                    alert = serializer.save()
                    alert.destinataires.add(*dest_alert) 


                    counts = {}
                    counts["vehicule"]=instance.vehicule_id
                    counts["n_depassement"]= 0
                    counts["n_danger"]=0
                    counts["n_critique"]=1
                    counts["ecart"]=instance.ecart 
                    counts["type_ep"]= "300 H"
                    counts["session"] = sess
                    serializercount = CountCritiqSerializer(data=counts)                  
                    serializercount.is_valid(raise_exception=True)
                    serializercount.save()






