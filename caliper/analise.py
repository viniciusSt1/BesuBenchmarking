import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

# Diretório base de experimentos
EXPERIMENTS_BASE = "reports_csv/experiments"

# Determinar quais experimentos processar
EXPERIMENTS_TO_PROCESS = []

if len(sys.argv) > 1:
    user_input = sys.argv[1]

    # Se o usuário passou um caminho completo, usar diretamente
    if os.path.isdir(user_input):
        EXPERIMENTS_TO_PROCESS = [user_input]
    # Se passou apenas o nome do experimento, procurar em experiments/
    elif os.path.isdir(os.path.join(EXPERIMENTS_BASE, user_input)):
        EXPERIMENTS_TO_PROCESS = [os.path.join(EXPERIMENTS_BASE, user_input)]
    else:
        print(f"Experimento nao encontrado: {user_input}")
        print(f"\nExperimentos disponiveis:")
        if os.path.isdir(EXPERIMENTS_BASE):
            exps = sorted(os.listdir(EXPERIMENTS_BASE))
            for exp in exps:
                if os.path.isdir(os.path.join(EXPERIMENTS_BASE, exp)):
                    print(f"  - {exp}")
        sys.exit(1)
else:
    # Sem argumentos: processar todos os experimentos
    if os.path.isdir(EXPERIMENTS_BASE):
        exps = sorted(os.listdir(EXPERIMENTS_BASE))
        for exp in exps:
            exp_path = os.path.join(EXPERIMENTS_BASE, exp)
            if os.path.isdir(exp_path):
                EXPERIMENTS_TO_PROCESS.append(exp_path)

    if not EXPERIMENTS_TO_PROCESS:
        print("Nenhum experimento encontrado em", EXPERIMENTS_BASE)
        sys.exit(1)

    print(f"Analisando {len(EXPERIMENTS_TO_PROCESS)} experimentos...\n")

# =====================
# Função para processar um experimento
# =====================
def process_experiment(BASE_DIR):
    perf_csv = os.path.join(BASE_DIR, "caliper_performance_metrics.csv")
    mon_csv = os.path.join(BASE_DIR, "caliper_monitor_metrics.csv")

    # Verifica se ambos os arquivos existem
    if not (os.path.exists(perf_csv) and os.path.exists(mon_csv)):
        print(f"Arquivos CSV nao encontrados em {BASE_DIR}")
        print(f"Esperado: {perf_csv} e {mon_csv}")
        return

    # -------------------
    # 1. Leitura dos dados
    # -------------------
    perf_df = pd.read_csv(perf_csv)
    mon_df = pd.read_csv(mon_csv)

    # Converte colunas numéricas relevantes
    num_cols_perf = [
        "Send Rate (TPS)",
        "Max Latency (s)",
        "Min Latency (s)",
        "Avg Latency (s)",
        "Throughput (TPS)",
        "TPS"
    ]
    for col in num_cols_perf:
        if col in perf_df.columns:
            perf_df[col] = pd.to_numeric(perf_df[col], errors="coerce")

    # Colunas conhecidas do monitoramento
    cpu_col = "CPU%(avg)"
    mem_col_gb = "Memory(avg) [GB]"
    mem_col_mb = "Memory(avg) [MB]"

    # Converte tipos numéricos
    for col in [cpu_col, mem_col_gb, mem_col_mb, "TPS"]:
        if col in mon_df.columns:
            mon_df[col] = pd.to_numeric(mon_df[col], errors="coerce")

    # Seleciona qual coluna de memória usar
    if mem_col_gb in mon_df.columns and mon_df[mem_col_gb].notna().sum() > 0:
        mon_df["Memory_used_GB"] = mon_df[mem_col_gb]
    elif mem_col_mb in mon_df.columns and mon_df[mem_col_mb].notna().sum() > 0:
        mon_df["Memory_used_GB"] = mon_df[mem_col_mb] / 1024
    else:
        print("Nenhuma coluna de memoria valida encontrada, pulando...\n")
        return

    # -------------------
    # 2. Processar por função (Name)
    # -------------------
    print(f"\n{'='*60}")
    print(f"Experimento: {os.path.basename(BASE_DIR)}")
    print(f"{'='*60}\n")

    # Processar cada função (open, query, transfer)
    for func_name in perf_df['Name'].unique():
        print(f"\nFuncao: {func_name.upper()}")
        print("-" * 40)

        # Filtrar dados dessa função
        perf_func = perf_df[perf_df['Name'] == func_name]

        if len(perf_func) == 0:
            print(f"Sem dados para {func_name}")
            continue

        # Mostrar métricas de performance
        print("\nPerformance:")
        for col in ["Send Rate (TPS)", "Throughput (TPS)", "Min Latency (s)", "Avg Latency (s)", "Max Latency (s)"]:
            if col in perf_func.columns:
                val = perf_func[col].iloc[0]
                print(f"  {col}: {val:.4f}")

        # Mostrar métricas de recursos
        print("\nRecursos (media entre nodes):")
        print(f"  CPU media: {mon_df[cpu_col].mean():.2f}%")
        print(f"  CPU maxima: {mon_df[cpu_col].max():.2f}%")
        print(f"  Memoria media: {mon_df['Memory_used_GB'].mean():.4f} GB")
        print(f"  Memoria maxima: {mon_df['Memory_used_GB'].max():.4f} GB")

        # Mostrar por nó
        print(f"\nPor no:")
        for _, row in mon_df.iterrows():
            print(f"  {row['Name']}: CPU={row[cpu_col]:.2f}%, Mem={row['Memory_used_GB']:.4f}GB")

# =====================
# Execução principal
# =====================
if __name__ == "__main__":
    for exp_path in EXPERIMENTS_TO_PROCESS:
        process_experiment(exp_path)
        if len(EXPERIMENTS_TO_PROCESS) > 1:
            print("\n" + "="*60 + "\n")
