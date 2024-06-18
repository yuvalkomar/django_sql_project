# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Hiker(models.Model):
    hid = models.IntegerField(primary_key=True)
    hname = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    smoker = models.IntegerField(blank=True, null=True)
    fitness = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Hiker'


class Trek(models.Model):
    tname = models.CharField(primary_key=True, max_length=100)
    tlength = models.IntegerField(blank=True, null=True)
    season = models.CharField(max_length=100, blank=True, null=True)
    difficulty = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Trek'


class HikerInTrek(models.Model):
    hid = models.ForeignKey(Hiker, on_delete=models.CASCADE, db_column='hID')
    tname = models.ForeignKey(Trek, on_delete=models.CASCADE, db_column='tName')
    tdate = models.DateField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'HikerInTrek'
        unique_together = (('hid', 'tname'),)


class TrekInCountry(models.Model):
    country = models.CharField(primary_key=True, max_length=100)
    tname = models.ForeignKey(Trek, on_delete=models.CASCADE, db_column='tName')

    class Meta:
        managed = True
        db_table = 'TrekInCountry'
        unique_together = (('country', 'tname'),)
