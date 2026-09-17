from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from MatRoulant.models import VehiculesEses, AssurVeh, CGVeh, VisiteVeh
from Entreprise.models import Eses, AbonnementEse
from decimal import Decimal
from Parameters.paramserializer import ParamComptAlertSerializer



@receiver(post_save, sender=VehiculesEses)
def CreateTenant(sender, instance, created, **kwargs):
    if created:
        AssurVeh.objects.create(vehicule=instance)
        VisiteVeh.objects.create(vehicule=instance)
        CGVeh.objects.create(vehicule=instance)

        param_alert = {}
        cat = instance.categorie
        
        schema_name = str(instance.identite).split('_')[0].lower()
        code = AbonnementEse.objects.filter(schema_name=schema_name).first().code
        list_categ = [('PL1', 130.0), ('PL2', 9500.0), ('VL', 4700.0), ('VT', 4700.0), ('MN', 230.0), ('GC', 230.0)]
        for categ in list_categ:
            if categ[0] == cat:
                param_alert['schema_name'] = schema_name
                param_alert['code_ese'] = code
                param_alert['vehicule'] = str(instance.immat)
                param_alert['alert'] = Decimal(categ[1])
                param_alert['categorie'] = categ[0]
                param_alert['observations'] = ""

                serializer = ParamComptAlertSerializer(data=param_alert)
                serializer.is_valid(raise_exception=True)
                serializer.save()



        
