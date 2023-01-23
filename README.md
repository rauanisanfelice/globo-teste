# Teste Globo

Teste de avaliação para processo seletivo da Globo.

## Instruções

1. Configurando ambiente local para desenvolvimento;
2. Executar testes;
3. Executar aplicação.

### Configurando ambiente local para desenvolvimento

Copiando arquivos "*.example" depois disto preeencha com as informações necessária.s

```shell
make copy-example
```

```shell
make install
```

### Executar testes

```shell
make test
```

Coverage

```shell
make coverage
```

Sonar Qube

```shell
make sonar-scan
```

### Executar aplicação

```shell
make run
```

## Projeto

Sobre o projeto foi desenvolvido em Python com framework Django, neste projeto possui duas aplicações para atender o objetivo. A primeira aplicação tem como objetivo processar os dados. A segunda aplicação tem a função de servir os dados importados.

Após executar os comandos da #instruções o sistema irá criar um usuário na projeto de teste, este mesmo deverá ser utilizado nas duas aplicações.

| Usuário | Senha |
|---|---|
| admin | admin |

## Teste 2

A aplicação foi desenvolvida para atender um cenário de processamento dos dados por parte de um funcionário, mas segue um exemplo de arquitetura responsável para processar os dados do lake.

![Diagram](../develop/Contract/deploy_diagram.png?raw=true)
