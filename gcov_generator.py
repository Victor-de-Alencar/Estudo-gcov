import os
import math
import random
import argparse
import logging
import json
from datetime import datetime

# Configuração de log para experimentação científica
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def generate_uniform(L: int, A: int) -> set:
    """Distribui as linhas cobertas uniformemente por todo o espaço L."""
    return set(random.sample(range(1, L + 1), A))

def generate_clustered(L: int, A: int) -> set:
    """Cria hotspots de cobertura simulando loops fortemente executados."""
    covered = set()
    while len(covered) < A:
        # Escolhe um centro de cluster aleatório
        center = random.randint(1, L)
        # O tamanho do cluster varia, limitando-se ao que falta para cobrir A
        cluster_size = min(random.randint(10, 100), A - len(covered))
        
        start = max(1, center - cluster_size // 2)
        end = min(L, start + cluster_size)
        
        for i in range(start, end + 1):
            if len(covered) < A:
                covered.add(i)
    return covered

def generate_biased(L: int, A: int) -> set:
    """Aplica o Princípio de Pareto: 80% da execução em 20% do código."""
    covered = set()
    dense_region_size = max(1, int(L * 0.2))
    
    # Define os limites da região densa
    dense_start = random.randint(1, L - dense_region_size + 1)
    dense_end = dense_start + dense_region_size - 1
    
    hits_in_dense = int(A * 0.8)
    hits_in_sparse = A - hits_in_dense
    
    # Se a região densa for menor que a quantidade de hits, capamos o valor
    if hits_in_dense > dense_region_size:
        hits_in_sparse += (hits_in_dense - dense_region_size)
        hits_in_dense = dense_region_size

    # Popula região densa (20% do código)
    dense_candidates = list(range(dense_start, dense_end + 1))
    covered.update(random.sample(dense_candidates, hits_in_dense))
    
    # Popula região esparsa (80% do código)
    sparse_candidates = [x for x in range(1, L + 1) if x < dense_start or x > dense_end]
    if hits_in_sparse > len(sparse_candidates):
        hits_in_sparse = len(sparse_candidates)
    
    covered.update(random.sample(sparse_candidates, hits_in_sparse))
    return covered

def generate_fault_like(L: int, A: int) -> set:
    """Simula falhas reais: buracos inativos pequenos (1 a 4 linhas) espalhados no código."""
    U = L - A # Linhas NÃO cobertas necessárias
    uncovered = set()
    
    while len(uncovered) < U:
        block_start = random.randint(1, L)
        block_size = min(random.randint(1, 4), U - len(uncovered)) # Buracos de 1 a 4 linhas
        
        for i in range(block_start, min(L + 1, block_start + block_size)):
            if len(uncovered) < U:
                uncovered.add(i)
                
    # A cobertura é o complemento dos buracos
    return set(range(1, L + 1)) - uncovered

def write_gcov_report(filepath: str, L: int, covered: set, filename: str):
    """Gera um arquivo sintético no formato estrito GNU GCOV."""
    with open(filepath, 'w') as f:
        # Metadados do cabeçalho GCOV
        f.write(f"        -:    0:Source:{filename}.c\n")
        f.write(f"        -:    0:Graph:{filename}.gcno\n")
        f.write(f"        -:    0:Data:{filename}.gcda\n")
        f.write(f"        -:    0:Runs:1\n")
        
        for line_idx in range(1, L + 1):
            if line_idx in covered:
                # Contadores seguem distribuição exponencial (comum em execução real)
                exec_count = int(random.expovariate(1/1000)) + 1
                f.write(f"{exec_count:>9}: {line_idx:>4}:    int instrucao_alvo_{line_idx} = {line_idx};\n")
            else:
                # Linha não coberta (alvo primário da pesquisa)
                f.write(f"    #####: {line_idx:>4}:    if (falha_borda_{line_idx}) return -1;\n")

def main():
    parser = argparse.ArgumentParser(description="GCOV Synthetic Report Generator for Experimental Coverage Analysis")
    parser.add_argument("--outdir", type=str, default="gcov_experiments", help="Diretório de saída")
    parser.add_argument("--samples", type=int, default=35, help="N amostral por configuração (Poder Estatístico ANOVA)")
    parser.add_argument("--seed", type=int, default=42, help="Seed para reproducibilidade científica")
    args = parser.parse_args()

    random.seed(args.seed)
    
    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    sizes_L = [2**i for i in range(6, 17)] # 64 até 65536
    densities_P = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    strategies = {
        "uniform": generate_uniform,
        "cluster": generate_clustered,
        "biased": generate_biased,
        "fault": generate_fault_like
    }

    metadata = {
        "timestamp": datetime.now().isoformat(),
        "seed": args.seed,
        "samples_per_config": args.samples,
        "total_files_expected": len(sizes_L) * len(densities_P) * len(strategies) * args.samples,
        "experiments": []
    }

    logging.info(f"Iniciando framework de simulação. Gerando {metadata['total_files_expected']} artefatos GCOV.")

    experiment_id = 0
    
    for L in sizes_L:
        for P in densities_P:
            A = int(L * P)
            for strat_name, strat_func in strategies.items():
                
                # Configuração atual
                config_dir = os.path.join(args.outdir, f"L_{L}_P_{int(P*100)}_{strat_name}")
                os.makedirs(config_dir, exist_ok=True)
                
                config_meta = {
                    "L_total_lines": L,
                    "P_density": P,
                    "A_covered_lines": A,
                    "strategy": strat_name,
                    "files": []
                }
                
                for sample in range(1, args.samples + 1):
                    experiment_id += 1
                    covered_set = strat_func(L, A)
                    
                    filename = f"sim_{sample:03d}"
                    filepath = os.path.join(config_dir, f"{filename}.gcov")
                    
                    write_gcov_report(filepath, L, covered_set, filename)
                    config_meta["files"].append(filepath)
                
                metadata["experiments"].append(config_meta)
                logging.info(f"[L={L:>5} | P={P:.1f} | Strat={strat_name:<7}] -> {args.samples} amostras exportadas.")

    # Dump dos metadados para auditoria e reprodutibilidade
    with open(os.path.join(args.outdir, "experimental_design.json"), "w") as mfile:
        json.dump(metadata, mfile, indent=4)
        
    logging.info("Geração concluída. Metadados exportados em experimental_design.json.")

if __name__ == "__main__":
    main()