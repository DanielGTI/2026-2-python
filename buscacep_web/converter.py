"""
===============================================================================
MÓDULO: converter.py  (ETAPAS 2 E 3 DO ETL: TRANSFORM e LOAD)
===============================================================================
- normalizar_cep       : valida e padroniza o CEP digitado.
- converter_json_viacep: transforma a resposta da API em {cep_sem_hifen: dados}.
- ler_base_local       : lê o ceps.json (a base de dados local).
- inserir_na_base_local: grava o registro no ceps.json (Load).
===============================================================================
"""

import json
import os

# O ceps.json fica na mesma pasta deste arquivo, não importa de onde o
# programa seja executado.
PASTA_PROJETO = os.path.dirname(os.path.abspath(__file__))
NOME_ARQUIVO_PADRAO = os.path.join(PASTA_PROJETO, "ceps.json")


def normalizar_cep(texto):
    """
    Remove hífen/espaços e valida o CEP.
    Retorna os 8 dígitos (str) ou None se o formato for inválido.
    """
    cep_limpo = texto.replace("-", "").strip()
    if len(cep_limpo) != 8 or not cep_limpo.isdigit():
        return None
    return cep_limpo


def converter_json_viacep(dados_endereco):
    """
    TRANSFORM: valida a resposta do ViaCEP e a indexa pelo CEP sem hífen.
    Retorna None se o CEP não existir ou se a resposta vier sem o campo 'cep'.
    """
    if not isinstance(dados_endereco, dict):
        print("[!] Erro: a resposta da API não tem o formato esperado.")
        return None

    if "erro" in dados_endereco:
        print("[!] Aviso: o ViaCEP informou que esse CEP não existe.")
        return None

    chave_limpa = dados_endereco.get("cep", "").replace("-", "").strip()

    if not chave_limpa:
        print("[!] Erro: não foi possível identificar a chave 'cep' na resposta.")
        return None

    return {chave_limpa: dados_endereco}


def ler_base_local(caminho_arquivo=NOME_ARQUIVO_PADRAO):
    """
    Lê o ceps.json e devolve o dicionário.
    Arquivo inexistente ou vazio -> {}.
    Arquivo corrompido -> levanta json.JSONDecodeError (quem chama decide).
    """
    if not os.path.exists(caminho_arquivo):
        return {}

    with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
        conteudo = arquivo.read()

    if not conteudo.strip():
        return {}

    return json.loads(conteudo)


def inserir_na_base_local(registro_convertido, caminho_arquivo=NOME_ARQUIVO_PADRAO):
    """
    LOAD: junta o registro à base existente e regrava o arquivo.
    Se o CEP já existir, ele é atualizado (sem duplicar).
    Retorna a base atualizada.
    """
    base_dados = ler_base_local(caminho_arquivo)
    base_dados.update(registro_convertido)

    with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
        json.dump(base_dados, arquivo, ensure_ascii=False, indent=4)

    return base_dados
