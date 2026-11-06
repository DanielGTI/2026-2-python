"""
===============================================================================
MÓDULO: converter.py
===============================================================================
Funções para conversão e atualização do repositório JSON.
===============================================================================
"""

import json
import os

NOME_ARQUIVO_PADRAO = "ceps.json"


def converter_json_viacep(json_bruto_viacep):
    """Trata e converte a resposta do ViaCEP para um dicionário indexado."""
    if isinstance(json_bruto_viacep, str):
        dados_endereco = json.loads(json_bruto_viacep)
    else:
        dados_endereco = json_bruto_viacep

    if "erro" in dados_endereco:
        print("[!] Aviso: O JSON informado indica um CEP inexistente.")
        return None

    cep_formatado = dados_endereco.get("cep", "")
    chave_limpa = cep_formatado.replace("-", "").strip()

    if not chave_limpa:
        print("[!] Erro: Não foi possível identificar a chave 'cep' no JSON.")
        return None

    return {chave_limpa: dados_endereco}


def inserir_na_base_local(json_bruto_viacep, caminho_arquivo=NOME_ARQUIVO_PADRAO):
    """
    Converte o JSON bruto e atualiza o arquivo físico no disco.
    Retorna a base de dados consolidada e atualizada.
    """
    registro_convertido = converter_json_viacep(json_bruto_viacep)

    if not registro_convertido:
        return None

    base_dados = {}

    # 1. Carrega dados pré-existentes se o arquivo existir
    if os.path.exists(caminho_arquivo):
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            try:
                base_dados = json.load(arquivo)
            except json.JSONDecodeError:
                base_dados = {}

    # 2. Atualiza a estrutura em memória
    base_dados.update(registro_convertido)

    # 3. Grava o dicionário completo atualizado no arquivo JSON
    with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
        json.dump(base_dados, arquivo, ensure_ascii=False, indent=4)

    return base_dados