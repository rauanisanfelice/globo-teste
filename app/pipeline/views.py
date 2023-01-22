import logging
from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import HttpResponse, redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import View

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


class PipelineAudienciaView(View):

    template_name = "pipeline-audiencia.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        logger.info(f"PipelineAudienciaView {request.method}")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, **kwargs):
        return render(request, self.template_name)


class PipelineTempoView(View):

    template_name = "pipeline-tempo.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        logger.info(f"PipelineTempoView {request.method}")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, **kwargs):
        return render(request, self.template_name)
