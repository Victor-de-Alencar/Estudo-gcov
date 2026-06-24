import os

GCOV_DIR = "gcov_experiments"
OUTPUT_DIR = "benchmark_analise"


def analisar_gcov(filepath):

    executaveis = 0
    executadas = 0
    nao_executadas = 0

    with open(filepath, "r", encoding="utf-8") as f:

        for linha in f:

            partes = linha.split(":", 2)

            if len(partes) < 3:
                continue

            contador = partes[0].strip()
            numero = partes[1].strip()

            # ignora cabeçalhos GCOV
            if numero == "0":
                continue

            if contador == "-":
                continue

            executaveis += 1

            if contador == "#####":

                nao_executadas += 1

            else:

                try:

                    if int(contador) > 0:
                        executadas += 1
                    else:
                        nao_executadas += 1

                except ValueError:
                    pass

    return (
        executaveis,
        executadas,
        nao_executadas
    )


for root, dirs, files in os.walk(GCOV_DIR):

    for file in files:

        if not file.endswith(".gcov"):
            continue

        gcov_path = os.path.join(root, file)

        (
            executaveis,
            executadas,
            nao_executadas
        ) = analisar_gcov(gcov_path)

        # caminho relativo dentro de gcov_experiments
        rel_dir = os.path.relpath(
            root,
            GCOV_DIR
        )

        # cria a mesma estrutura dentro de benchmark_analise
        output_subdir = os.path.join(
            OUTPUT_DIR,
            rel_dir
        )

        os.makedirs(
            output_subdir,
            exist_ok=True
        )

        output_file = os.path.join(
            output_subdir,
            file.replace(".gcov", ".txt")
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as out:

            out.write(
                f"Arquivo GCOV: {file}\n"
            )

            out.write(
                f"Categoria: {rel_dir}\n\n"
            )

            out.write(
                f"Linhas executáveis: "
                f"{executaveis}\n"
            )

            out.write(
                f"Linhas executadas: "
                f"{executadas}\n"
            )

            out.write(
                f"Linhas não executadas: "
                f"{nao_executadas}\n"
            )

        print(
            f"Analisado: {gcov_path}"
        )

print("\nAnálise concluída.")