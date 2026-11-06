"""
===============================================================================
ARQUIVO PRINCIPAL: main.py (ETL DE CEPS COM EXTRAÇÃO DIRETO DA API VIACEP)
===============================================================================
1. EXTRACT   : busca o CEP na API do ViaCEP (viacep.py), em formato JSON.
2. TRANSFORM : valida e indexa os dados (converter.py).
3. LOAD      : grava no 'ceps.json', a base de dados local (converter.py).

Diferença para o projeto 'buscacep': não existe mais o 'novo.json'. Os dados
chegam direto da internet, então também não há etapa de limpeza (staging).
===============================================================================
"""

import json
import os

from converter import (
    NOME_ARQUIVO_PADRAO,
    converter_json_viacep,
    inserir_na_base_local,
    ler_base_local,
    normalizar_cep,
)
from viacep import ViaCepErro, buscar_cep

ARQUIVO_BASE = NOME_ARQUIVO_PADRAO  # Repositório local (Load)


def exibir_endereco(endereco, titulo):
    """Imprime um endereço no terminal."""
    print("\n" + "=" * 50)
    print(f"  {titulo}")
    print("=" * 50)
    print(f"CEP        : {endereco.get('cep')}")
    print(f"Logradouro : {endereco.get('logradouro')}")
    print(f"Bairro     : {endereco.get('bairro')}")
    print(f"Cidade     : {endereco.get('localidade')}")
    print(f"Estado     : {endereco.get('uf')}")
    print(f"DDD        : {endereco.get('ddd')}")
    print("=" * 50)


def inspecionar_arquivo_disco():
    """Lê o arquivo 'ceps.json' do disco e exibe seu conteúdo no terminal."""
    if os.path.exists(ARQUIVO_BASE):
        with open(ARQUIVO_BASE, "r", encoding="utf-8") as f:
            conteudo_real = f.read()

        print("\n" + "=" * 50)
        print(" [PROVA REAL] CONTEÚDO GRAVADO NO DISCO (ceps.json):")
        print("=" * 50)
        print(conteudo_real if conteudo_real.strip() else "{ } (Arquivo vazio)")
        print("=" * 50)
    else:
        print("\n[!] O arquivo 'ceps.json' ainda não existe no disco.")


def fluxo_processamento_etl(cep):
    """
    Executa Extract (API), Transform e Load para um CEP já normalizado.
    Retorna o endereço salvo ou None se algo falhar.
    """
    print("\n" + "-" * 50)
    print("      INICIANDO PIPELINE DE ETL (ORIGEM: VIACEP)     ")
    print("-" * 50)

    # 1. EXTRACT
    print(f"[1/3] EXTRACT  : Consultando https://viacep.com.br/ws/{cep}/json/ ...")
    try:
        resposta = buscar_cep(cep)
    except ViaCepErro as erro:
        print(f"[!] [EXTRACT FALHOU]: {erro}")
        return None

    # 2. TRANSFORM
    print("[2/3] TRANSFORM: Validando resposta e indexando pelo CEP...")
    registro = converter_json_viacep(resposta)
    if not registro:
        return None

    # 3. LOAD
    print("[3/3] LOAD     : Gravando no 'ceps.json'...")
    try:
        inserir_na_base_local(registro)
    except json.JSONDecodeError:
        print("[!] [LOAD FALHOU]: O 'ceps.json' está corrompido ou malformatado.")
        return None
    except OSError as erro:
        print(f"[!] [LOAD FALHOU]: Não foi possível gravar o arquivo: {erro}")
        return None

    print("-" * 50)
    print("     PIPELINE DE ETL CONCLUÍDO COM SUCESSO!     ")
    print("-" * 50)
    return next(iter(registro.values()))


def consultar_cep_local(cep_digitado):
    """
    Busca o CEP na base local. Se não existir, oferece buscar na web
    (e, se o usuário aceitar, o CEP passa a fazer parte da base local).
    """
    cep = normalizar_cep(cep_digitado)
    if cep is None:
        print("\n[!] Erro: Digite um CEP válido com 8 números.")
        return

    try:
        base_dados = ler_base_local()
    except json.JSONDecodeError:
        print("\n[!] Erro: O arquivo 'ceps.json' está corrompido ou malformatado.")
        return

    if cep in base_dados:
        exibir_endereco(base_dados[cep], "ENDEREÇO ENCONTRADO NA BASE LOCAL")
        return

    print(f"\n[!] O CEP '{cep_digitado.strip()}' não consta na base local.")
    resposta = input("Deseja buscá-lo no ViaCEP e salvá-lo na base? (s/n): ").strip().lower()
    if resposta == "s":
        endereco = fluxo_processamento_etl(cep)
        if endereco:
            exibir_endereco(endereco, "ENDEREÇO OBTIDO DO VIACEP E SALVO")


def cadastrar_cep_pela_web(cep_digitado):
    """Busca o CEP no ViaCEP e grava/atualiza na base local."""
    cep = normalizar_cep(cep_digitado)
    if cep is None:
        print("\n[!] Erro: Digite um CEP válido com 8 números.")
        return

    endereco = fluxo_processamento_etl(cep)
    if endereco:
        exibir_endereco(endereco, "ENDEREÇO OBTIDO DO VIACEP E SALVO")


def menu_principal():
    """Interface interativa do menu."""
    while True:
        print("\n" + "=" * 50)
        print("   SISTEMA DE PROCESSAMENTO DE DADOS (ETL DE CEPS)")
        print("=" * 50)
        print("[ 1 ] Consultar CEP na base local (ceps.json)")
        print("[ 2 ] Buscar CEP no ViaCEP e salvar na base local")
        print("[ 3 ] Inspecionar arquivo 'ceps.json' direto do disco")
        print("[ 4 ] Sair do sistema")
        print("=" * 50)

        opcao = input("Escolha uma opção (1, 2, 3 ou 4): ").strip()

        if opcao == "1":
            cep_input = input("\nDigite o CEP para busca (ex: 01001000): ")
            consultar_cep_local(cep_input)

        elif opcao == "2":
            cep_input = input("\nDigite o CEP a buscar na web (ex: 01001000): ")
            cadastrar_cep_pela_web(cep_input)

        elif opcao == "3":
            inspecionar_arquivo_disco()

        elif opcao == "4":
            print("\nEncerrando a aplicação... Bons estudos!")
            break

        else:
            print("\n[!] Opção inválida. Digite 1, 2, 3 ou 4.")


if __name__ == "__main__":
    menu_principal()
