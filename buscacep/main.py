"""
===============================================================================
ARQUIVO PRINCIPAL: main.py (SISTEMA DE ETL COM LIMPEZA DE STAGING AREA)
===============================================================================
CONCEITO CHAVE EM CIÊNCIA DE DADOS: ETL + Limpeza de Staging Area
-------------------------------------------------------------------------------
1. EXTRACT (Extração) : Lê dados brutos de 'novo.json'.
2. TRANSFORM (Transformação) : Limpa e padroniza a estrutura no 'converter.py'.
3. LOAD (Carga) : Salva o registro consolidado no 'ceps.json'.
4. CLEANUP (Limpeza) : Esvazia o 'novo.json' para evitar reprocessamento duplo.
===============================================================================
"""

import json
import os

# Importação do módulo de conversão
from buscacep.converter import converter_json_viacep, inserir_na_base_local

# Constantes de configuração de arquivos
ARQUIVO_BASE = "ceps.json"       # Repositório Final (Load)
ARQUIVO_ENTRADA = "novo.json"   # Staging Area (Extract)


def limpar_arquivo_entrada(caminho_arquivo=ARQUIVO_ENTRADA):
    """
    BOA PRÁTICA DE ETL (CLEANUP):
    Abre o arquivo de entrada no modo 'w' (write/escrita).
    O modo 'w' apaga todo o conteúdo existente do arquivo, deixando-o zerado
    para a próxima inserção de dados.
    """
    try:
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            f.write("")  # Escreve uma string vazia (zerando o arquivo)
        print(f"[4/4] CLEANUP  : O arquivo '{caminho_arquivo}' foi esvaziado com sucesso.")
    except Exception as erro:
        print(f"[!] Erro ao tentar limpar o arquivo '{caminho_arquivo}': {erro}")


def inspecionar_arquivo_disco():
    """Lê o arquivo 'ceps.json' do disco e exibe seu conteúdo no terminal."""
    if os.path.exists(ARQUIVO_BASE):
        with open(ARQUIVO_BASE, "r", encoding="utf-8") as f:
            conteudo_real = f.read()

        print("\n" + "=" * 50)
        print(f" [PROVA REAL] CONTEÚDO GRAVADO NO DISCO ({ARQUIVO_BASE}):")
        print("=" * 50)
        print(conteudo_real if conteudo_real.strip() else "{ } (Arquivo vazio)")
        print("=" * 50)
    else:
        print(f"\n[!] O arquivo '{ARQUIVO_BASE}' ainda não existe no disco.")


def consultar_cep_local(cep_digitado):
    """Busca um CEP no dicionário do arquivo 'ceps.json'."""
    cep_limpo = cep_digitado.replace("-", "").strip()

    if len(cep_limpo) != 8 or not cep_limpo.isdigit():
        print("\n[!] Erro: Digite um CEP válido com 8 números.")
        return

    if not os.path.exists(ARQUIVO_BASE):
        print(f"\n[!] Erro: A base de dados '{ARQUIVO_BASE}' ainda não existe.")
        return

    try:
        with open(ARQUIVO_BASE, "r", encoding="utf-8") as arquivo:
            base_dados = json.load(arquivo)

        if cep_limpo in base_dados:
            endereco = base_dados[cep_limpo]
            print("\n" + "=" * 50)
            print("       ENDEREÇO ENCONTRADO NA BASE CONSOLIDADA     ")
            print("=" * 50)
            print(f"CEP        : {endereco.get('cep')}")
            print(f"Logradouro : {endereco.get('logradouro')}")
            print(f"Bairro     : {endereco.get('bairro')}")
            print(f"Cidade     : {endereco.get('localidade')}")
            print(f"Estado     : {endereco.get('uf')}")
            print(f"DDD        : {endereco.get('ddd')}")
            print("=" * 50)
        else:
            print(f"\n[!] O CEP '{cep_digitado}' não consta na base local.")

    except json.JSONDecodeError:
        print(f"\n[!] Erro: O arquivo '{ARQUIVO_BASE}' está corrompido ou malformatado.")


def fluxo_processamento_etl():
    """Executa as etapas de Extract, Transform, Load e Cleanup."""
    print("\n" + "-" * 50)
    print("      INICIANDO PIPELINE DE ETL EM CIÊNCIA DE DADOS     ")
    print("-" * 50)

    # 1. EXTRACT
    if not os.path.exists(ARQUIVO_ENTRADA):
        print(f"[!] [EXTRACT FALHOU]: O arquivo '{ARQUIVO_ENTRADA}' não existe.")
        return

    try:
        with open(ARQUIVO_ENTRADA, "r", encoding="utf-8") as arquivo:
            conteudo_json_bruto = arquivo.read()

        if not conteudo_json_bruto.strip():
            print(f"[!] [EXTRACT FALHOU]: O arquivo '{ARQUIVO_ENTRADA}' já está vazio.")
            print("Cole um novo CEP no 'novo.json' antes de rodar a opção [2].")
            return

        print(f"[1/4] EXTRACT  : Dados extraídos de '{ARQUIVO_ENTRADA}'.")

        # 2 & 3. TRANSFORM & LOAD
        print("[2/4] TRANSFORM: Limpando chaves no 'converter.py'...")
        print(f"[3/4] LOAD     : Atualizando arquivo '{ARQUIVO_BASE}'...")

        resultado = inserir_na_base_local(conteudo_json_bruto, ARQUIVO_BASE)

        if resultado:
            # 4. CLEANUP (Esvazia o arquivo de entrada)
            limpar_arquivo_entrada(ARQUIVO_ENTRADA)

            print("-" * 50)
            print("     PIPELINE DE ETL CONCLUÍDO COM SUCESSO!     ")
            print("-" * 50)

            # Exibe o conteúdo real gravado no repositório final
            inspecionar_arquivo_disco()

    except Exception as erro:
        print(f"[!] ERRO NO PIPELINE: {erro}")


def menu_principal():
    """Interface interativa do menu."""
    while True:
        print("\n" + "=" * 50)
        print("   SISTEMA DE PROCESSAMENTO DE DADOS (ETL DE CEPS)")
        print("=" * 50)
        print("[ 1 ] Consultar CEP na base consolidada (ceps.json)")
        print("[ 2 ] Executar Pipeline ETL ('novo.json' -> 'ceps.json')")
        print("[ 3 ] Inspecionar arquivo 'ceps.json' direto do disco")
        print("[ 4 ] Sair do sistema")
        print("=" * 50)

        opcao = input("Escolha uma opção (1, 2, 3 ou 4): ").strip()

        if opcao == "1":
            cep_input = input("\nDigite o CEP para busca (ex: 01230000): ")
            consultar_cep_local(cep_input)

        elif opcao == "2":
            fluxo_processamento_etl()

        elif opcao == "3":
            inspecionar_arquivo_disco()

        elif opcao == "4":
            print("\nEncerrando a aplicação... Bons estudos!")
            break

        else:
            print("\n[!] Opção inválida. Digite 1, 2, 3 ou 4.")


if __name__ == "__main__":
    menu_principal()