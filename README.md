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