# tracer_backend/ocr/models.py

from django.db import models

class TracerRecord(models.Model):
    no            = models.CharField("No.", max_length=50, blank=True)
    establishment = models.CharField(max_length=255, blank=True)
    owner         = models.CharField(max_length=255, blank=True)
    address       = models.CharField(max_length=255, blank=True)
    business      = models.CharField(max_length=255, blank=True)
    date          = models.CharField(max_length=100, blank=True)
    first         = models.CharField("1st", max_length=100, blank=True)
    date2         = models.CharField(max_length=100, blank=True)
    second        = models.CharField("2nd", max_length=100, blank=True)
    date3         = models.CharField(max_length=100, blank=True)
    third         = models.CharField("3rd", max_length=100, blank=True)
    final         = models.CharField(max_length=100, blank=True)
    remarks       = models.TextField(blank=True)

    def __str__(self):
        return f"{self.no} – {self.establishment}"


class MonthlyBusinessRecord(models.Model):
    no         = models.CharField("No.", max_length=50, blank=True)
    name       = models.CharField(max_length=255, blank=True)
    address    = models.CharField(max_length=255, blank=True)
    january    = models.CharField(max_length=100, blank=True)
    february   = models.CharField(max_length=100, blank=True)
    march      = models.CharField(max_length=100, blank=True)
    april      = models.CharField(max_length=100, blank=True)
    may        = models.CharField(max_length=100, blank=True)
    june       = models.CharField(max_length=100, blank=True)
    july       = models.CharField(max_length=100, blank=True)
    august     = models.CharField(max_length=100, blank=True)
    september  = models.CharField(max_length=100, blank=True)
    october    = models.CharField(max_length=100, blank=True)
    november   = models.CharField(max_length=100, blank=True)
    december   = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.no} – {self.name}"
