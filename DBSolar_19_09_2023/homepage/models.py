
from django.contrib.auth.models import User
from django.db import models
from django.apps import apps
from django.db import models


# class Stock(models.Model):
#     id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=30, unique=True)
#     quantity = models.IntegerField(default=1)
#     is_deleted = models.BooleanField(default=False)
#
#     def __str__(self):
#         return self.name