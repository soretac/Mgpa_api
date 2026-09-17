from django.db import models



class ParamComptAlert(models.Model):
    
    schema_name = models.CharField(max_length=50, null=True, blank=True)
    code_ese = models.CharField(max_length=250, null=True, blank=True)
    categorie = models.CharField(max_length=50, null=True, blank=True)
    vehicule = models.CharField(max_length=255, null=True, blank=True) # pour des véhicules particuliers
    alert = models.DecimalField(max_digits=10, decimal_places=1, blank=True)
    observations = models.TextField(null=True, blank=True)
    # alert_temp = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.sigle_ese} - {self.categorie} - {self.alert}"


class Prestatons(models.Model):
    code_prest = models.CharField(max_length=255, null=True, blank=True)
    libelle_prest = models.CharField(max_length=255)
    organe = models.CharField(max_length=255, null=True, blank=True)  
    duree_prest = models.IntegerField()
    montant_prest = models.IntegerField()

    def __str__(self):
        return f"{self.libelle_prest} - {self.organe} - {self.duree_prest}"
    

class PieceRechange(models.Model):
    code_art = models.CharField(max_length=255, null=True, blank=True)
    libelle_art  = models.CharField(max_length=255, null=True, blank=True)
    prix_art  = models.IntegerField()
    ref_usine = models.CharField(max_length=255, null=True, blank=True)
    cat_art = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.libelle_art} - {self.cat_art} - {self.ref_usine} - {self.prix_art}"


