from django.db import models


class PassportInfo(models.Model):
    first_name = models.CharField(max_length=255, verbose_name="ISM")
    last_name = models.CharField(max_length=255, verbose_name="FAMILIYASI")
    sex = models.CharField(max_length=30, verbose_name="JINSI")
    pass_number = models.CharField(max_length=30, verbose_name="PASPORT RAQAMI")
    pass_serial = models.CharField(max_length=30, verbose_name="PASPORT SERIYASI")
    date_of_birth = models.CharField(max_length=30, verbose_name="TUG'ILGAN SANASI")
    date_of_issue = models.CharField(max_length=30, verbose_name="BERILGAN SANASI")
    date_of_expiry = models.CharField(max_length=30, verbose_name="AMAL QILISH MUDATTI")
    pinfl = models.CharField(max_length=30, verbose_name="PINFL")
