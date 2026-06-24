import os
import re
import csv

# ==========================================
# CONFIGURAÇÃO
# ==========================================

ANALISE_DIR = "benchmark_analise"
CSV_SAIDA = "resultados_experimento.csv"

# ==========================================
# EXTRAI DADOS DE UM TXT
# ==========================================

def processar_txt(txt_path):

    with open(
        txt_path,
        "r",
        encoding="utf-8"
    ) as f:

        conteudo = f.read()

    # --------------------------------------
    # Categoria
    # Ex:
    # Categoria: L_64_P_30_biased
    # --------------------------------------

    categoria_match = re.search(
        r"Categoria:\s*L_(\d+)_P_(\d+)_(\w+)",
        conteudo
    )

    if not categoria_match:
        raise ValueError(
            f"Categoria não encontrada em {txt_path}"
        )

    L = int(
        categoria_match.group(1)
    )

    P = int(
        categoria_match.group(2)
    )

    tipo = (
        categoria_match.group(3)
        .strip()
    )

    # --------------------------------------
    # Nome do arquivo GCOV
    # Ex:
    # Arquivo GCOV: sim_001.gcov
    # --------------------------------------

    arquivo_match = re.search(
        r"Arquivo GCOV:\s*(sim_\d+)\.gcov",
        conteudo
    )

    if not arquivo_match:
        raise ValueError(
            f"Arquivo GCOV não encontrado em {txt_path}"
        )

    nome_base = (
        arquivo_match.group(1)
    )

    row_id = (
        f"{nome_base}"
        f"_L_{L}"
        f"_P_{P}"
        f"_{tipo}"
    )

    # --------------------------------------
    # Cobertura
    # --------------------------------------

    executaveis = int(
        re.search(
            r"Linhas executáveis:\s*(\d+)",
            conteudo
        ).group(1)
    )

    executadas = int(
        re.search(
            r"Linhas executadas:\s*(\d+)",
            conteudo
        ).group(1)
    )

    nao_executadas = int(
        re.search(
            r"Linhas não executadas:\s*(\d+)",
            conteudo
        ).group(1)
    )

    linha = {
        "row_id": row_id,
        "L": L,
        "P": P,
        "tipo": tipo,
        "linhas_executaveis": executaveis,
        "linhas_executadas": executadas,
        "linhas_nao_executadas": nao_executadas
    }

    # ======================================
    # ALGORITMOS
    # ======================================

    algoritmos = {

        "Busca Binária":
            "binary",

        "Busca por Interpolação":
            "interpolation",

        "Busca Binary+Interpolation":
            "binary_interpolation",

        "Busca Interpolation Once Binary":
            "interpolation_once_binary"
    }

    for nome_txt, prefixo in algoritmos.items():

        padrao = (
            rf"{re.escape(nome_txt)}"
            rf".*?"
            rf"Tempo médio \(ns\):\s*([\d.]+)"
            rf".*?"
            rf"Memória média \(KB\):\s*([\d.]+)"
            rf".*?"
            rf"Iterações médias:\s*([\d.]+)"
        )

        match = re.search(
            padrao,
            conteudo,
            re.DOTALL
        )

        if not match:

            raise ValueError(
                f"{nome_txt} não encontrado "
                f"em {txt_path}"
            )

        linha[
            f"{prefixo}_tempo_ns"
        ] = float(
            match.group(1)
        )

        linha[
            f"{prefixo}_memoria_kb"
        ] = float(
            match.group(2)
        )

        linha[
            f"{prefixo}_iteracoes"
        ] = float(
            match.group(3)
        )

    return linha

# ==========================================
# MAIN
# ==========================================

def main():

    registros = []

    for root, dirs, files in os.walk(
        ANALISE_DIR
    ):

        for file in files:

            if file.endswith(".txt"):

                txt_path = os.path.join(
                    root,
                    file
                )

                try:

                    registros.append(
                        processar_txt(
                            txt_path
                        )
                    )

                except Exception as e:

                    print(
                        f"ERRO: "
                        f"{txt_path}\n{e}\n"
                    )

    registros.sort(
        key=lambda x: x["row_id"]
    )

    if not registros:

        print(
            "Nenhum registro encontrado."
        )
        return

    colunas = [

        "row_id",

        "L",
        "P",
        "tipo",

        "linhas_executaveis",
        "linhas_executadas",
        "linhas_nao_executadas",

        "binary_tempo_ns",
        "binary_memoria_kb",
        "binary_iteracoes",

        "interpolation_tempo_ns",
        "interpolation_memoria_kb",
        "interpolation_iteracoes",

        "binary_interpolation_tempo_ns",
        "binary_interpolation_memoria_kb",
        "binary_interpolation_iteracoes",

        "interpolation_once_binary_tempo_ns",
        "interpolation_once_binary_memoria_kb",
        "interpolation_once_binary_iteracoes"
    ]

    with open(
        CSV_SAIDA,
        "w",
        newline="",
        encoding="utf-8"
    ) as csvfile:

        writer = csv.DictWriter(
            csvfile,
            fieldnames=colunas
        )

        writer.writeheader()

        for registro in registros:

            writer.writerow(
                registro
            )

    print(
        f"\nCSV gerado com sucesso:"
    )

    print(
        f"{CSV_SAIDA}"
    )

    print(
        f"Total de linhas:"
        f" {len(registros)}"
    )

if __name__ == "__main__":
    main()