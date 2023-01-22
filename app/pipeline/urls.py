from django.urls import path

from pipeline.views import (
    HomeView,
    PipelineAudienciaView,
    PipelineHistoricoView,
    PipelineTempoView,
    index,
    keepalive,
)

urlpatterns = [
    path("", index, name="index"),
    path("home/", HomeView.as_view(), name="home"),
    path("keepalive/", keepalive, name="keepalive"),
    path(
        "pipeline/historico/",
        PipelineHistoricoView.as_view(),
        name="pipeline-historico",
    ),
    path(
        "pipeline/audiencia/",
        PipelineAudienciaView.as_view(),
        name="pipeline-audiencia",
    ),
    path("pipeline/tempo/", PipelineTempoView.as_view(), name="pipeline-tempo"),
]
