from django.db import models

class Pathway(models.Model):
  name = models.CharField(max_length=255, primary_key=True)
  graphInfo = models.TextField()

class Compound(models.Model):
  identifier = models.CharField(max_length=6, primary_key=True)
  name = models.CharField(max_length=255)