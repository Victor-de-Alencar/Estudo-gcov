import os
import json
import subprocess
import tempfile
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import as_completed

# ==========================================
# CONFIGURAÇÃO
# ==========================================

REPETICOES = 2000

GCOV_DIR = "gcov_experiments"
ANALISE_DIR = "benchmark_analise"

TEMP_DIR = "temp"
TEMP_FILE = os.path.join(
    TEMP_DIR,
    "busca_input.tmp"
)

ALGORITMOS = {
    "Busca Binária":
        "./algoritmos_bin/binary",

    "Busca por Interpolação":
        "./algoritmos_bin/interpolation",

    "Busca Binary+Interpolation":
        "./algoritmos_bin/binary_interpolation",

    "Busca Interpolation Once Binary":
        "./algoritmos_bin/interpolation_once_binary"
}

# ==========================================
# EXTRAÇÃO DOS VETORES
# ==========================================

def extrair_vetores(filepath):

    executaveis = []
    executadas = []

    with open(
        filepath,
        "r",
        encoding="utf-8"
    ) as f:

        for linha in f:

            partes = linha.split(":", 2)

            if len(partes) < 3:
                continue

            contador = partes[0].strip()
            numero = partes[1].strip()

            if numero == "0":
                continue

            try:
                numero_linha = int(numero)
            except ValueError:
                continue

            if contador == "-":
                continue

            executaveis.append(
                numero_linha
            )

            if contador != "#####":

                try:

                    if int(contador) > 0:

                        executadas.append(
                            numero_linha
                        )

                except ValueError:
                    pass

    return (
        sorted(executaveis),
        sorted(executadas)
    )

# ==========================================
# NOVO TEMPORÁRIO UNIFICADO
# ==========================================

def gerar_arquivo_temporario(
    vetor_executadas,
    vetor_executaveis
):

    temp = tempfile.NamedTemporaryFile(
        mode="w",
        delete=False,
        suffix=".tmp"
    )

    with temp as f:

        f.write(
            f"{len(vetor_executadas)}\n"
        )

        f.write(
            " ".join(
                map(
                    str,
                    vetor_executadas
                )
            )
        )

        f.write("\n")

        f.write(
            f"{len(vetor_executaveis)}\n"
        )

        f.write(
            " ".join(
                map(
                    str,
                    vetor_executaveis
                )
            )
        )

        f.write("\n")

        f.write(
            f"{REPETICOES}\n"
        )

    return temp.name

# ==========================================
# EXECUTA ALGORITMO
# ==========================================

def executar_algoritmo(
    executavel,
    temp_file
):

    resultado = subprocess.run(
        [executavel, temp_file],
        capture_output=True,
        text=True
    )

    if resultado.returncode != 0:

        raise RuntimeError(
            f"\nErro executando "
            f"{executavel}\n\n"
            f"{resultado.stderr}"
        )

    return json.loads(
        resultado.stdout
    )
# ==========================================
# PROCESSA UM ALGORITMO
# ==========================================

def processar_algoritmo(
    executavel,
    temp_file
):

    return executar_algoritmo(
        executavel,
        temp_file
    )

# ==========================================
# REGISTRA RESULTADOS
# ==========================================

def registrar_resultados(
    txt_path,
    resultados
):

    with open(
        txt_path,
        "a",
        encoding="utf-8"
    ) as f:

        f.write("\n\n")

        for nome_alg, dados in resultados.items():

            f.write(
                "=" * 40 + "\n"
            )

            f.write(
                nome_alg + "\n"
            )

            f.write(
                "=" * 40 + "\n\n"
            )

            f.write(
                f"Tempo médio (ns): "
                f"{dados['tempo_ns']:.3f}\n"
            )

            f.write(
                f"Memória média (KB): "
                f"{dados['memoria_kb']:.3f}\n"
            )

            f.write(
                f"Iterações médias: "
                f"{dados['iteracoes']:.3f}\n\n"
            )

# ==========================================
# PROCESSAR GCOV
# ==========================================

def processar_gcov(gcov_path):

    (
        vetor_executaveis,
        vetor_executadas
    ) = extrair_vetores(
        gcov_path
    )

    temp_file = gerar_arquivo_temporario(
        vetor_executadas,
        vetor_executaveis
    )

    try:

        rel_path = os.path.relpath(
            gcov_path,
            GCOV_DIR
        )

        txt_path = os.path.join(
            ANALISE_DIR,
            rel_path.replace(
                ".gcov",
                ".txt"
            )
        )

        resultados = {}

        for nome_alg, executavel in ALGORITMOS.items():

            resultados[nome_alg] = (
                processar_algoritmo(
                    executavel,
                    temp_file
                )
            )

        registrar_resultados(
            txt_path,
            resultados
        )

        return gcov_path

    finally:

        if os.path.exists(
            temp_file
        ):
            os.remove(
                temp_file
            )

# ==========================================
# MAIN
# ==========================================

def main():

    gcovs = []

    for root, dirs, files in os.walk(
        GCOV_DIR
    ):

        for file in files:

            if file.endswith(
                ".gcov"
            ):

                gcovs.append(
                    os.path.join(
                        root,
                        file
                    )
                )

    gcovs.sort()

    total_gcovs = len(gcovs)

    print(
        f"\nEncontrados "
        f"{total_gcovs} GCOVs.\n"
    )

    MAX_WORKERS = 8

    with ProcessPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        futuros = {

            executor.submit(
                processar_gcov,
                gcov
            ): gcov

            for gcov in gcovs
        }

        concluidos = 0

        for futuro in as_completed(
            futuros
        ):

            concluidos += 1

            try:

                gcov = futuro.result()

                print(
                    f"[{concluidos}/{total_gcovs}] "
                    f"Concluído: "
                    f"{os.path.basename(gcov)}"
                )

            except Exception as e:

                print(
                    f"\nERRO:\n{e}\n"
                )

    print(
        "\nBenchmark concluído."
    )

if __name__ == "__main__":
    main()