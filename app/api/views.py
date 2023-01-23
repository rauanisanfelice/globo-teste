import datetime
import json
import logging
from typing import Dict, List

import pandas as pd
from django.core.exceptions import BadRequest
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, mixins
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import AudienciaFilter, AudienciaPorPeriodoFilter
from api.serializers import (
    AudienciaSerializer,
    ResponseSerializer,
    TempoDisponivelSerializer,
)
from pipeline.models import Audiencia, TempoDisponivel

logger = logging.getLogger(__name__)


class AudienciaList(mixins.ListModelMixin, generics.GenericAPIView):

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Audiencia.objects.all()
    serializer_class = AudienciaSerializer

    def dispatch(self, request, *args, **kwargs):
        logger.info(f"AudienciaList {request.method}")
        return super().dispatch(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Audiencia"])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class TempoDisponivelList(mixins.ListModelMixin, generics.GenericAPIView):

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = TempoDisponivel.objects.all()
    serializer_class = TempoDisponivelSerializer

    def dispatch(self, request, *args, **kwargs):
        logger.info(f"TempoDisponivelList {request.method}")
        return super().dispatch(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Tempo disponivel"])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


def transform_json(json_str: str) -> List[Dict]:
    json_formated = json.loads(json_str)
    itens = json_formated["index"]
    data = json_formated["data"]
    new_json = []
    for index, item in enumerate(itens):
        new_json.append(
            {
                "signal": item[0],
                "program_code": item[1],
                "weekday": item[2],
                "available_time": {
                    "mean": round(data[index][0], 2),
                    "median": round(data[index][1], 2),
                    "sum": round(data[index][2], 2),
                    "max": round(data[index][3], 2),
                    "min": round(data[index][4], 2),
                },
                "predicted_audience": {
                    "mean": round(data[index][5], 2),
                    "median": round(data[index][6], 2),
                    "sum": round(data[index][7], 2),
                    "max": round(data[index][8], 2),
                    "min": round(data[index][9], 2),
                },
            }
        )

    return new_json


class AnalizePorProgramaList(generics.ListAPIView):

    queryset = Audiencia.objects.all()
    serializer_class = ResponseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AudienciaFilter
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    ordering = ["signal", "program_code", "weekday"]

    def dispatch(self, request, *args, **kwargs):
        logger.info(f"AnalizePorProgramaList {request.method}")
        return super().dispatch(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Analitico"])
    def get(self, request, *args, **kwargs):

        filter_program_code = self.request.query_params.get("program_code")
        filter_exhibition_date = self.request.query_params.get("exhibition_date")

        audiencias = self.queryset
        if filter_program_code is not None:
            audiencias = audiencias.filter(program_code=filter_program_code)
        if filter_exhibition_date is not None:
            filter_exhibition_date = datetime.datetime.strptime(
                filter_exhibition_date, "%d/%m/%Y"
            )
            audiencias = audiencias.filter(exhibition_date=filter_exhibition_date)
        tempo_disponivel = TempoDisponivel.objects.all()
        data_frame_audiencia = pd.DataFrame(list(audiencias.values()))
        data_frame_tempo_disponivel = pd.DataFrame(list(tempo_disponivel.values()))

        # Tratativada das datas
        data_frame_tempo_disponivel["weekday"] = pd.to_datetime(
            data_frame_tempo_disponivel["date"]
        ).dt.dayofweek
        data_frame_audiencia["date"] = pd.to_datetime(
            data_frame_audiencia["exhibition_date"]
        ).dt.date
        data_frame_audiencia["weekday"] = pd.to_datetime(
            data_frame_audiencia["exhibition_date"]
        ).dt.dayofweek

        # Busca 4 ultimos registros por data
        data_frame_audiencia = data_frame_audiencia.groupby("date").head(4)

        data_frame_merge = data_frame_tempo_disponivel.merge(
            data_frame_audiencia,
            left_on=["signal", "program_code", "weekday"],
            right_on=["signal", "program_code", "weekday"],
        )

        # Calcula a mediana
        data_frame_merge_group_by = data_frame_merge.groupby(
            ["signal", "program_code", "weekday"]
        ).agg(
            {
                "average_audience": ["mean", "median", "sum", "max", "min"],
                "available_time": ["mean", "median", "sum", "max", "min"],
            }
        )
        json_merge_group_by = data_frame_merge_group_by.to_json(orient="split")
        formated_json_merge_group_by = transform_json(json_merge_group_by)
        response = ResponseSerializer(data=formated_json_merge_group_by, many=True)
        if response.is_valid():
            return Response(response.data)
        return Response(response.errors)


class AnalizePorPeriodoList(generics.ListAPIView):

    queryset = Audiencia.objects.all()
    serializer_class = ResponseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AudienciaPorPeriodoFilter
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    ordering = ["signal", "program_code", "weekday"]

    def dispatch(self, request, *args, **kwargs):
        logger.info(f"AnalizePorPeriodoList {request.method}")
        return super().dispatch(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Analitico"])
    def get(self, request, *args, **kwargs):

        audiencias = self.queryset
        exhibition_date_inicio = self.request.query_params.get("exhibition_date_inicio")
        exhibition_date_fim = self.request.query_params.get("exhibition_date_fim")

        if exhibition_date_inicio is None or exhibition_date_fim is None:
            raise BadRequest("Campos obrigatórios estão vazio")

        exhibition_date_inicio = datetime.datetime.strptime(
            exhibition_date_inicio, "%d/%m/%Y"
        )
        exhibition_date_fim = datetime.datetime.strptime(
            exhibition_date_fim, "%d/%m/%Y"
        )
        audiencias = audiencias.filter(
            exhibition_date__gte=exhibition_date_inicio,
            exhibition_date__lte=exhibition_date_fim,
        )

        tempo_disponivel = TempoDisponivel.objects.all()
        data_frame_audiencia = pd.DataFrame(list(audiencias.values()))
        data_frame_tempo_disponivel = pd.DataFrame(list(tempo_disponivel.values()))

        # Tratativada das datas
        data_frame_tempo_disponivel["weekday"] = pd.to_datetime(
            data_frame_tempo_disponivel["date"]
        ).dt.dayofweek
        data_frame_audiencia["date"] = pd.to_datetime(
            data_frame_audiencia["exhibition_date"]
        ).dt.date
        data_frame_audiencia["weekday"] = pd.to_datetime(
            data_frame_audiencia["exhibition_date"]
        ).dt.dayofweek

        # Busca 4 ultimos registros por data
        data_frame_audiencia = data_frame_audiencia.groupby("date").head(4)

        data_frame_merge = data_frame_tempo_disponivel.merge(
            data_frame_audiencia,
            left_on=["signal", "program_code", "weekday"],
            right_on=["signal", "program_code", "weekday"],
        )

        # Calcula a mediana
        data_frame_merge_group_by = data_frame_merge.groupby(
            ["signal", "program_code", "weekday"]
        ).agg(
            {
                "average_audience": ["mean", "median", "sum", "max", "min"],
                "available_time": ["mean", "median", "sum", "max", "min"],
            }
        )
        json_merge_group_by = data_frame_merge_group_by.to_json(orient="split")
        formated_json_merge_group_by = transform_json(json_merge_group_by)
        response = ResponseSerializer(data=formated_json_merge_group_by, many=True)
        if response.is_valid():
            return Response(response.data)
        return Response(response.errors)
