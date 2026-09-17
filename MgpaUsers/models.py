from django.db import models
from Entreprise.models import Organigramme
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, AbstractUser
from django.utils.timezone import now
from django.contrib.auth.models import Group


class UserAccountManager(BaseUserManager):
    def _create_user(self, email, username, password, first_name, last_name, matricule, mobile, type, poste, site, date_nais, genre, matrimonial, address, avatar,  permis, num_cni, signature, **extra_fields):
        if not email:
            raise ValueError("Vous devez fournir une adresse mail")
        if not password:
            raise ValueError('Vous devez fournir un mot de passe')
        
       

        UserAccount = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
            matricule = matricule,
            mobile = mobile,
            type = type,
            poste = poste,
            site = site,
            date_nais = date_nais, 
            genre = genre,
            matrimonial = matrimonial,
            address = address,
            avatar = avatar, 
            permis = permis, 
            num_cni = num_cni,  
            signature = signature,
           
            **extra_fields
        )

        UserAccount.set_password(password)
        UserAccount.save(using=self._db)
        
        
        return UserAccount

    def create_user(self, email, username, password, first_name, last_name, matricule, mobile, type, poste, site, date_nais, genre, matrimonial, address, avatar,  permis, num_cni, signature, **extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('is_superuser',False)
        return self._create_user(email, username, password, first_name, last_name, matricule, mobile, type, poste, site, date_nais, genre, matrimonial, address, avatar,  permis, num_cni, signature, **extra_fields)

    def create_superuser(self, email, username, password, first_name, last_name, matricule, mobile, type, poste, site, date_nais, genre, matrimonial, address, avatar,  permis, num_cni, signature, **extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('is_superuser',True)
        return self._create_user(email, username, password, first_name, last_name, matricule, mobile, type, poste, site, date_nais, genre, matrimonial, address, avatar,  permis, num_cni, signature, **extra_fields)






class UserAccount(AbstractUser, PermissionsMixin):
    users_types = {
        ("UTILISATEUR", "UTILISATEUR"),
        ("GARAGISTE", "GARAGISTE"),
        ("MAGASINIER", "MAGASINIER"),
        ("CHEF_SITE", "CHEF_SITE"),
        ("CHEF_CTECH", "CHEF_CTECH"),
        ("CHEF_AGENCE", "CHEF_AGENCE"),
        ("CHEF_REGION", "CHEF_REGION"),
        ("CHEF_SMRLT", "CHEF_SMRLT"),
        ("DIR_EXPLOIT", "DIR_EXPLOIT"),
        ("DIR_OPER", "DIR_OPER"),
        ("MASTER_DATA", "MASTER_DATA"),
        ("DIR_GEN", "DIR_GEN"),
        
    }

    GENRES = {
        ('MASCULIN', 'MASCULIN'),
        ('FEMININ', 'FEMININ'),
    }

    MATRIMONIAL = {
        ('MARIE', 'MARIE'),
        ('CELIBATAIRE', 'CELIBATAIRE'),
    }

    username = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, null=False, unique=True)  
    first_name = models.CharField(max_length=255, null=True,blank=True)
    last_name = models.CharField(max_length=255, null=True,blank=True)
    matricule = models.CharField(max_length=255, null=True, blank=True) 
    mobile = models.CharField(max_length=255, null=True,blank=True)
    type = models.CharField(max_length=50, blank=True, choices=users_types, default="Master Data")
    poste = models.CharField(max_length=255, null=True,blank=True)
    site = models.ForeignKey(Organigramme, null=True, blank=True, on_delete=models.SET_NULL, related_name='site_account')
    date_nais = models.DateField(null=True, blank=True, help_text="Format: JJ-MM-AAAA")
    genre = models.CharField(max_length=50, blank=True, choices=GENRES)
    matrimonial = models.CharField(max_length=50, blank=True, choices=MATRIMONIAL)
    address = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars', null=True, blank=True, default="user3.png")
    permis = models.CharField(max_length=255, null=True,blank=True)
    num_cni = models.CharField(max_length=255, null=True,blank=True)
    signature = models.ImageField(upload_to='signatures', null=True, blank=True)

    date_joined = models.DateTimeField(default=now)
    last_login = models.DateTimeField(blank=True, null=True)

    is_staff = models.BooleanField(default=True) # must needed, otherwise you won't be able to loginto django-admin.
    is_active = models.BooleanField(default=True) # must needed, otherwise you won't be able to loginto django-admin.
    is_superuser = models.BooleanField(default=False) # this field we inherit from PermissionsMixin.

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'matricule', 'mobile','type', 'poste', 'site', 'date_nais', 'genre', 'matrimonial', 'address', 'avatar', 'permis', 'num_cni', 'signature', 'is_superuser']
    
    @property
    def get_full_name(self):
        return f"{self.last_name} {self.first_name}"
    
    # def profile(self):
    #     profile = Profile.objects.get(user=self)
    
    def __str__(self):
        return f"{self.last_name} - {self.type} - {self.site}"



class GroupUsers(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, blank=False, related_name="user_groupusers")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=False, related_name="group_groupusers")

    def __str__(self):
        return "{} - {}".format(self.user.last_name, self.group.name)
    