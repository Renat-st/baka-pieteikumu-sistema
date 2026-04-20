from django.db import models
from django.contrib.auth.models import User


class Statuss(models.Model):
    nosaukums = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nosaukums


class PieteikumaTips(models.Model):
    nosaukums = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nosaukums


class Workflow(models.Model):
    pieteikuma_tips = models.ForeignKey(PieteikumaTips, on_delete=models.CASCADE)
    start_statuss = models.ForeignKey(Statuss, on_delete=models.CASCADE, related_name='workflow_start')
    end_statuss = models.ForeignKey(Statuss, on_delete=models.CASCADE, related_name='workflow_end')

    def __str__(self):
        return f"{self.pieteikuma_tips} : {self.start_statuss} -> {self.end_statuss}"


class Pieteikums(models.Model):
    nosaukums = models.CharField(max_length=200)
    apraksts = models.TextField(blank=True)
    statuss = models.ForeignKey(Statuss, on_delete=models.PROTECT)
    lietotajs = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tickets')
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets'
    )
    tips = models.ForeignKey(PieteikumaTips, on_delete=models.PROTECT)
    izveidots = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nosaukums