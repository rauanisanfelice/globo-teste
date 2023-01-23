import datetime
import json
import logging
from decimal import Decimal
from http import HTTPStatus

from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient

from api.views import transform_json
from pipeline.models import Audiencia, TempoDisponivel

logger = logging.getLogger(__name__)
urlconf = __import__(settings.ROOT_URLCONF, {}, {}, [""])

FIXTURES = [settings.BASE_DIR / "dump/mock-tests.json"]

USERS = {
    "admin": [{"id": 1, "username": "admin", "password": "admin"}],
}


class APIListAudienciaTestCase(TestCase):
    "Teste de rota list de Audiencia"

    fixtures = FIXTURES

    def setUp(self):
        self.client = APIClient()
        self.client.login(**USERS["admin"][0])

    def test_api_audiencia_list(self):
        "Should get list of audiencia"

        response = self.client.get("/api/audiencia/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        result_json = json.loads(response.content.decode("utf-8"))
        audiencia = Audiencia.objects.get(id=1)
        result_audiencia = result_json["results"][0]
        date_exhibition_date = datetime.datetime.strptime(
            result_audiencia["exhibition_date"], "%Y-%m-%d"
        ).date()
        self.assertEqual(result_json["count"], 1)
        self.assertEqual(result_audiencia["signal"], audiencia.signal)
        self.assertEqual(result_audiencia["program_code"], audiencia.program_code)
        self.assertEqual(date_exhibition_date, audiencia.exhibition_date)
        self.assertEqual(
            Decimal(result_audiencia["average_audience"]), audiencia.average_audience
        )


class APIListTempoDisponivelTestCase(TestCase):
    "Teste de rota list de Tempo disponivel"

    fixtures = FIXTURES

    def setUp(self):
        self.client = APIClient()
        self.client.login(**USERS["admin"][0])

    def test_api_tempo_disponivel_list(self):
        "Should get list of Tempo Disponivel"

        response = self.client.get("/api/tempo-disponivel/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        result_json = json.loads(response.content.decode("utf-8"))
        audiencia = TempoDisponivel.objects.get(id=1)
        result_audiencia = result_json["results"][0]
        date_date = datetime.datetime.strptime(
            result_audiencia["date"], "%Y-%m-%d"
        ).date()
        self.assertEqual(result_json["count"], 1)
        self.assertEqual(result_audiencia["signal"], audiencia.signal)
        self.assertEqual(result_audiencia["program_code"], audiencia.program_code)
        self.assertEqual(date_date, audiencia.date)
        self.assertEqual(result_audiencia["available_time"], audiencia.available_time)


class TransformJsonToListTestCase(TestCase):
    "Teste de transformacao do json para lista"

    def test_transform_json(self):
        "Should transform json to list"

        mock_json = """{"index": [[ "GLOBO", "MOCK", 6]], "data": [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]}"""
        mock_list = [
            {
                "signal": "GLOBO",
                "program_code": "MOCK",
                "weekday": 6,
                "available_time": {
                    "mean": 1,
                    "median": 2,
                    "sum": 3,
                    "max": 4,
                    "min": 5,
                },
                "predicted_audience": {
                    "mean": 6,
                    "median": 7,
                    "sum": 8,
                    "max": 9,
                    "min": 10,
                },
            }
        ]
        result_list = transform_json(mock_json)

        self.assertEqual(result_list, mock_list)


class APIListAnaliticoTestCase(TestCase):
    "Teste de rota list de Analitico Por Programa"

    fixtures = FIXTURES

    def setUp(self):
        self.client = APIClient()
        self.client.login(**USERS["admin"][0])

    def test_api_list_analitico_por_programa_retorna_sucesso(self):
        "Should get list of Analicio por programa"

        response = self.client.get("/api/analitico/programa/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        result_json = json.loads(response.content.decode("utf-8"))
        mock_result = {
            "signal": "SP1",
            "program_code": "PTV1",
            "weekday": 4,
            "available_time": {
                "mean": 933891.96,
                "median": 933891.96,
                "sum": 933891.96,
                "max": 933891.96,
                "min": 933891.96,
            },
            "predicted_audience": {
                "mean": 10.0,
                "median": 10.0,
                "sum": 10,
                "max": 10,
                "min": 10,
            },
        }
        self.assertEqual(result_json[0], mock_result)

    def test_api_list_analitico_por_periodo_retorna_sucesso(self):
        "Should get list of Analicio por periodo"

        response = self.client.get(
            "/api/analitico/periodo/?exhibition_date_inicio=05%2F06%2F2020&exhibition_date_fim=05%2F06%2F2020"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        result_json = json.loads(response.content.decode("utf-8"))
        mock_result = {
            "signal": "SP1",
            "program_code": "PTV1",
            "weekday": 4,
            "available_time": {
                "mean": 933891.96,
                "median": 933891.96,
                "sum": 933891.96,
                "max": 933891.96,
                "min": 933891.96,
            },
            "predicted_audience": {
                "mean": 10.0,
                "median": 10.0,
                "sum": 10,
                "max": 10,
                "min": 10,
            },
        }
        self.assertEqual(result_json[0], mock_result)
