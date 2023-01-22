import logging

from django.contrib import admin

from pipeline.models import Audiencia, Pipeline

admin.site.site_header = "Globo Administrador"
admin.site.index_title = "Portal Globo"
admin.site.site_title = "Bem vindo ao Portal Globo"
admin.site.empty_value_display = ""


logger = logging.getLogger(__name__)


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    pass


@admin.register(Audiencia)
class AudienciaAdmin(admin.ModelAdmin):
    pass
