from django.db.models.signals import post_save
from .models import UserAccount 
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.contrib.auth.models import Group
from guardian.shortcuts import assign_perm
from MatRoulant.models import VehiculesEses
from CompteurApps.models import AlerteEp


User = get_user_model()

@receiver(post_save, sender=UserAccount)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        user = User.objects.get(email=instance.email)
        if instance.type == "CHEF_SMRLT":
            
            assign_perm("MatRoulant.view_vehiculeseses", user, VehiculesEses.objects.filter(site_matrlt=user.site))
            assign_perm("MatRoulant.change_vehiculeseses", user, VehiculesEses.objects.filter(site_matrlt=user.site))
            assign_perm("MatRoulant.delete_vehiculeseses", user, VehiculesEses.objects.filter(site_matrlt=user.site))
            assign_perm("MatRoulant.add_vehiculeseses", user, VehiculesEses.objects.filter(site_matrlt=user.site))

            

        elif instance.type == "CHEF_REGION" or instance.type == "CHEF_AGENCE" or instance.type == "CHEF_CTECH" or instance.type == "CHEF_SITE" or instance.type == "DIR_OPER":
            assign_perm("MatRoulant.view_vehiculeseses", user, VehiculesEses.objects.filter(affectation__in=user.site))
            

        elif instance.type == "DIR_EXPLOIT" or instance.type == "MASTER_DATA" or instance.type == "DIR_GEN":
            assign_perm("MatRoulant.view_vehiculeseses", user, VehiculesEses.objects.all())
            assign_perm("MatRoulant.change_vehiculeseses", user, VehiculesEses.objects.all())
            assign_perm("MatRoulant.delete_vehiculeseses", user, VehiculesEses.objects.all())
            assign_perm("MatRoulant.add_vehiculeseses", user, VehiculesEses.objects.all())

            

        elif instance.type == "UTILISATEUR":
            task = [veh for veh in VehiculesEses.objects.all() if user in veh.conducteurs]
            assign_perm("MatRoulant.view_vehiculeseses", user, task)
            assign_perm("MatRoulant.change_vehiculeseses", user, task)
            