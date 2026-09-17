from django.db import models
from MatRoulant.models import VehiculesEses
from django.contrib.auth import get_user_model
from CompteurApps.models import AlerteEp
from PreventApps.models import SuiviEp
from django.utils import timezone
from datetime import date
from MgpaUsers.models import UserAccount

User = get_user_model()



class NumPrefix(models.Model):
    entete = models.CharField(max_length=20)
    prefix = models.CharField(max_length=3)
    statut = models.CharField(max_length=20, default="valide")
    suffix = models.CharField(max_length=3, default="000")

    def __str__(self):
        return f"{self.entete}-{self.prefix}"



class DTPrev(models.Model):

    # TYPES_DT = [
    #     ("", ""),
    #     ("DEMANDE DE MAINTENANCE PREVENTIVE", "DEMANDE DE MAINTENANCE PREVENTIVE"),
    #     ("DEMANDE MAINTENANCE CURATIVE", "DEMANDE MAINTENANCE CURATIVE"),
    #     ("DEMANDE DE MAINTENANCE CORRECTIVE", "DEMANDE DE MAINTENANCE CORRECTIVE"),
    # ]

    STATUTEP = [
        ("En Demande", "En Demande"),
        ("En Cours", "En Cours"),
        ("Réalisé", "Réalisé"),
        ("Réalisé Partiel", "Réalisé Partiel"),
        ("Non Réalisé", "Non Réalisé"),
        ("abandonné", "abandonné"),
    ]

    PRIORITE = [
        ("NORMAL",  "NORMAL"),
        ("URGENT", "URGENT"),
        ("TRES URGENT", "TRES URGENT"),
    ]

    num_dtep = models.CharField(max_length=255, unique=True)
    vehicule = models.ForeignKey(VehiculesEses, null=True, on_delete=models.SET_NULL, related_name="veh_dt")
    demandeur = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="dt_exp")
    garagiste = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="dt_dest")
    ep        = models.ForeignKey(SuiviEp, null=True, on_delete=models.SET_NULL, blank=True, related_name="dt_eps")
    description = models.TextField()
    date_depo = models.DateField(default=date.today())
    statut_dt = models.CharField(max_length=50, choices=STATUTEP, default="En Demande")
    date_demande = models.DateField(auto_now_add=True)
    document_dtep = models.FileField(upload_to='demandes_travaux/', blank=True, null=True)
    priorite = models.CharField(max_length=50, choices=PRIORITE, default="NORMAL")


    def __str__(self):
        return "DT N°{} - {} - {} - {} - {}".format(self.num_dtep, self.vehicule.immat, self.date_demande, self.ep.prochain_ep, self.garagiste)



class DTCurative(models.Model):

    STATUTEP = [
        ("En Demande", "En Demande"),
        ("En Cours", "En Cours"),
        ("Réalisé", "Réalisé"),
        ("Réalisé Partiel", "Réalisé Partiel"),
        ("Non Réalisé", "Non Réalisé"),
        ("abandonné", "abandonné"),
    ]
    
    PRIORITE = [
        ("NORMAL",  "NORMAL"),
        ("URGENT", "URGENT"),
        ("TRES URGENT", "TRES URGENT"),
    ]

    num_dtcur = models.CharField(max_length=255, unique=True)
    vehicule = models.ForeignKey(VehiculesEses, null=True, on_delete=models.SET_NULL, related_name="veh_dtcur")
    demandeur = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="dtcur_demand")
    garagiste = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="dtcur_gar")
    # ep        = models.ForeignKey(SuiviEp, null=True, on_delete=models.SET_NULL, blank=True, related_name="dt_eps")
    descript_panne = models.TextField()
    declare_panne = models.TextField()
    utilisateurs = models.ManyToManyField(User)
    date_depo = models.DateField(default=date.today())
    statut_dt = models.CharField(max_length=50, choices=STATUTEP, default="En Demande")
    date_demande = models.DateField(auto_now_add=True)
    document_dtcurat = models.FileField(upload_to='demandes_travaux/', blank=True, null=True)
    priorite = models.CharField(max_length=50, choices=PRIORITE, default="NORMAL")



class VehDepoEp(models.Model):

    DEPOT = [ 
        ("PAS DEPOSE", "PAS DEPOSE"),
        ("DEPOSE",  "DEPOSE"),
    
    ]

    dtep = models.ForeignKey(DTPrev, on_delete=models.SET_NULL, null=True, related_name="depo_dtep")
    utilisateur = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True, related_name="depo_utilisateur")
    depot_utilisateur = models.CharField("DEPOT UTILISATEUR", max_length=20, choices=DEPOT, default="PAS DEPOSE")
    date_depot = models.DateTimeField(auto_created=True)
    observation_util = models.TextField(null=True, blank=True)
    signature_util = models.ImageField(upload_to="signatures/", blank=True, null=True)
    

    def __str__(self):
        return "{} - {} - {} - {} - {} {}".format(self.dtep.vehicule.immat, self.dtep.ep.prochain_ep, self.dtep.date_depo, self.depot_utilisateur, self.utilisateur.last_name, self.utilisateur.first_name)


class VehRecuEp(models.Model):

    RECEPTION = [    
        ("NON RECU", "NON RECU"),
        ("RECU",  "RECU"),
        
    ]

    dtep = models.ForeignKey(DTPrev, on_delete=models.SET_NULL, null=True, related_name="recu_dtep")
    date_recept = models.DateTimeField(auto_created=True)
    garagiste = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="recu_garage")
    valid_garage = models.CharField("DEPOT GARAGE", max_length=20, choices=RECEPTION, default="NON RECU")
    observation_gar = models.TextField(null=True, blank=True)
    signature_gar = models.ImageField(upload_to="signatures/", blank=True, null=True)

    def __str__(self):
        return "{} - {} - {} - {} - {} {}".format(self.dtep.vehicule.immat, self.dtep.ep.prochain_ep, self.dtep.date_recept, self.valid_garage, self.garagiste.last_name, self.garagiste.first_name)





class FcMnExt(models.Model):

    ext_amortisseur_colonne_direction = models.CharField("Amortisseur colonne direction", max_length=255, null=True, blank=True)
    ext_calendre_bord_supinf = models.CharField("Calendre de bord sup et inf", max_length=255, null=True, blank=True)
    ext_capot = models.CharField("Capot", max_length=255, null=True, blank=True)
    ext_ceinture_sécurité = models.CharField("Ceinture de sécurité", max_length=255, null=True, blank=True)
    ext_etat_peinture = models.CharField("Etat peinture", max_length=255, null=True, blank=True)
    ext_extincteur = models.CharField("Extincteur", max_length=255, null=True, blank=True)
    ext_fixation_bouteille_gaz = models.CharField("Fixation bouteille à gaz", max_length=255, null=True, blank=True)
    ext_grille_protection_feux_ar = models.CharField("Grille de protection des feux AR", max_length=255, null=True, blank=True)
    ext_grille_protection_feux_av = models.CharField("Grille de protection des feux AV", max_length=255, null=True, blank=True)
    ext_plexiglass_parebrise = models.CharField("Plexiglass / pare brise", max_length=255, null=True, blank=True)
    ext_prenettoyeur_prefiltre_air = models.CharField("Prenettoyeur / prefiltre à air", max_length=255, null=True, blank=True)
    ext_proprete_engin = models.CharField("Propreté engin", max_length=255, null=True, blank=True)
    ext_protege_échappement = models.CharField("Protège échappement", max_length=255, null=True, blank=True)
    ext_rétroviseurs = models.CharField("Rétroviseurs", max_length=255, null=True, blank=True)
    ext_robinet_bouteille_gaz = models.CharField("Robinet de bouteille à gaz", max_length=255, null=True, blank=True)
    ext_roulement_colonne_direction = models.CharField("Roulement colonne direction", max_length=255, null=True, blank=True)
    ext_securite_siege = models.CharField("Sécurité du siège", max_length=255, null=True, blank=True)
    ext_siege = models.CharField("Siège", max_length=255, null=True, blank=True)
    ext_tampon_pedale = models.CharField("Tampon pédale", max_length=255, null=True, blank=True)
    ext_tampon_plancher = models.CharField("Tampon plancher", max_length=255, null=True, blank=True)
    ext_vérin_capot = models.CharField("Vérin du capot", max_length=255, null=True, blank=True)



class FcMnCoMarche(models.Model):

    comarche_approche_lente = models.CharField("Approche lente", max_length=255, null=True, blank=True)
    comarche_couvercle_bocal_huile_frein = models.CharField("Couvercle du bocal huile de frein", max_length=255, null=True, blank=True)
    comarche_frein_stationnement = models.CharField("Frein de stationnement", max_length=255, null=True, blank=True)
    comache_freinage_pied = models.CharField("Freinage à pied", max_length=255, null=True, blank=True)
    comarche_jeu_pedale_embrayage = models.CharField("Jeu de pédale d'embrayage", max_length=255, null=True, blank=True)
    comarche_maitre_cylindre_frein = models.CharField("Maitre cylindre de frein", max_length=255, null=True, blank=True)
    comarche_ressort_rappel_embrayage_frein = models.CharField("Ressort de rappel d'embrayage / frein", max_length=255, null=True, blank=True)
    comarche_tuyauterie_flexible_rigide_freins = models.CharField("Tuyauterie flexible et rigide des freins", max_length=255, null=True, blank=True)
    comarche_valve_commande_embrayage = models.CharField("Valve de commande embrayage", max_length=255, null=True, blank=True)



class FcMnCoMoteur(models.Model):

    comoteur_buse_air_radiateur = models.CharField("Buse d'air du radiateur", max_length=255, null=True, blank=True)
    comoteur_cardan_sortie_bvPont = models.CharField("Cardan sortie BV-Pont", max_length=255, null=True, blank=True)
    comoteur_courroie_ventilateur = models.CharField("Courroie de ventilateur", max_length=255, null=True, blank=True)
    comoteur_durites_refroidissement_supinf = models.CharField("Durites de refroidissement sup et inf", max_length=255, null=True, blank=True)
    comoteur_etat_poulie_alternateur = models.CharField("Etat poulie d'alternateur", max_length=255, null=True, blank=True)
    comoteur_evaporateur = models.CharField("Evaporateur", max_length=255, null=True, blank=True)
    comoteur_filtre_air = models.CharField("Filtre à air", max_length=255, null=True, blank=True)
    comoteur_filtre_gaz = models.CharField("Filtre à gaz", max_length=255, null=True, blank=True)
    comoteur_fumee = models.CharField("Fumée", max_length=255, null=True, blank=True)
    comoteur_jauge_huile_bv = models.CharField("Jauge d'huile de BV", max_length=255, null=True, blank=True)
    comoteur_jauge_huile_hydraulique = models.CharField("Jauge d'huile de hydraulique", max_length=255, null=True, blank=True)
    comoteur_jauge_huile_moteur = models.CharField("Jauge d'huile moteur", max_length=255, null=True, blank=True)
    comoteur_pompe_eau = models.CharField("Pompe à eau", max_length=255, null=True, blank=True)
    comoteur_pompette_carburant = models.CharField("Pompette à carburant", max_length=255, null=True, blank=True)
    comoteur_refroidisseur_huile_hydraulique = models.CharField("Refroidisseur d'huile hydraulique", max_length=255, null=True, blank=True)
    comoteur_reservoir_huile_hydraulique = models.CharField("Reservoir d'huile hydraulique", max_length=255, null=True, blank=True)
    comoteur_supports_moteur = models.CharField("Supports moteur", max_length=255, null=True, blank=True)
    comoteur_tringlerie_accélérateur = models.CharField("Tringlerie d'accélérateur", max_length=255, null=True, blank=True)
    comoteur_tuyau_echappement = models.CharField("Tuyau échappement", max_length=255, null=True, blank=True)
    comoteur_ventilateur = models.CharField("Ventilateur", max_length=255, null=True, blank=True)



class FcMnLev(models.Model):

    equiplev_amortisseurs_fourches = models.CharField("Amortisseurs des fourches", max_length=255, null=True, blank=True)
    equiplev_ancrage_chaînes = models.CharField("Ancrage des chaînes", max_length=255, null=True, blank=True)
    equiplev_bandes_appuies = models.CharField("Bandes d'appuies", max_length=255, null=True, blank=True)
    equiplev_barres_profilees = models.CharField("Barres profilées", max_length=255, null=True, blank=True)
    equiplev_chaine_levage = models.CharField("Chaîne de levage", max_length=255, null=True, blank=True)
    equiplev_distributeur = models.CharField("Distributeur", max_length=255, null=True, blank=True)
    equiplev_etat_tablier = models.CharField("Etat du tablier", max_length=255, null=True, blank=True)
    equiplev_fixation_mat_presse = models.CharField("Fixation mât de presse", max_length=255, null=True, blank=True)
    equiplev_fixation_mat_telescopie = models.CharField("Fixation mât de télescopie", max_length=255, null=True, blank=True)
    equiplev_fourches = models.CharField("Fourches", max_length=255, null=True, blank=True)
    equiplev_galets_chaine = models.CharField("Galets de chaîne", max_length=255, null=True, blank=True)
    equiplev_galets_mat = models.CharField("Galets de mât", max_length=255, null=True, blank=True)
    equiplev_galets_tablier = models.CharField("Galets de tablier", max_length=255, null=True, blank=True)
    equiplev_garnitures_plateau_presseur = models.CharField("Garnitures du plateau presseur", max_length=255, null=True, blank=True)
    equiplev_manette_commande = models.CharField("Manette de commande", max_length=255, null=True, blank=True)
    equiplev_plateau_presse = models.CharField("Plateau de presse", max_length=255, null=True, blank=True)
    equiplev_poulies_teflon = models.CharField("Poulies en téflon", max_length=255, null=True, blank=True)
    equiplev_poulies_guide_chaines = models.CharField("Poulies guide chaînes", max_length=255, null=True, blank=True)
    equiplev_rouleau_translateur = models.CharField("Rouleau du translateur", max_length=255, null=True, blank=True)
    equiplev_taquet_mat_presse = models.CharField("Taquet de mat de presse", max_length=255, null=True, blank=True)
    equiplev_tension_chaînes = models.CharField("Tension des chaînes", max_length=255, null=True, blank=True)
    equiplev_tuyau_metallique = models.CharField("Tuyau métallique", max_length=255, null=True, blank=True)
    equiplev_verin_ecartement_fourches = models.CharField("Vérin d'écartement de fourches", max_length=255, null=True, blank=True)
    equiplev_verin_inclinaison = models.CharField("Vérin d'inclinaison", max_length=255, null=True, blank=True)
    equiplev_verin_levage_central = models.CharField("Vérin de levage central", max_length=255, null=True, blank=True)
    equiplev_verin_levage_latéral_droit = models.CharField("Vérin de levage latéral droit", max_length=255, null=True, blank=True)
    equiplev_verin_levage_latéral_gauche = models.CharField("Vérin de levage latéral gauche", max_length=255, null=True, blank=True)
    equiplev_verin_presse = models.CharField("Vérin de presse", max_length=255, null=True, blank=True)
    equiplev_verin_translation = models.CharField("Vérin de translation", max_length=255, null=True, blank=True)



class FcMnFuite(models.Model):

    fuite_boitier_direction = models.CharField("Boitier de direction", max_length=255, null=True, blank=True)
    fuite_circuit_alimentation_gaz = models.CharField("Circuit d'alimentation en gaz", max_length=255, null=True, blank=True)
    fuite_circuit_aspiration_air = models.CharField("Circuit d'aspiration d'air", max_length=255, null=True, blank=True)
    fuite_eau_refroidissement = models.CharField("Eau de refroidissement", max_length=255, null=True, blank=True)
    fuite_electrolyte_batterie = models.CharField("Electrolyte batterie", max_length=255, null=True, blank=True)
    fuite_etancheite_radiateur = models.CharField("étanchéité radiateur", max_length=255, null=True, blank=True)
    fuite_gasoil = models.CharField("Gas-oil", max_length=255, null=True, blank=True)
    fuite_gaz_echappement = models.CharField("Gaz d'échappement", max_length=255, null=True, blank=True)
    fuite_huile_freins = models.CharField("Huile de freins", max_length=255, null=True, blank=True)
    fuite_huile_transmission = models.CharField("Huile de transmission", max_length=255, null=True, blank=True)
    fuite_huile_hydraulique = models.CharField("Huile hydraulique", max_length=255, null=True, blank=True)
    fuite_huile_moteur = models.CharField("Huile moteur", max_length=255, null=True, blank=True)



class FcMnNiveau(models.Model):

    niveaux_eau_refroidissement = models.CharField("Eau de refroidissement", max_length=255, null=True, blank=True)
    niveaux_huile_frein = models.CharField("Huile de frein", max_length=255, null=True, blank=True)
    niveaux_huile_transmission = models.CharField("Huile de transmission", max_length=255, null=True, blank=True)
    niveaux_huile_hydraulique = models.CharField("Huile hydraulique", max_length=255, null=True, blank=True)
    niveaux_huile_moteur = models.CharField("Huile moteur", max_length=255, null=True, blank=True)



class FcMnElec(models.Model):

    elec_allumeur = models.CharField("Allumeur", max_length=255, null=True, blank=True)
    elec_avertisseur_sonore_recul = models.CharField("Avertisseur sonore de recul", max_length=255, null=True, blank=True)
    elec_boîte_fusibles = models.CharField("Boîte à fusibles", max_length=255, null=True, blank=True)
    elec_bougie_prechauffage = models.CharField("Bougie de préchauffage", max_length=255, null=True, blank=True)
    elec_bouton_commande_translateur = models.CharField("Bouton de commande du translateur", max_length=255, null=True, blank=True)
    elec_branchement_cables = models.CharField("Branchement des câbles (AL)", max_length=255, null=True, blank=True)
    elec_bruit_demarreur = models.CharField("Bruit démarreur", max_length=255, null=True, blank=True)
    elec_bruit_roulements = models.CharField("Bruit des roulements (AL)", max_length=255, null=True, blank=True)
    elec_cable_alimentation_demarreur = models.CharField("Câble d'alimentation démarreur", max_length=255, null=True, blank=True)
    elec_cable_batterie = models.CharField("Câble de batterie", max_length=255, null=True, blank=True)
    elec_cable_commande_translateur = models.CharField("Câble de commande translateur", max_length=255, null=True, blank=True)
    elec_chapeau_allumeur = models.CharField("Chapeau d'allumeur", max_length=255, null=True, blank=True)
    elec_commodo_phare = models.CharField("Commodo de phare", max_length=255, null=True, blank=True)
    elec_compteur_horaire = models.CharField("Compteur horaire", max_length=255, null=True, blank=True)
    elec_contacteur_cle = models.CharField("Contacteur à clé", max_length=255, null=True, blank=True)
    elec_cosses_batterie = models.CharField("Cosses de batterie", max_length=255, null=True, blank=True)
    elec_densite_electrolyte = models.CharField("Densité électrolyte", max_length=255, null=True, blank=True)
    elec_faisceau_bord = models.CharField("Faisceau de bord", max_length=255, null=True, blank=True)
    elec_faisceau_moteur = models.CharField("Faisceau moteur", max_length=255, null=True, blank=True)
    elec_feu_clignotant_ard = models.CharField("Feu clignotant ARD", max_length=255, null=True, blank=True)
    elec_feu_clignotant_arg = models.CharField("Feu clignotant ARG", max_length=255, null=True, blank=True)
    elec_feu_clignotant_avd = models.CharField("Feu clignotant AVD", max_length=255, null=True, blank=True)
    elec_feu_clignotant_avg = models.CharField("Feu clignotant AVG", max_length=255, null=True, blank=True)
    elec_feux_ard = models.CharField("Feux ARD", max_length=255, null=True, blank=True)
    elec_fEUX_arg = models.CharField("FEUX ARG", max_length=255, null=True, blank=True)
    elec_feux_recul = models.CharField("Feux de recul", max_length=255, null=True, blank=True)
    elec_fil_bougie_haute_tension = models.CharField("Fil de bougie haute tension", max_length=255, null=True, blank=True)
    elec_fixation_alternateur = models.CharField("Fixation alternateur", max_length=255, null=True, blank=True)
    elec_fixation_batterie = models.CharField("Fixation batterie", max_length=255, null=True, blank=True)
    elec_fixation_demarreur = models.CharField("Fixation démarreur", max_length=255, null=True, blank=True)
    elec_fixation_faisceau_electrique = models.CharField("Fixation faisceau électrique", max_length=255, null=True, blank=True)
    elec_fusibles = models.CharField("Fusibles", max_length=255, null=True, blank=True)
    elec_gyrophare = models.CharField("Gyrophare", max_length=255, null=True, blank=True)
    elec_inverseur_marche = models.CharField("Inverseur de marche", max_length=255, null=True, blank=True)
    elec_isolation_cables = models.CharField("Isolation des câbles (AL)", max_length=255, null=True, blank=True)
    elec_klaxon = models.CharField("Klaxon", max_length=255, null=True, blank=True)
    elec_mano_huile = models.CharField("Mano d'huile", max_length=255, null=True, blank=True)
    elec_mano_temperature_eau = models.CharField("Mano de température d'eau", max_length=255, null=True, blank=True)
    elec_phare_avd = models.CharField("Phare AVD", max_length=255, null=True, blank=True)
    elec_phare_avg= models.CharField("Phare AVG", max_length=255, null=True, blank=True)
    elec_projecteur_ar = models.CharField("Projecteur AR", max_length=255, null=True, blank=True)
    elec_relais_prechauffage = models.CharField("Relais de préchauffage", max_length=255, null=True, blank=True)
    elec_solenoides_marche_av_ar = models.CharField("Solénoides de marche AV et AR", max_length=255, null=True, blank=True)
    elec_tableau_bord = models.CharField("Tableau de bord", max_length=255, null=True, blank=True)
    elec_taux_charge  = models.CharField("Taux de charge (AL)", max_length=255, null=True, blank=True) 
    elec_tension_etat_courroie = models.CharField("Tension / état de la courroie (AL)", max_length=255, null=True, blank=True)



class FcMnEssieu(models.Model):

    ess_Axes_fusee = models.CharField("Axes de fusée", max_length=255, null=True, blank=True)
    ess_Bague_moyeu = models.CharField("Bague de moyeu", max_length=255, null=True, blank=True)
    ess_Bague_trompette_av  = models.CharField("Bague de trompette AV", max_length=255, null=True, blank=True)
    ess_Biellette_direction_d = models.CharField("Biellette de direction D", max_length=255, null=True, blank=True)
    ess_Biellette_direction_g = models.CharField("Biellette de direction G", max_length=255, null=True, blank=True)
    ess_Butee_aiguilles = models.CharField("Butée à aiguilles", max_length=255, null=True, blank=True)
    ess_Capuchon_moyeu_roue = models.CharField("Capuchon de moyeu de roue", max_length=255, null=True, blank=True)
    ess_Ecrous_roue_ar = models.CharField("Ecrous de roue AR", max_length=255, null=True, blank=True)
    ess_Ecrous_roue_av = models.CharField("Ecrous de roue Av", max_length=255, null=True, blank=True)
    ess_etats_tambours = models.CharField("états des tambours", max_length=255, null=True, blank=True)
    ess_Flexible_verin_direction = models.CharField("Flexible de vérin de direction", max_length=255, null=True, blank=True)
    ess_Fusee_ard = models.CharField("Fusée ARD", max_length=255, null=True, blank=True)
    ess_Fusee_arg = models.CharField("Fusée ARG", max_length=255, null=True, blank=True)
    ess_Goujons_roue_ar = models.CharField("Goujons de roue AR", max_length=255, null=True, blank=True)
    ess_Goujons_roue_av = models.CharField("Goujons de roue AV", max_length=255, null=True, blank=True)
    ess_Graisseurs = models.CharField("Graisseurs", max_length=255, null=True, blank=True)
    ess_Jante_ar = models.CharField("Jante AR - état", max_length=255, null=True, blank=True)
    ess_Jante_av = models.CharField("Jante AV - état", max_length=255, null=True, blank=True)
    ess_Moyeu_ar = models.CharField("Moyeu AR (état, jeu)", max_length=255, null=True, blank=True)
    ess_Moyeu_av = models.CharField("Moyeu AV (état, jeu)", max_length=255, null=True, blank=True)
    ess_Pneumatique_ar = models.CharField("Pneumatique AR", max_length=255, null=True, blank=True)
    ess_Pneumatique_av = models.CharField("Pneumatique AV", max_length=255, null=True, blank=True)
    ess_Pression_pneus = models.CharField("Pression des pneus", max_length=255, null=True, blank=True)
    ess_Roulement_moyeu_ar = models.CharField("Roulement de moyeu AR (état)", max_length=255, null=True, blank=True)
    ess_Roulement_moyeu_av = models.CharField("Roulement de moyeu AV (état)", max_length=255, null=True, blank=True)
    ess_Silentbloc_fixation_essieu = models.CharField("Silentbloc de fixation de l'essieu", max_length=255, null=True, blank=True)
    ess_Tampon_choc = models.CharField("Tampon choc", max_length=255, null=True, blank=True)
    ess_Usure_paliers = models.CharField("Usure des paliers", max_length=255, null=True, blank=True)
    ess_Verin_direction = models.CharField("Vérin de direction", max_length=255, null=True, blank=True)



class FcMnHydrau(models.Model):

    hydrau_Flexible_levage = models.CharField("Flexible de levage", max_length=255, null=True, blank=True)
    hydrau_Flexibles_bouteille_gaz = models.CharField("Flexibles de bouteille à gaz", max_length=255, null=True, blank=True)
    hydrau_Flexibles_distributeur = models.CharField("Flexibles de distributeur", max_length=255, null=True, blank=True)
    hydrau_Flexibles_presse = models.CharField("Flexibles de presse", max_length=255, null=True, blank=True)
    hydrau_Flexibles_refroidissement = models.CharField("Flexibles de refroidissement", max_length=255, null=True, blank=True)
    hydrau_Flexibles_translation = models.CharField("Flexibles de translation", max_length=255, null=True, blank=True)
    hydrau_Repartiteur_huile = models.CharField("Repartiteur d'huile", max_length=255, null=True, blank=True)



# PROFILE FICHE DE CONTROLE POUR POIDS LOURDS


class FcPlCabine(models.Model):

    cabine_balais_essuie_glace = models.CharField("Balais Essuie-glace", max_length=255, null=True, blank=True)
    cabine_panneau_portiere = models.CharField("Panneau portièère", max_length=255, null=True, blank=True)
    cabine_pare_brise = models.CharField("Pare-brise", max_length=255, null=True, blank=True)
    cabine_retroviseurs_ext = models.CharField("Rétroviseurs ext.", max_length=255, null=True, blank=True)



class FcPlCarrosserie(models.Model):

    carros_aile_droite = models.CharField("Aile droite", max_length=255, null=True, blank=True)
    carros_aile_gauche = models.CharField("Aile gauche", max_length=255, null=True, blank=True)
    carros_capot_moteur = models.CharField("Capot moteur", max_length=255, null=True, blank=True)
    carros_fixation_caisse_ar = models.CharField("Fixation caisse AR", max_length=255, null=True, blank=True)
    carros_mecanismes_leve_vitres = models.CharField("Mécanismes lève-vitres", max_length=255, null=True, blank=True)
    carros_pare_choc_ar = models.CharField("Pare choc AR", max_length=255, null=True, blank=True)
    carros_pare_choc_av = models.CharField("Pare choc AV", max_length=255, null=True, blank=True)
    carros_plateur_brasseur = models.CharField("Plateur brasseur", max_length=255, null=True, blank=True)
    carros_poignees_ouverture_ext = models.CharField("Poignées d'ouverture ext", max_length=255, null=True, blank=True)
    carros_poignees_ouverture_int = models.CharField("Poignées d'ouverture int", max_length=255, null=True, blank=True)
    carros_portiere_avd = models.CharField("Portière AV/D", max_length=255, null=True, blank=True)
    carros_portiere_avg = models.CharField("Portière AV/G", max_length=255, null=True, blank=True)
    carros_pose_pied = models.CharField("Pose pied", max_length=255, null=True, blank=True)
    carros_ridelles = models.CharField("Ridelles", max_length=255, null=True, blank=True)
    carros_vitrages = models.CharField("Vitrages", max_length=255, null=True, blank=True)



class FcPlMoteur(models.Model):

    comoteur_circuit_carburant = models.CharField("Circuit carburant", max_length=255, null=True, blank=True)
    comoteur_circuit_refroidissement = models.CharField("Circuit refroidissement", max_length=255, null=True, blank=True)
    comoteur_courroie_ventilateur = models.CharField("Courroie de ventilateur", max_length=255, null=True, blank=True)
    comoteur_courroies_compresseur = models.CharField("Courroies de compresseur", max_length=255, null=True, blank=True)
    comoteur_filtre_air = models.CharField("Filtre à air", max_length=255, null=True, blank=True)
    comoteur_fuites_direction_assistée = models.CharField("Fuites direction assistée", max_length=255, null=True, blank=True)
    comoteur_fumee = models.CharField("Fumée", max_length=255, null=True, blank=True)



class FcPlElec(models.Model):

    elec_clignotants = models.CharField("Clignotants", max_length=255, null=True, blank=True)
    elec_eclairage_ar = models.CharField("Eclairage AR", max_length=255, null=True, blank=True)
    elec_eclairage_av = models.CharField("Eclairage AV", max_length=255, null=True, blank=True)
    elec_feu_stop = models.CharField("Feu stop", max_length=255, null=True, blank=True)
    elec_plaque = models.CharField("Plaque", max_length=255, null=True, blank=True)


class FcPlEssai(models.Model):

    essai_bruits = models.CharField("Bruits", max_length=255, null=True, blank=True)
    essai_demarreur = models.CharField("Démarreur", max_length=255, null=True, blank=True)
    essai_embrayage = models.CharField("Embrayage", max_length=255, null=True, blank=True)
    essai_equilibrage_roues = models.CharField("Equilibrage roues", max_length=255, null=True, blank=True)
    essai_freinage = models.CharField("Freinage", max_length=255, null=True, blank=True)
    essai_tenue_route = models.CharField("Tenue de route", max_length=255, null=True, blank=True)





class FcPlInter(models.Model):

    intern_arret_moteur = models.CharField("Arrêt moteur", max_length=255, null=True, blank=True)
    intern_commodo_eclairage_avert = models.CharField("Commodo éclairage/avert", max_length=255, null=True, blank=True)
    intern_commodo_essuie_vitres = models.CharField("Commodo essuie-vitres", max_length=255, null=True, blank=True)
    intern_compteur_horaire = models.CharField("Compteur horaire", max_length=255, null=True, blank=True)
    intern_embrayage_Emetteur = models.CharField("Embrayage / Emetteur", max_length=255, null=True, blank=True)
    intern_frein_main = models.CharField("Frein à main", max_length=255, null=True, blank=True)
    intern_frein_pied = models.CharField("Frein à pied", max_length=255, null=True, blank=True)
    intern_instruments_bord = models.CharField("Instruments de bord", max_length=255, null=True, blank=True)
    intern_levier_vitesse = models.CharField("Levier de vitesse", max_length=255, null=True, blank=True)
    intern_pedale_accelerateur = models.CharField("Pédale accélérateur", max_length=255, null=True, blank=True)
    intern_siege_chauffeur = models.CharField("Siège chauffeur", max_length=255, null=True, blank=True)
    intern_siege_passager = models.CharField("Siège passager", max_length=255, null=True, blank=True)



class FcPlNiveau(models.Model):

    Eau_refroidissement = models.CharField("Eau de refroidissement", max_length=255, null=True, blank=True)
    Electrolyte_batterie = models.CharField("Electrolyte batterie", max_length=255, null=True, blank=True)
    Huile_direction = models.CharField("Huile de direction", max_length=255, null=True, blank=True)
    Huile_frein = models.CharField("Huile de frein", max_length=255, null=True, blank=True)
    Huile_moteur = models.CharField("Huile moteur", max_length=255, null=True, blank=True)
    Lave_glace = models.CharField("Lave-glace", max_length=255, null=True, blank=True)
    Réservoir_air = models.CharField("Réservoir d'air", max_length=255, null=True, blank=True)

class FcPlSousveh(models.Model):
 
    Amortisseurs_av = models.CharField("Amortisseurs AV", max_length=255, null=True, blank=True)
    Canalisations_carburant = models.CharField("Canalisations carburant", max_length=255, null=True, blank=True)
    Canalisations_freinage = models.CharField("Canalisations freinage", max_length=255, null=True, blank=True)
    Echappement = models.CharField("Echappement", max_length=255, null=True, blank=True)
    Etats_pneus = models.CharField("Etats pneus", max_length=255, null=True, blank=True)
    Etoquiaux = models.CharField("Etoquiaux", max_length=255, null=True, blank=True)
    Freinage_ar = models.CharField("Freinage AR", max_length=255, null=True, blank=True)
    Freinage_av = models.CharField("Freinage AV", max_length=255, null=True, blank=True)
    Fuite_boite_transfert = models.CharField("Fuite boîte de transfert", max_length=255, null=True, blank=True)
    Fuites_bv = models.CharField("Fuites BV", max_length=255, null=True, blank=True)
    Fuites_moteur = models.CharField("Fuites moteur", max_length=255, null=True, blank=True)
    Fusee = models.CharField("Fusée", max_length=255, null=True, blank=True)
    Piedestal = models.CharField("Piédestal", max_length=255, null=True, blank=True)
    Poumon = models.CharField("Poumon", max_length=255, null=True, blank=True)
    Pression_pneu = models.CharField("Pression pneu", max_length=255, null=True, blank=True)
    Récepteur_embrayage = models.CharField("Récepteur d'embrayage", max_length=255, null=True, blank=True)
    Ressorts_ar = models.CharField("Ressorts AR", max_length=255, null=True, blank=True)
    Ressorts_av = models.CharField("Ressorts AV", max_length=255, null=True, blank=True)
    Serrage_roues = models.CharField("Serrage des roues", max_length=255, null=True, blank=True)
    Transmission_ar = models.CharField("Transmission AR", max_length=255, null=True, blank=True)
    Transmission_ar_Cardan = models.CharField("Transmission AV / Cardan", max_length=255, null=True, blank=True)








class FCtrl(models.Model):

    TRAVAUX = [
        ('EP', 'EP'),
        ('CURATIVE', 'CURATIVE'),
        ('CORRECTIVE', 'CORRECTIVE'),
        ('INSPECTION', 'INSPECTION'),
    ]


    vehicule = models.ForeignKey(VehiculesEses, on_delete=models.SET_NULL, null=True, related_name='veh_fc_mn')
    dtep = models.ForeignKey(DTPrev, on_delete=models.SET_NULL, null=True, blank=True, related_name="dtep_fc")
    dtcur = models.ForeignKey(DTCurative, on_delete=models.SET_NULL, null=True, blank=True, related_name="dtcur_fc")
    date_ctrl = models.DateField(auto_now_add=True)
    maintenance = models.CharField(max_length=50, blank=True, null=True, choices=TRAVAUX)
    garagiste = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='gar_fc_mn')
    # PROFILE FICHE CONTROLE POUR ENGIN MANUTENTION
    fc_mn_ext = models.OneToOneField(FcMnExt, on_delete=models.CASCADE, null=True, blank=True, related_name="mn_exterieur")
    fc_mn_comarche = models.OneToOneField(FcMnCoMarche, on_delete=models.CASCADE, null=True, blank=True, related_name="mn_marche")
    fc_mn_comoteur = models.OneToOneField(FcMnCoMoteur, on_delete=models.CASCADE, null=True, blank=True, related_name="mn_moteur")
    fc_mn_levage = models.OneToOneField(FcMnLev, on_delete=models.CASCADE, null=True, blank=True, related_name="mn_levage")
    fc_mn_fuite = models.OneToOneField(FcMnFuite, on_delete=models.CASCADE, null=True, blank=True, related_name="mn_fuite")
    fc_mn_niveau = models.OneToOneField(FcMnNiveau, on_delete=models.CASCADE, null=True, blank=True, related_name="mn_niveau")
    fc_mn_elec = models.OneToOneField(FcMnElec, on_delete=models.CASCADE, null=True, blank=True, related_name="mn_elec")
    fc_mn_essieu = models.OneToOneField(FcMnEssieu, on_delete=models.CASCADE, null=True, blank=True, related_name="mn_essieu")
    fc_mn_hydrau = models.OneToOneField(FcMnHydrau, on_delete=models.CASCADE, null=True, blank=True, related_name="mn_hydrau")
    # PROFILE FICHE CONTROLE POUR POIDS LOURDS
    fc_pl_cabine = models.OneToOneField(FcPlCabine, on_delete=models.CASCADE, null=True, blank=True, related_name="pl_cabine")
    fc_pl_carros = models.OneToOneField(FcPlCarrosserie, on_delete=models.CASCADE, null=True, blank=True, related_name="pl_carros")
    fc_pl_moteur = models.OneToOneField(FcPlMoteur, on_delete=models.CASCADE, null=True, blank=True, related_name="pl_moteur")
    fc_pl_elec = models.OneToOneField(FcPlElec, on_delete=models.CASCADE, null=True, blank=True, related_name="pl_elec")
    fc_pl_essai = models.OneToOneField(FcPlEssai, on_delete=models.CASCADE, null=True, blank=True, related_name="pl_essai")
    fc_pl_interne = models.OneToOneField(FcPlInter, on_delete=models.CASCADE, null=True, blank=True, related_name="pl_interne")
    fc_pl_niveau = models.OneToOneField(FcPlNiveau, on_delete=models.CASCADE, null=True, blank=True, related_name="pl_niveau")
    fc_pl_sousveh = models.OneToOneField(FcPlSousveh, on_delete=models.CASCADE, null=True, blank=True, related_name="pl_sousveh")











    

    

  

    
