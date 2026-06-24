# Estudo-gcov

Framework experimental para avaliação de algoritmos de busca aplicados à localização de linhas executáveis e executadas em relatórios de cobertura sintéticos no formato GCOV.

## Objetivo

Este projeto foi desenvolvido para investigar o comportamento de diferentes algoritmos de busca quando aplicados a estruturas derivadas de arquivos de cobertura de código.

Os experimentos avaliam:

* Tempo médio de execução;
* Consumo de memória;
* Número médio de iterações;
* Influência do tamanho da entrada;
* Influência da distribuição dos dados.

## Algoritmos Avaliados

* Busca Binária
* Busca por Interpolação
* Binary Interpolation Search
* Interpolation Once Binary Search

## Estrutura do Projeto

```text
.
├── gerar_gcov.py
├── analisar_gcov.py
├── benchmark_busca.py
├── gerar_csv.py
│
│
├── algoritmos_bin/
│   ├── binary.c
│   ├── interpolation.c
│   ├── binary_interpolation.c
│   └── interpolation_once_binary.c
│
├── gcov_experiments/
│
├── benchmark_analise/
│
└── resultados.csv
```

## Fluxo Experimental

### 1. Geração dos arquivos GCOV

São produzidos relatórios sintéticos contendo diferentes:

* tamanhos de entrada;
* densidades de cobertura;
* distribuições de dados.

Distribuições implementadas:

* Uniform
* Cluster
* Biased
* Fault

### 2. Análise dos arquivos GCOV

O script `analisar_gcov.py` extrai:

* número de linhas executáveis;
* número de linhas executadas;
* número de linhas não executadas.

Os resultados são armazenados em arquivos `.txt` mantendo a mesma estrutura de diretórios dos arquivos GCOV originais.

### 3. Execução dos benchmarks

O script `benchmark_busca.py`:

* percorre todos os arquivos GCOV;
* gera estruturas temporárias de entrada;
* executa todos os algoritmos de busca;
* coleta métricas experimentais.

Métricas registradas:

* tempo médio (ns);
* memória média (KB);
* número médio de iterações.

### 4. Consolidação dos dados

O script `gerar_csv.py` converte os arquivos de análise em um único conjunto de dados tabular (`CSV`) para posterior análise estatística e visualização.

## Compilação

Utilizando GCC:

```bash
gcc -O3 binary.c -o binary
gcc -O3 interpolation.c -o interpolation
gcc -O3 binary_interpolation.c -o binary_interpolation
gcc -O3 interpolation_once_binary.c -o interpolation_once_binary
```

## Execução

### Gerar relatórios GCOV sintéticos

```bash
python3 gerar_gcov.py
```

### Extrair informações dos GCOVs

```bash
python3 analisar_gcov.py
```

### Executar benchmark

```bash
python3 benchmark_busca.py
```

### Gerar CSV consolidado

```bash
python3 gerar_csv.py
```

## Ambiente Utilizado

* Python 3.12+
* GCC
* Linux / WSL2
* Pandas
* Matplotlib

## Resultados

Os experimentos indicaram que:

* a Busca Binária apresentou o melhor desempenho temporal geral;
* algoritmos baseados em interpolação realizaram menos iterações;
* a distribuição dos dados influencia fortemente algoritmos que utilizam interpolação;
* distribuições uniformes favorecem métodos baseados em interpolação;
* a Busca Binária apresentou maior estabilidade frente às diferentes distribuições analisadas.

## Uso Acadêmico

Este projeto foi desenvolvido para fins de pesquisa e experimentação em algoritmos de busca e análise de cobertura de código.
