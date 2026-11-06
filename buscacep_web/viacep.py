"""
===============================================================================
MÓDULO: viacep.py  (ETAPA 1 DO ETL: EXTRACT)
===============================================================================
Cliente da API pública ViaCEP (https://viacep.com.br).

Usa apenas a biblioteca padrão do Python (urllib), então não é preciso
instalar nada com pip.
===============================================================================
"""

import json
import urllib.error
import urllib.request

URL_VIACEP = "https://viacep.com.br/ws/{cep}/json/"
TIMEOUT_SEGUNDOS = 10


class ViaCepErro(Exception):
    """Falha ao acessar a API (sem internet, timeout, resposta inválida...)."""


def buscar_cep(cep, timeout=TIMEOUT_SEGUNDOS):
    """
    Consulta o ViaCEP e devolve a resposta como dicionário.

    'cep' deve ter 8 dígitos, sem hífen (a validação é feita em converter.py).

    Atenção: para um CEP bem formatado, mas inexistente, a API responde
    HTTP 200 com {"erro": "true"}. Quem decide o que fazer com isso é a
    etapa de Transform (converter.py).
    """
    url = URL_VIACEP.format(cep=cep)
    requisicao = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "buscacep-web-aula/1.0",
        },
    )

    try:
        with urllib.request.urlopen(requisicao, timeout=timeout) as resposta:
            corpo = resposta.read().decode("utf-8")
        return json.loads(corpo)

    except urllib.error.HTTPError as erro:
        # Ex.: 400 quando o formato do CEP é rejeitado pela API.
        raise ViaCepErro(f"A API respondeu com erro HTTP {erro.code}.") from erro
    except urllib.error.URLError as erro:
        raise ViaCepErro(
            f"Não foi possível conectar ao ViaCEP (verifique a internet): {erro.reason}"
        ) from erro
    except TimeoutError as erro:
        raise ViaCepErro(f"A API não respondeu em {timeout} segundos.") from erro
    except json.JSONDecodeError as erro:
        raise ViaCepErro("A API devolveu uma resposta que não é um JSON válido.") from erro
