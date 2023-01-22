from django.contrib.auth.models import User
from django.db import models


class Status(models.Model):

    descricao = models.CharField(verbose_name="Descrição", max_length=100)

    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Status"
        ordering = ["descricao"]

    def __str__(self):
        return self.descricao


class Pipeline(models.Model):

    status = models.ForeignKey(Status, verbose_name="Status", on_delete=models.CASCADE)
    finalizado = models.BooleanField(verbose_name="Finaliza?", default=False)

    data_inicio = models.DateTimeField(
        verbose_name="Data/Hora de inicío", auto_now=True
    )
    data_inicio = models.DateTimeField(
        verbose_name="Data/Hora da final", auto_now=False
    )
    criado_por = models.ForeignKey(
        User, verbose_name="Criado por", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Pipeline"
        verbose_name_plural = "Pipelines"
