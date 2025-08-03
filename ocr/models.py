from django.db import models

class Barangay(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Barangays"

    def __str__(self):
        return self.name


class TracerRecord(models.Model):
    no            = models.CharField("No.",           max_length=50,  blank=True)
    establishment = models.CharField("Establishment", max_length=255, blank=True)
    owner         = models.CharField("Owner",         max_length=255, blank=True)
    address       = models.CharField("Address",       max_length=255, blank=True)
    business      = models.CharField("Business",      max_length=255, blank=True)

    date      = models.CharField("Date",      max_length=100, blank=True)
    first     = models.CharField("1st",       max_length=100, blank=True)
    date2     = models.CharField("Date2",     max_length=100, blank=True)
    second    = models.CharField("2nd",       max_length=100, blank=True)
    date3     = models.CharField("Date3",     max_length=100, blank=True)
    third     = models.CharField("3rd",       max_length=100, blank=True)
    datefinal = models.CharField("DateFinal", max_length=100, blank=True)
    final     = models.CharField("Final",     max_length=100, blank=True)

    remarks = models.TextField("Remarks", blank=True)

    def __str__(self):
        return f"{self.no} – {self.establishment}"

    class Meta:
        db_table = "tracer_records"
