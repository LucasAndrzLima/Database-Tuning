# Avaliação Somativa N2 - Equipe 10

**Tema:** distribuição geográfica dos fornecedores.

[Relatório final](RELATORIO.pdf) · [Apresentação](APRESENTACAO.pptx) · [Pacote completo](N2_Equipe10.zip)

**Integrantes:** Bárbara Tebaldi Franco; Henrique Dias de Carvalho Junior; Joao Vitor Lima Cecilio; Lucas Andrzejewski de Lima.

## Objetivo e escopo

Analisar a participação dos fornecedores por região para apoiar o planejamento de suprimentos. O projeto utiliza as tabelas supplier, nation e region do TPC-H SF=0,01: 100 fornecedores, 25 países e cinco regiões. O recorte mantém todos os fornecedores dessa escala e permite reproduzir a integração e a validação com menor consumo de recursos.

## Execução

Requisito: Docker com contêineres Linux e Docker Compose. Na pasta do projeto:

```powershell
.\scripts\preparar.ps1
docker compose up -d mysql mongodb postgres redis
docker compose run --rm extrair
docker compose run --rm carregar
docker compose run --rm validar
docker compose run --rm analisar
```

Na primeira inicialização de um volume novo do Redash:

```powershell
docker compose run --rm server create_db
```

Depois:

```powershell
docker compose up -d server worker scheduler
```

Abrir `http://localhost:5000`, criar a conta administrativa e configurar a fonte MongoDB com URI `mongodb://mongodb:27017/n2_equipe10`, banco `n2_equipe10`. Criar as consultas a partir de `consultas/redash/` e adicionar as duas visualizações ao dashboard.

| Visual | Campos |
|---|---|
| Participação de fornecedores por região | Barras: região e participação_pct; unidade % |
| Distribuição de fornecedores por país | Tabela: país, região, fornecedores e participação_pct |

Os valores de participação já estão na escala de 0 a 100. Não aplicar uma formatação que multiplique novamente por cem.

## Arquivos

- `RELATORIO.pdf`: problema, modelos, ETL, validação e análise gerencial.
- `APRESENTACAO.pptx`: apresentação de nove slides para os dez minutos da equipe.
- `modelo_estrela.mmd`: modelo dimensional.
- `sql/`: base do recorte, extração e consultas de conferência.
- `mongo/`: transformação, carga, validação e agregações no mongosh.
- `consultas/`: pipelines nativos e versões para o Redash.
- `evidencias/`: comparação MySQL × MongoDB e resultados das consultas.
- `ROTEIRO.md`: organização da apresentação de dez minutos.

A ETL foi executada nos contêineres do Compose. A validação confirmou os 100 fornecedores, 25 países e cinco regiões, sem divergências. As duas consultas foram executadas no Redash e conferidas com os resultados MySQL/MongoDB. A captura do dashboard e a conferência estão em `evidencias/redash/`.

Para conferir pelo Workbench: `localhost:3308`, usuário `root`, senha local configurada no `.env`, schema `tpch`. Para o Compass: `mongodb://localhost:27018/n2_equipe10`.

Encerrar preservando os dados:

```powershell
docker compose stop
```

## Referências

Avaliação Somativa N2; Aula 04 - Modelagem de bancos NoSQL; Diagrama TPCH; laboratórios DB L02 - Modelagem e criação de bancos NoSQL e DB L03 - TPC-H, MongoDB e Analytics/BI.
