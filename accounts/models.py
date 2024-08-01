from django.db import models,IntegrityError, transaction
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
#==creating ==first authentication models for user
from django.utils import timezone
from django.db.models.signals import pre_save, post_save
from django.utils.translation import ugettext_lazy as _


import random
import uuid

#===now the user manager
class UserManager(BaseUserManager):
    def _create_user(self,username, email, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self,username, email, password, **extra_fields):
        return self._create_user(username,email,password,False,False,**extra_fields)

    def create_superuser(self,username,email,password, **extra_fields):
        user=self._create_user(username,email, password, True, True, **extra_fields)
        return user

Accounts = (
    ('SILVER','Silver'),
    ('GOLD', 'Gold'),
    ('PLATINUM', 'Platinum'),
)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=254, blank=False, default='bosa')
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=254,blank=False)
    paid = models.BooleanField(default=False)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    account_type = models.CharField(max_length=8, choices=Accounts,default="SILVER")



    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()


    #====add a function to generate a referral link

    def __str__(self):
        return self.email

    class Meta:
        unique_together = ("username","email")#username and email should be unique

    def save(self, *args, **kwargs):
        pass



    #=====decoarator to check if the user is activated===
    @property
    def activated(self):
        if self.paid:return True
        else:return False

    #===define a decorator here to return the deposit amount baing on the package
    @property
    def get_deposit(self):
        deposit = 0
        if self.account_type == "SILVER":
            deposit = 20000
        elif self.account_type == "GOLD":deposit = 50000
        elif self.account_type == "PLATINUM":
            deposit >= 100000 #hoping this code works, but i think it does
        return deposit



