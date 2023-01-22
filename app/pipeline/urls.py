from django.urls import path

from pipeline.views import (
    HomeView,
    PipelineAudienciaView,
    PipelineTempoView,
    index,
    keepalive,
)

urlpatterns = [
    path("", index, name="index"),
    path("home/", HomeView.as_view(), name="home"),
    path("keepalive/", keepalive, name="keepalive"),
    path(
        "pipeline/audiencia/",
        PipelineAudienciaView.as_view(),
        name="pipeline-audiencia",
    ),
    path("pipeline/tempo/", PipelineTempoView.as_view(), name="pipeline-tempo"),
]
