from celery import shared_task
from time import sleep

@shared_task
def notif_client(message):
    print("Transfert de 10.000 emails....")
    sleep(5)
    print("Les emails ont été envoyé avec succès")


# @shared_task
# def check_abonnement(instance):
#     print(instance)
    # if instance.is_valid == True:
    #     codeabonne = CodeAbonne.objects.filter(code_ab=instance.code_ese).first()
    #     client = Clients.objects.filter(id_enreg=codeabonne.ese_id).first()
    #     print("Le code d'abonnement est "+ str(client.code))
    #     # client.ese_activate = False
    #     # client.save()

