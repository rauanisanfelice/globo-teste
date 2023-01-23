from django.conf import settings
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from api.views import (
    AnalizePorPeriodoList,
    AnalizePorProgramaList,
    AudienciaList,
    TempoDisponivelList,
)

schema_view = get_schema_view(
    openapi.Info(
        title="Globo API",
        default_version="1.0.0",
        description="Teste Globo - API",
        contact=openapi.Contact(email=settings.ADMINS[0][1]),
    ),
    public=False,
)


urlpatterns = [
    path("", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("swagger.json", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("audiencia/", AudienciaList.as_view(), name="audiencia",),
    path("tempo-disponivel/", TempoDisponivelList.as_view(), name="audiencia",),
    path("analitico/programa/", AnalizePorProgramaList.as_view(), name="audiencia",),
    path("analitico/periodo/", AnalizePorPeriodoList.as_view(), name="audiencia",),
]
