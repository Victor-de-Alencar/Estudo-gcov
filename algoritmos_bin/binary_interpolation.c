#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <sys/resource.h>

typedef struct {
    long iteracoes;
} SearchMetrics;


int binary_interpolation_search(
    int *array,
    int n,
    int X,
    SearchMetrics *metrics
) {

    int left = 0;
    int right = n - 1;

    while (
        left <= right &&
        X >= array[left] &&
        X <= array[right]
    ) {

        metrics->iteracoes++;

        if (array[left] == array[right]) {

            if (array[left] == X)
                return left;

            return -1;
        }

        int Inter =
            left +
            ((double)(X - array[left]) *
             (right - left))
            /
            (array[right] - array[left]);

        if (Inter < left || Inter > right)
            return -1;

        if (array[Inter] == X)
            return Inter;

        if (X > array[Inter]) {

            int Mid =
                (Inter + right) / 2;

            if (X <= array[Mid]) {

                left = Inter + 1;
                right = Mid;

            } else {

                left = Mid + 1;
            }
        }

        else {

            int Mid =
                (left + Inter) / 2;

            if (X >= array[Mid]) {

                left = Mid;
                right = Inter - 1;

            } else {

                right = Mid - 1;
            }
        }
    }

    if (
        left < n &&
        array[left] == X
    ) {
        return left;
    }

    return -1;
}


/*--------------------------------------------------
  Tempo em nanossegundos
--------------------------------------------------*/
long long current_time_ns() {

    struct timespec ts;

    clock_gettime(
        CLOCK_MONOTONIC,
        &ts
    );

    return
        (long long)ts.tv_sec * 1000000000LL +
        ts.tv_nsec;
}


/*--------------------------------------------------
  Memória RSS
--------------------------------------------------*/
long get_memory_kb() {

    struct rusage usage;

    getrusage(
        RUSAGE_SELF,
        &usage
    );

    return usage.ru_maxrss;
}


/*--------------------------------------------------
  Main
--------------------------------------------------*/
int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        fprintf(stderr,
                "Uso: %s arquivo_entrada\n",
                argv[0]);
        return 1;
    }

    FILE *f = fopen(argv[1], "r");

    if (!f)
    {
        perror("Erro ao abrir arquivo");
        return 1;
    }

    /*----------------------------------
      vetor_executadas
    -----------------------------------*/

    int n_executadas;

    fscanf(
        f,
        "%d",
        &n_executadas
    );

    int *executadas =
        malloc(
            sizeof(int)
            * n_executadas
        );

    if (!executadas)
    {
        fclose(f);
        return 1;
    }

    for (
        int i = 0;
        i < n_executadas;
        i++
    )
    {
        fscanf(
            f,
            "%d",
            &executadas[i]
        );
    }

    /*----------------------------------
      vetor_executaveis
    -----------------------------------*/

    int n_executaveis;

    fscanf(
        f,
        "%d",
        &n_executaveis
    );

    int *executaveis =
        malloc(
            sizeof(int)
            * n_executaveis
        );

    if (!executaveis)
    {
        free(executadas);
        fclose(f);
        return 1;
    }

    for (
        int i = 0;
        i < n_executaveis;
        i++
    )
    {
        fscanf(
            f,
            "%d",
            &executaveis[i]
        );
    }

    /*----------------------------------
      repetições
    -----------------------------------*/

    int repeticoes;

    fscanf(
        f,
        "%d",
        &repeticoes
    );

    fclose(f);

    /*----------------------------------
      benchmark
    -----------------------------------*/

    SearchMetrics metrics;

    metrics.iteracoes = 0;

    long long inicio =
        current_time_ns();

    for (
        int alvo_idx = 0;
        alvo_idx < n_executaveis;
        alvo_idx++
    )
    {
        int alvo =
            executaveis[alvo_idx];

        for (
            int r = 0;
            r < repeticoes;
            r++
        )
        {
            binary_interpolation_search(
                executadas,
                n_executadas,
                alvo,
                &metrics
            );
        }
    }

    long long fim =
        current_time_ns();

    long memoria =
        get_memory_kb();

    long long total_buscas =
        (long long)n_executaveis *
        repeticoes;

    double tempo_medio_ns =
        (double)(fim - inicio)
        / total_buscas;

    double iteracoes_medias =
        (double)metrics.iteracoes
        / total_buscas;

    printf(
        "{"
        "\"tempo_ns\":%.3f,"
        "\"memoria_kb\":%ld,"
        "\"iteracoes\":%.3f"
        "}\n",
        tempo_medio_ns,
        memoria,
        iteracoes_medias
    );

    free(executadas);
    free(executaveis);

    return 0;
}