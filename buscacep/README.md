# Busca CEP — mini pipeline de ETL em Python

Aplicação de terminal que mantém uma **base local de CEPs** em um arquivo JSON e permite consultá-la sem acessar a internet. Ela foi escrita para estudar, na prática, o fluxo **ETL** (*Extract, Transform, Load*) com Python.

## O que a aplicação faz

Você entra com dados de endereço no formato retornado pela API pública [ViaCEP](https://viacep.com.br). A aplicação limpa e organiza esses dados e os guarda em uma base consolidada. Depois, é possível buscar qualquer CEP já cadastrado.

> **Importante:** a aplicação **não** chama a API do ViaCEP. Você copia o JSON manualmente (veja o passo a passo abaixo). Isso deixa o foco no tratamento dos dados.

### Os arquivos

| Arquivo | Papel |
|---|---|
| `main.py` | Programa principal: menu interativo, consulta e orquestração do ETL. |
| `converter.py` | Etapa **Transform**: valida o JSON e o converte para o formato da base. |
| `novo.json` | **Staging area**: área de entrada onde você cola o JSON de um novo CEP. |
| `ceps.json` | **Base consolidada**: repositório final com todos os CEPs cadastrados. |
| `docker-compose.yml` | Define o container que executa a aplicação. |

### O pipeline de ETL

Quando você escolhe a opção `[2]` do menu, acontecem 4 etapas:

```
novo.json ──► 1. EXTRACT ──► 2. TRANSFORM ──► 3. LOAD ──► ceps.json
 (entrada)    lê o arquivo    converter.py     grava na      (base final)
                              limpa e indexa   base
                                                   │
                                                   ▼
                                            4. CLEANUP
                                      esvazia o novo.json
```

1. **Extract:** lê o conteúdo bruto do `novo.json`.
2. **Transform:** o `converter.py` usa o CEP **sem hífen** como chave (`06268-160` vira `06268160`). Se o JSON indicar um CEP inexistente (campo `"erro"`) ou não tiver o campo `cep`, o registro é rejeitado.
3. **Load:** o registro é adicionado ao `ceps.json`. Se o CEP já existir, ele é atualizado, sem duplicar.
4. **Cleanup:** o `novo.json` é esvaziado, para o mesmo dado não ser processado duas vezes.

Como fica o `ceps.json` (um dicionário indexado pelo CEP, o que torna a busca direta):

```json
{
    "01001000": {
        "cep": "01001-000",
        "logradouro": "Praça da Sé",
        "bairro": "Sé",
        "localidade": "São Paulo",
        "uf": "SP",
        "ddd": "11"
    }
}
```

## Como executar

### Pré-requisito

Só o **Docker** (com o Docker Compose) instalado. Não precisa instalar Python nem nenhuma biblioteca: tudo roda dentro do container, a partir da imagem oficial `python:3.12-slim`.

### Passo a passo

1. Abra um terminal **dentro da pasta `buscacep`**.
2. Execute:

   ```bash
   docker compose run --rm app
   ```

   Na primeira vez, o Docker baixa a imagem do Python, o que pode demorar um pouco. Depois disso o menu aparece:

   ```
   ==================================================
      SISTEMA DE PROCESSAMENTO DE DADOS (ETL DE CEPS)
   ==================================================
   [ 1 ] Consultar CEP na base consolidada (ceps.json)
   [ 2 ] Executar Pipeline ETL ('novo.json' -> 'ceps.json')
   [ 3 ] Inspecionar arquivo 'ceps.json' direto do disco
   [ 4 ] Sair do sistema
   ```

> Use `docker compose run --rm app` e **não** `docker compose up`. O menu espera você digitar, e o `run` liga o teclado ao container corretamente. O `--rm` apaga o container ao sair.

### Cadastrar um novo CEP

1. No navegador, abra a URL do ViaCEP com o CEP desejado, por exemplo:
   `https://viacep.com.br/ws/06268160/json/`
2. Copie o JSON exibido.
3. Cole o conteúdo no arquivo `novo.json` (que está na pasta do projeto) e salve.
4. No menu, escolha a opção **`2`**. Você verá as 4 etapas do ETL.
5. Use a opção **`1`** e digite o CEP (com ou sem hífen) para consultar.

### Opções do menu

| Opção | O que faz |
|---|---|
| `1` | Pede um CEP (8 dígitos) e mostra logradouro, bairro, cidade, estado e DDD, se existir na base. |
| `2` | Executa o pipeline ETL com o conteúdo do `novo.json`. |
| `3` | Mostra o conteúdo bruto do `ceps.json`, lido do disco. |
| `4` | Encerra a aplicação. |

## Como o Docker foi configurado

O `docker-compose.yml` sobe um único serviço, o `app`:

- **`image: python:3.12-slim`:** usa o Python oficial pronto, sem precisar de Dockerfile.
- **`volumes: .:/app/buscacep`:** compartilha a pasta do projeto com o container. Assim, os dados gravados em `ceps.json` e `novo.json` **ficam no seu computador** e não se perdem quando o container é removido.
- **`PYTHONPATH=/app`:** o `main.py` faz `from buscacep.converter import ...`, então o Python precisa enxergar a pasta pai como ponto de partida dos pacotes.
- **`stdin_open` e `tty`:** permitem que o `input()` do menu receba o que você digita.

## Problemas comuns

| Sintoma | Causa provável |
|---|---|
| `[EXTRACT FALHOU]: ... já está vazio` | O `novo.json` está vazio. Cole um JSON do ViaCEP antes de usar a opção `2`. |
| `ERRO NO PIPELINE` | O conteúdo do `novo.json` não é um JSON válido (confira chaves, aspas e vírgulas). |
| `CEP inexistente` | O ViaCEP respondeu `{"erro": true}` para esse CEP. Verifique se ele está correto. |
| `não consta na base local` | O CEP ainda não foi cadastrado via opção `2`. |
| `Cannot connect to the Docker daemon` | O Docker Desktop não está aberto. Inicie-o e tente de novo. |

## Para ir além (sugestões de exercício)

- Fazer o programa buscar o CEP direto na API do ViaCEP, eliminando o passo manual de copiar e colar.
- Permitir cadastrar vários CEPs de uma vez (o `novo.json` como lista).
- Trocar o `ceps.json` por um banco de dados (SQLite, por exemplo) e comparar as abordagens.
