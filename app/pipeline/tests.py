import logging
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.test import Client, TestCase
from django.urls import URLPattern, URLResolver, reverse

logger = logging.getLogger(__name__)
urlconf = __import__(settings.ROOT_URLCONF, {}, {}, [""])

ERROR_TEMPLATE: str = "error.html"
FIXTURES = [settings.BASE_DIR / "dump/mock-tests.json"]

USERS = {
    "admin": [{"id": 1, "username": "admin", "password": "admin"}],
    "fail": [{"id": 100, "username": "teste.fail", "password": "password"}],
    "inativo": [{"id": 2, "username": "teste.inativo", "password": "admin"}],
    "ativo": [{"id": 3, "username": "teste.ativo", "password": "admin"}],
}


def list_urls(lis, acc=None):
    """Função que busca todas as urls do projeto"""
    if acc is None:
        acc = []
    if not lis:
        return
    first_list = lis[0]
    if isinstance(first_list, URLPattern):
        yield acc + [str(first_list.pattern)]
    elif isinstance(first_list, URLResolver):
        yield from list_urls(first_list.url_patterns, acc + [str(first_list.pattern)])
    yield from list_urls(lis[1:], acc)


class TestLogin(TestCase):
    "Testes de login"

    fixtures = FIXTURES

    def setUp(self):
        "Configuração inicial do teste"

        self.client = Client()
        self.urls = list_urls(urlconf.urlpatterns)
        self.exclusao = [
            "accounts",
            "admin",
            "400",
            "403",
            "404",
            "500",
        ]

    def test_redirect_if_not_logged_in(self):
        """Testa se ira redirecionar para tela de login caso não estiver logado

        Telas que não serão testadas:

            * accounts/
            * admin/
            * 400/
            * 403/
            * 404/
            * 500/
        """

        for url in self.urls:

            # VERIFICA SE DEVE VALIDAR URL
            url_name = "".join(url)
            if url_name.split("/")[0] not in self.exclusao and url_name:
                valid = True
                for exclusao in self.exclusao:
                    if exclusao in url_name:
                        valid = False
                        break

                if valid:

                    # TRATAR EXCECOES
                    logger.info(f"Testando redirect login: {url_name}")
                    if "<" in url_name:

                        parameters = url_name.split("<")
                        parameters = list(filter(lambda x: ">" in x, parameters))
                        parameters = list(map(lambda x: x.split(">/"), parameters))
                        new_parameters = []
                        for item in parameters:
                            for i in item:
                                new_parameters.append(i)

                        parameters = list(filter(lambda x: x != "", new_parameters))
                        parameters = list(filter(lambda x: ":" in x, parameters))
                        list_parameters = list(map(lambda x: x.split(":"), parameters))
                        new_list_parameters = []
                        for item in list_parameters:
                            if item[0] != "":
                                new_list_parameters.append(item)

                        # MONTA URL
                        for parameter in new_list_parameters:
                            url_name = url_name.replace(parameter[0], "")

                    # REALIZA REQUEST
                    response = self.client.get(f"/{url_name}")

                    self.assertEqual(
                        response.status_code, HTTPStatus.FOUND, msg=f"URL: {url_name}"
                    )
                    self.assertRedirects(response, f"/accounts/login/?next=/{url_name}")

    def test_login_fail(self):
        "Testa login com usuário e senha incorretos"

        response = self.client.post(reverse("login"), USERS["fail"][0], follow=True)
        form = AuthenticationForm(None, USERS["fail"][0])
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors.keys())
        self.assertIn(
            "Por favor, entre com um usuário  e senha corretos. Note que ambos os campos diferenciam maiúsculas e minúsculas.",
            form.errors["__all__"],
        )

    def test_login_success(self):
        "Testa login com usuário e senha corretos"

        response = self.client.post(reverse("login"), USERS["admin"][0], follow=True)
        form = AuthenticationForm(None, USERS["admin"][0])
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(form.is_valid())

    def test_login_conta_inativa(self):
        "Testa login com usuário e senha corretos, porem conta está inativa"

        response = self.client.post(reverse("login"), USERS["inativo"][0], follow=True)
        form = AuthenticationForm(None, USERS["inativo"][0])
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(form.is_valid())
        self.assertIn("inactive", form.error_messages)
        self.assertEqual(form.error_messages["inactive"], "Esta conta está inativa.")


class ErrorHandlersTestCase(TestCase):
    "Teste se as rotas de erro"

    def setUp(self):
        self.client = Client()
        self.client.login(**USERS["admin"][0])

    def test_400_page(self):
        "Should check is 400 page correct"
        response = self.client.get("/400/")
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertTemplateUsed(response, ERROR_TEMPLATE)
        self.assertIn("Requisição inválida", response.content.decode("utf-8"))

    def test_404_page(self):
        "Should check is 404 page correct"
        response = self.client.get("/404/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, ERROR_TEMPLATE)
        self.assertIn("Página não localizada.", response.content.decode("utf-8"))

    def test_403_page(self):
        "Should check is 403 page correct"
        response = self.client.get("/403/")
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertTemplateUsed(response, ERROR_TEMPLATE)
        self.assertIn("Permisão negada.", response.content.decode("utf-8"))

    # def test_500_page(self):
    #     "Should check is 500 page correct"
    #     response = self.client.get("/500/")
    #     self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
    #     self.assertTemplateUsed(response, ERROR_TEMPLATE)
    #     self.assertIn("Erro interno no servidor.", response.content.decode("utf-8"))


class KeepAliveTestCase(TestCase):
    "Teste rota keepalive"

    fixtures = FIXTURES

    def setUp(self):
        self.client = Client()
        self.client.login(**USERS["admin"][0])

    def test_keep_alive_route(self):
        "Should check is route keep alive"
        response = self.client.get("/keepalive/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.content, b"<html><body>KeepAlive Ok.</body></html>")
