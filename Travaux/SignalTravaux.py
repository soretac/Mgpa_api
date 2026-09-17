from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import DTPrev, VehDepoEp
from .SerializerTravaux import VehDepoEpSerializer
from MatRoulant.models import VehiculesEses
from django.contrib.auth import get_user_model
from Mgpa_api.middleware import get_tenant
from fillpdf import fillpdfs
import datetime
from django.db.models import Q
from Client.models import Clients
from PreventApps.models import SuiviEp
from django.core.files import File



User = get_user_model()

@receiver(post_save, sender=DTPrev)
def createSuiviEp(sender, instance, created, **kwargs):

    if created:
        sche = str(instance.num_dtep).split('-')[0]
        print(sche)
        clients = Clients.objects.filter(schema_name=sche).first()

        sep = SuiviEp.objects.filter(id=instance.ep_id).first()

        veh = VehiculesEses.objects.filter(id=instance.vehicule_id).first()
        dies = None
        ess = None
        gz = None

        normal = None
        urgent = None
        turgent = None

        prio = instance.priorite
        if prio == "NORMAL":
            normal = "Yes_mgsf"
        elif prio == "URGENT":
            urgent = "Yes_mgsf"
        elif prio == "TRES URGENT":
            turgent = "Yes_mgsf"

        ener = veh.energie
        if ener == "ESSENCE":
            ess = "Yes_iogj"
        elif ener == "DIESEL":
            dies = "Yes_iogj"
        elif ener == "GAZ":
            gz = "Yes_iogj"

        conds = veh.conducteurs.prefetch_related().all()
        tels = []
        noms = []

        garag = User.objects.filter(id=instance.garagiste_id).first()
        demand = User.objects.filter(id=instance.demandeur_id).first()
        chef_fonct = User.objects.filter(Q(site=veh.site_fonct) & Q(type="CHEF FONCTIONNEL")).first()
    
        for cond in conds:
            # us = User.objects.filter(id=cond).first()
            tels.append(cond.mobile)
            noms.append(cond.last_name)

        lesnoms = ""
        lestels = ""

        for nom in noms:
            lesnoms = lesnoms + str(nom) + ", "

        for tel in tels:
            lestels = lestels + str(tel) + " / "
            


        # CREER LE FICHIER PDF DE LA DEMANDE DE TRAVAIL

        # fichier_dt = os.path.join(settings.MEDIA_ROOT, "fichiers/demande_travail.pdf") 

        forms_fields = list(fillpdfs.get_form_fields("demande_travail.pdf").keys())
        print(forms_fields)

        info = "" + str(clients.nom_ese) + ". \n" + str(clients.description_ese) + "\n" + "Site web: " + str(clients.siteweb) + ". Adresse: " + str(clients.adresse) + ". Téléphone: " + str(clients.phone1) + " / " + str(clients.phone2) + "\n" + ". NIU: " + str(clients.niu_ese) 

        data_pdf = {
            forms_fields[0] : str(veh.marque),    # veh_marque
            forms_fields[1] : "Yes_cski",         # checkbox_preventif
            forms_fields[2] : "",                  # checkbox_correctif
            forms_fields[3] : dies,                  # checkbox_diesel
            forms_fields[4] : ess,                  # checkbox_essence
            forms_fields[5] : gz,                  # checkbox_hybride
            forms_fields[6] : "",                  # checkbox_curatif
            forms_fields[7] : normal,                  # checkbox_prionormal
            forms_fields[8] : urgent,                  # checkbox_priourgent
            forms_fields[9] : turgent,                  # checkbox_prioturgent
            forms_fields[10] : info,                  # info_ese
            forms_fields[11] : str(clients.slogan),                  # slogan_ese
            forms_fields[12] : instance.num_dtep,                  # ndemande
            forms_fields[13] : str(instance.date_depo),                  # date
            forms_fields[14] : "",                                      # heure
            forms_fields[15] : str(demand.last_name) + " " + str(demand.first_name),                  # ini_nomprenom
            forms_fields[16] : str(veh.immat),                  # veh_immat
            forms_fields[17] : str(demand.poste),                  # ini_fonction
            forms_fields[18] : str(veh.num_parc),                  # veh_nparc
            forms_fields[19] : str(demand.mobile),                  # ini_tel
            forms_fields[20] : str(veh.model),                  # veh_modele
            forms_fields[21] : str(demand.email),                  # ini_mail
            forms_fields[22] : str(veh.serie),                  # veh_chassis
            forms_fields[23] : str(veh.date_mse),                  # veh_datemes
            forms_fields[24] : str(sep.compt_act),                  # veh_compteur
            forms_fields[25] : lesnoms,                  # veh_chauffeur
            forms_fields[26] : lestels,                  # veh_tel
            forms_fields[27] : str(veh.affectation),                  # veh_site
            forms_fields[28] : str(instance.description),                  # textarea_panne
            forms_fields[29] : "",                  # atelier_nom
            forms_fields[30] : str(garag.last_name)+" "+str(garag.first_name),                  # atelier_nomchef
            forms_fields[31] : "",                  # atelier_localise
            forms_fields[32] : "",                  # textarea_symptomes
            forms_fields[33] : str(garag.mobile),                  # atelier_telephone
            forms_fields[34] : str(demand.last_name) + " " + str(demand.first_name),                  # nom_respons1
            forms_fields[35] : str(chef_fonct.last_name) + " " + str(chef_fonct.first_name),                  # nom_respons2
            forms_fields[36] : "",                  # nom_respons3
            forms_fields[37] : str(demand.poste),                  # fonct_respons1
            forms_fields[38] : str(chef_fonct.poste),                  # fonct_respons2
            forms_fields[39] : "",                  # fonct_respons3
            forms_fields[40] : datetime.date.today(),                  # date_respons1
            forms_fields[41] : datetime.date.today(),                  # date_respons2
            forms_fields[42] : ""                  # date_respons3
        }

        print("******************************************************************************\n")


        print(data_pdf)

        fillpdfs.write_fillable_pdf(input_pdf_path="demande_travail.pdf", output_pdf_path="Demande_Travail_EP - " +str(veh.immat)+" - "+str(instance.date_depo)+".pdf", data_dict=data_pdf, flatten=True)

        with open("Demande_Travail_EP - " +str(veh.immat)+" - "+str(instance.date_depo)+".pdf", 'rb') as local_file:
            # 3. Use the field's .save() method directly
            instance.document_dtep.save("Demande_Travail_EP-" +str(veh.immat)+"-"+str(instance.date_depo)+".pdf", File(local_file), save=True)


        # data_dispo = {}

        # conds = list(instance.vehicule.conducteurs.all())
        # print(conds)

        # data_dispo["dtep"] = instance.id
        # data_dispo["depot_utilisateur"] = "PAS DEPOSE"
        # data_dispo["date_utilisateur"] = datetime.datetime.today()
        # data_dispo["garagiste"] = instance.garagiste_id
        # data_dispo["valid_garage"] = "NON RECU"
        # data_dispo["utilisateur"] = None
        # data_dispo["observation_util"] = ""
        # data_dispo["observation_gar"] = ""
        # data_dispo["signature_util"] = None
        # data_dispo["signature_gar"] = None

        # serializer_dispo = VehDispoEPSerializer(data=data_dispo)
        # serializer_dispo.is_valid(raise_exception=True)
        # serializer_dispo.save()

    


    
