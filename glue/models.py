from django.db import models


class Vkaccount(models.Model):
    name = models.CharField(max_length=300, default="")
    token = models.CharField(max_length=300)
    vk_id = models.IntegerField()


class Community(models.Model):
    vk_domen = models.IntegerField()
    name = models.CharField(max_length=300, default="")
    url = models.CharField(max_length=300, default="")
