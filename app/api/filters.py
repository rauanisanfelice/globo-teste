from django_filters import rest_framework as filters

from pipeline.models import Audiencia


class AudienciaFilter(filters.FilterSet):
    class Meta:
        model = Audiencia
        fields = ["program_code", "exhibition_date"]


class AudienciaPorPeriodoFilter(filters.FilterSet):

    exhibition_date_inicio = filters.DateFilter()
    exhibition_date_fim = filters.DateFilter()

    class Meta:
        model = Audiencia
        fields = []
