
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
                    data_alert["nbalert"] = lastg.nbalert + 1
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
