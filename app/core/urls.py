from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from pipeline.views import bad_request, page_not_found, permission_denied, server_error

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls"), name="login"),
    path("", include("pipeline.urls")),
    path(
        "400/",
        bad_request,
        kwargs={"exception": Exception("Requisição mal realizada")},
    ),
    path(
        "403/", permission_denied, kwargs={"exception": Exception("Permisão negada")},
    ),
    path(
        "404/",
        page_not_found,
        kwargs={"exception": Exception("Página não localizada")},
    ),
    path("500/", server_error),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
