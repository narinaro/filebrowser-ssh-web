from django.db import models
# Create your models here.


class login_parameters(models.Model):
    session = models.IntegerField()
    server = models.CharField(max_length=100)
    user = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    port = models.CharField(max_length=100)
