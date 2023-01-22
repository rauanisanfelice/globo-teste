import csv
import datetime
import logging
from http import HTTPStatus
from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.http import HttpRequest
from django.shortcuts import HttpResponse, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from pipeline.entity import Zones
from pipeline.forms import UploadFileForm
from pipeline.models import Audiencia
from pipeline.models import File as FileUpload
from pipeline.models import Pipeline, TempoDisponivel

ERROR_TEMPLATE: str = "error.html"
ERROR_BAD_REQUEST: str = "Requisição inválida"

logger = logging.getLogger(__name__)


def bad_request(request: HttpRequest, exception):
    status = HTTPStatus.BAD_REQUEST
    context = {
        "error_menssage": ERROR_BAD_REQUEST,
        "error_status": status.value,
    }
    logger.error(f"Erro: {exception}")
    return render(request, ERROR_TEMPLATE, context, status=status.value)


def permission_denied(request: HttpRequest, exception):
    status = HTTPStatus.FORBIDDEN
    context = {"error_menssage": "Permisão negada.", "error_status": status.value}
    logger.error(f"Erro: {exception}")
    return render(request, ERROR_TEMPLATE, context, status=status.value)


def page_not_found(request: HttpRequest, exception):
    status = HTTPStatus.NOT_FOUND
    context = {"error_menssage": "Página não localizada.", "error_status": status.value}
    logger.error(f"Erro: {exception}")
    return render(request, ERROR_TEMPLATE, context, status=status.value)


def server_error(request: HttpRequest):
    status = HTTPStatus.INTERNAL_SERVER_ERROR
    context = {
        "error_menssage": "Erro interno no servidor.",
        "error_status": status.value,
    }
    return render(request, ERROR_TEMPLATE, context, status=status.value)


@login_required
def keepalive(request):
    html = "<html><body>KeepAlive Ok.</body></html>"
    return HttpResponse(html)


@login_required
def index(request):
    return redirect("login")


class HomeView(View):

    template_name = "home.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        logger.info(f"HomeView {request.method}")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, **kwargs):
        return render(request, self.template_name)


class PipelineHistoricoView(ListView):

    template_name = "pipeline-historico.html"
    model = Pipeline
    ordering = ["-data_inicio", "-data_final"]

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        logger.info(f"PipelineHistoricoView {request.method}")
        return super().dispatch(request, *args, **kwargs)


class PipelineAudienciaView(FormView):

    template_name = "pipeline-audiencia.html"
    form_class = UploadFileForm
    success_url = reverse_lazy("pipeline-historico")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        logger.info(f"PipelineAudienciaView {request.method}")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form"] = self.form_class(self.request.GET)
        return context

    def upload_data_base_file(self, pipeline: Pipeline):
        file_name = pipeline.file.file.path
        delemiter = ","
        with open(file_name, newline="") as csvfile:
            spamreader = csv.reader(csvfile, delimiter=delemiter, quotechar="|")
            index = 0
            for row in spamreader:
                if len(row) != 5:
                    raise Exception("Layout do arquivo incorreto")

                index += 1
                if index == 1:
                    continue
                Audiencia.objects.create(
                    signal=row[0],
                    program_code=row[1],
                    exhibition_date=row[2],
                    program_start_time=row[3],
                    average_audience=row[4],
                )

    def post(self, request: HttpRequest, **kwargs: Any) -> HttpResponse:
        context = super().get_context_data(**kwargs)
        form = self.form_class(request.POST, request.FILES)
        if not form.is_valid():
            messages.add_message(
                request, messages.ERROR, "Erro ao processar arquivo",
            )
            return render(request, self.template_name, context=context)

        file = request.FILES["file"]
        file_create = File(file, f"zone/{Zones.RAW.value}/{file.name}")
        file_upload = FileUpload.objects.create(
            tipo_arquivo=FileUpload.FILE_AUDIENCIA, file=file_create,
        )
        pipeline = Pipeline.objects.create(
            file=file_upload,
            status=Pipeline.STATUS_PROCESSANDO,
            criado_por=request.user,
        )

        try:
            self.upload_data_base_file(pipeline=pipeline)

            pipeline.data_final = datetime.datetime.now()
            pipeline.finalizado = True
            pipeline.status = Pipeline.STATUS_FINALIZADO
            pipeline.save()

            messages.add_message(
                request, messages.SUCCESS, "Arquivo processado com sucesso",
            )

        except Exception as ex:

            pipeline.finalizado = True
            pipeline.status = Pipeline.STATUS_ERRO
            pipeline.save()

            messages.add_message(
                request, messages.ERROR, f"Erro ao processar arquivo - Erro: {ex}",
            )
            return render(request, self.template_name, context=context)

        return redirect(self.success_url)


class PipelineTempoView(FormView):

    template_name = "pipeline-tempo.html"
    form_class = UploadFileForm
    success_url = reverse_lazy("pipeline-historico")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        logger.info(f"PipelineTempoView {request.method}")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form"] = self.form_class(self.request.GET)
        return context

    def upload_data_base_file(self, pipeline: Pipeline):
        file_name = pipeline.file.file.path
        delemiter = ";"
        with open(file_name, newline="") as csvfile:
            spamreader = csv.reader(csvfile, delimiter=delemiter, quotechar="|")
            index = 0
            for row in spamreader:
                if len(row) != 4:
                    raise Exception("Layout do arquivo incorreto")

                index += 1
                if index == 1:
                    continue
                date_split = row[2].split("/")
                new_date = f"{date_split[2]}-{date_split[1]}-{date_split[0]}"
                TempoDisponivel.objects.create(
                    signal=row[0],
                    program_code=row[1],
                    date=new_date,
                    available_time=row[3],
                )

    def post(self, request: HttpRequest, **kwargs: Any) -> HttpResponse:
        context = super().get_context_data(**kwargs)
        form = self.form_class(request.POST, request.FILES)
        if not form.is_valid():
            messages.add_message(
                request, messages.ERROR, "Erro ao processar arquivo",
            )
            return render(request, self.template_name, context=context)

        file = request.FILES["file"]
        file_create = File(file, f"zone/{Zones.RAW.value}/{file.name}")
        file_upload = FileUpload.objects.create(
            tipo_arquivo=FileUpload.FILE_TEMPO, file=file_create,
        )
        pipeline = Pipeline.objects.create(
            file=file_upload,
            status=Pipeline.STATUS_PROCESSANDO,
            criado_por=request.user,
        )

        try:
            self.upload_data_base_file(pipeline=pipeline)

            pipeline.data_final = datetime.datetime.now()
            pipeline.finalizado = True
            pipeline.status = Pipeline.STATUS_FINALIZADO
            pipeline.save()

            messages.add_message(
                request, messages.SUCCESS, "Arquivo processado com sucesso",
            )

        except Exception as ex:

            pipeline.finalizado = True
            pipeline.status = Pipeline.STATUS_ERRO
            pipeline.save()

            messages.add_message(
                request, messages.ERROR, f"Erro ao processar arquivo - Erro: {ex}",
            )
            return render(request, self.template_name, context=context)

        return redirect(self.success_url)
