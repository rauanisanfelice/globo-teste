from django.contrib.auth.models import User
from django.db import models


class File(models.Model):

    FILE_AUDIENCIA = "A"
    FILE_TEMPO = "T"
    CHOICE_FILE = (
        (FILE_AUDIENCIA, "Arquivo de audiencia"),
        (FILE_TEMPO, "Arquivo de tempo"),
    )

    tipo_arquivo = models.CharField(
        verbose_name="Tipo do arquivo", max_length=1, choices=CHOICE_FILE
    )
    file = models.FileField(null=True, verbose_name="Arquivo")


class Pipeline(models.Model):

    STATUS_PROCESSANDO = "P"
    STATUS_FINALIZADO = "F"
    STATUS_ERRO = "E"
    CHOICE_STATUS = (
        (STATUS_PROCESSANDO, "Processando"),
        (STATUS_FINALIZADO, "Finalizado"),
        (STATUS_ERRO, "Erro"),
    )

    status = models.CharField(
        verbose_name="Status", max_length=1, choices=CHOICE_STATUS
    )
    finalizado = models.BooleanField(verbose_name="Finalizado?", default=False)
    file = models.ForeignKey(
        File, verbose_name="Arquivo uplaod", on_delete=models.CASCADE
    )

    data_inicio = models.DateTimeField(
        verbose_name="Data/Hora de inicío", auto_now=True
    )
    data_final = models.DateTimeField(
        verbose_name="Data/Hora da final", auto_now=False, null=True, blank=True,
    )
    criado_por = models.ForeignKey(
        User, verbose_name="Criado por", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Pipeline"
        verbose_name_plural = "Pipelines"


class Audiencia(models.Model):

    signal = models.CharField(name="signal", max_length=10)
    program_code = models.CharField(name="program_code", max_length=10)
    exhibition_date = models.DateField(
        "exhibition_date", auto_now=False, auto_now_add=False
    )
    program_start_time = models.DateTimeField(
        "program_start_time", auto_now=False, auto_now_add=False
    )
    average_audience = models.DecimalField(
        "average_audience", max_digits=19, decimal_places=10
    )

    class Meta:
        verbose_name = "Audiencia"
        verbose_name_plural = "Audiencias"

    def __str__(self):
        return self.signal


class TempoDisponivel(models.Model):

    signal = models.CharField(name="signal", max_length=10)
    program_code = models.CharField(name="program_code", max_length=10)
    date = models.DateField("date", auto_now=False, auto_now_add=False)
    available_time = models.IntegerField("available_time")

    class Meta:
        verbose_name = "Tempo Disponivel"
        verbose_name_plural = "Tempo Disponivel"

    def __str__(self):
        return self.signal
