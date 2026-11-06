# Busca CEP Web — ETL de CEPs com extração direto da API ViaCEP

Evolução do projeto `buscacep`. Antes, você copiava o JSON do ViaCEP e colava num arquivo (`novo.json`). Agora a aplicação **consulta a API [viacep.com.br](https://viacep.com.br) sozinha**, trata a resposta e grava na **base local** (`ceps.json`).

## O que mudou em relação ao `buscacep`

| | `buscacep` | `buscacep_web` |
|---|---|---|
| Origem dos dados | `novo.json` (colado à mão) | API ViaCEP (HTTP, formato JSON) |
| Staging area / Cleanup | Sim (`novo.json` é esvaziado) | Não existe: os dados vêm direto da web |
| Etapas do ETL | 4 (Extract, Transform, Load, Cleanup) | 3 (Extract, Transform, Load) |
| Base local | `ceps.json` | `ceps.json` (mesmo formato) |
| Dependências | nenhuma | nenhuma (usa `urllib`, da biblioteca padrão) |

## Os arquivos

| Arquivo | Papel |
|---|---|
| `main.py` | Menu interativo e orquestração do pipeline. |
| `viacep.py` | **Extract:** faz a requisição HTTP ao ViaCEP e trata erros de rede. |
| `converter.py` | **Transform** e **Load:** valida o CEP e a resposta, indexa pelo CEP e grava o `ceps.json`. |
| `ceps.json` | Base de dados local (um dicionário indexado pelo CEP sem hífen). |
| `docker-compose.yml` | Define o container que executa a aplicação. |

## Como funciona

```
 digitou o CEP
      │
      ▼
 1. EXTRACT   ── GET https://viacep.com.br/ws/{cep}/json/ ──►  JSON da API
      │
      ▼
 2. TRANSFORM ── rejeita {"erro": ...}; usa o CEP sem hífen como chave
      │
      ▼
 3. LOAD      ── adiciona/atualiza o registro no ceps.json
```

Pontos para observar no código:

- **O CEP é validado antes de ir para a rede** (8 dígitos). Evita chamadas inúteis, já que o ViaCEP responde `HTTP 400` para formato inválido.
- **CEP inexistente não é erro HTTP.** A API responde `HTTP 200` com `{"erro": "true"}`. Por isso essa checagem fica no Transform, e não no tratamento de exceções do Extract.
- **Falhas de rede viram uma mensagem amigável** (sem internet, timeout de 10 s, resposta que não é JSON) em vez de derrubar o programa.
- **A base local funciona como cache:** o que já foi buscado é consultado offline.

## Principais funções do `main.py`

| Função | O que faz |
|---|---|
| `menu_principal()` | Mostra o menu em um laço `while True`, lê a opção com `input()` e chama a função correspondente. Só termina na opção `4` (`break`). |
| `fluxo_processamento_etl(cep)` | Executa o pipeline para um CEP já normalizado: **Extract** (`buscar_cep()` do `viacep.py`), **Transform** (`converter_json_viacep()`) e **Load** (`inserir_na_base_local()`). Trata `ViaCepErro`, `JSONDecodeError` e `OSError`; retorna o endereço salvo ou `None` se algo falhar. |
| `consultar_cep_local(cep_digitado)` | Normaliza o CEP com `normalizar_cep()`, lê a base com `ler_base_local()` e exibe o endereço se existir. Se não existir, pergunta (`s/n`) se deve buscá-lo no ViaCEP e salvá-lo. |
| `cadastrar_cep_pela_web(cep_digitado)` | Valida o CEP e dispara `fluxo_processamento_etl()`, gravando ou atualizando o registro na base local. |
| `exibir_endereco(endereco, titulo)` | Imprime os campos do endereço (CEP, logradouro, bairro, cidade, estado e DDD) em um quadro formatado. Reaproveitada pela consulta e pelo cadastro. |
| `inspecionar_arquivo_disco()` | Lê o `ceps.json` direto do disco com `open()` e `read()` e o imprime, para confirmar o que foi gravado. |

Recursos do Python usados nessas funções:

- `import` de funções de outros módulos do projeto (`converter.py` e `viacep.py`), separando as etapas do ETL.
- `open(..., encoding="utf-8")` dentro de `with`, que fecha o arquivo sozinho, mesmo se ocorrer erro.
- `os.path.exists()`, para checar se o arquivo existe antes de abri-lo.
- `try / except` com exceções específicas (`ViaCepErro`, `json.JSONDecodeError`, `OSError`), para dar mensagens claras em cada falha.
- `next(iter(registro.values()))`, que pega o único valor do dicionário `{cep: endereço}` sem precisar saber a chave.
- `dict.get()`, que devolve `None` em vez de erro quando um campo não existe.
- `input()`, `print()`, `str.strip()` e `str.lower()` para a interação no terminal.
- `if __name__ == "__main__":`, que só abre o menu quando o arquivo é executado diretamente, e não quando é importado.

## Como executar

Pré-requisito: apenas **Docker** com Docker Compose. Não é preciso instalar Python. O container precisa de **acesso à internet** para chamar o ViaCEP.

Dentro da pasta `buscacep_web`:

```bash
docker compose run --rm app
```

> Use `run`, e não `up`: o menu espera você digitar. O `--rm` apaga o container ao sair.

### Opções do menu

| Opção | O que faz |
|---|---|
| `1` | Consulta um CEP na base local. **Se ele não existir lá**, pergunta se você quer buscá-lo no ViaCEP e salvá-lo. |
| `2` | Busca um CEP direto no ViaCEP e grava/atualiza na base local (pipeline completo). |
| `3` | Mostra o conteúdo bruto do `ceps.json`. |
| `4` | Encerra a aplicação. |

### Exemplo rápido

1. Rode `docker compose run --rm app`.
2. Escolha `2` e digite `30140071`. Você verá as 3 etapas do ETL.
3. Escolha `1` e digite o mesmo CEP: agora ele é encontrado na base local, sem usar a internet.
4. Escolha `3` para ver o registro gravado no `ceps.json`.

## Problemas comuns

| Mensagem | Causa provável |
|---|---|
| `Não foi possível conectar ao ViaCEP` | Sem internet, ou o Docker sem acesso à rede. |
| `A API não respondeu em 10 segundos` | Lentidão ou instabilidade no ViaCEP. Tente de novo. |
| `O ViaCEP informou que esse CEP não existe` | O CEP tem 8 dígitos, mas não está cadastrado nos Correios. |
| `Digite um CEP válido com 8 números` | Formato inválido (aceita com ou sem hífen: `01001-000` ou `01001000`). |
| `O 'ceps.json' está corrompido` | O arquivo foi editado à mão e ficou com JSON inválido. |
| `Cannot connect to the Docker daemon` | O Docker Desktop não está aberto. |

## Para ir além

- Buscar endereço por UF/cidade/logradouro (o ViaCEP tem `/ws/{UF}/{cidade}/{logradouro}/json/`).
- Guardar a data da consulta em cada registro e atualizar os mais antigos.
- Trocar o `ceps.json` por SQLite.
- Escrever testes automatizados para `converter.py` (funções puras, fáceis de testar).
