import os
import pandas as pd
import matplotlib.pyplot as plt

# Caminho base dos relatórios
BASE_DIR = "./6nos5bps2510/reports_csv"
FUNCTIONS = ["open", "query", "transfer"]

# =====================
# Função para processar uma pasta
# =====================
def process_function(func_name):
    print(f"\n🔍 Processando função: {func_name.upper()}")
    report_dir = os.path.join(BASE_DIR, func_name)
    perf_csv = os.path.join(report_dir, "caliper_performance_metrics.csv")
    mon_csv = os.path.join(report_dir, "caliper_monitor_metrics.csv")

    # Verifica se ambos os arquivos existem
    if not (os.path.exists(perf_csv) and os.path.exists(mon_csv)):
        print(f"⚠️ Arquivos CSV não encontrados em {report_dir}, pulando...\n")
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
        print("⚠️ Nenhuma coluna de memória válida encontrada, pulando...\n")
        return

    # -------------------
    # 2. Agrupar por TPS e calcular médias
    # -------------------
    perf_grouped = (
        perf_df.groupby("TPS")[["Send Rate (TPS)", "Min Latency (s)", "Avg Latency (s)", "Max Latency (s)", "Throughput (TPS)"]]
        .mean()
        .reset_index()
    )

    mon_grouped = (
        mon_df.groupby("TPS")[["Memory_used_GB", cpu_col]]
        .mean()
        .reset_index()
    )

    # Junta tudo em uma tabela resumo
    summary = pd.merge(perf_grouped, mon_grouped, on="TPS", how="inner")

    # -------------------
    # 3. Mostrar tabela na tela
    # -------------------
    print("\n📊 Tabela de médias por TPS:")
    print(summary.to_string(index=False, float_format=lambda x: f"{x:,.4f}"))

    # -------------------
    # 4. Gráficos
    # -------------------
    plt.figure(figsize=(10, 6))
    plt.plot(summary["TPS"], summary["Avg Latency (s)"], marker="o", label="Latência Média")
    plt.plot(summary["TPS"], summary["Max Latency (s)"], marker="o", linestyle="--", label="Latência Máxima")
    plt.plot(summary["TPS"], summary["Min Latency (s)"], marker="o", linestyle="--", label="Latência Mínima")
    plt.title(f"{func_name.upper()} - TPS × Latências (s)")
    plt.xlabel("TPS")
    plt.ylabel("Tempo (s)")
    plt.legend()
    plt.grid(True)
    plt.show()

    plt.figure(figsize=(10, 6))
    plt.plot(summary["TPS"], summary["Send Rate (TPS)"], marker="o", color="orange", label="Send Rate (TPS)")
    plt.plot(summary["TPS"], summary["Throughput (TPS)"], marker="o", color="green", label="Throughput (TPS)")
    plt.title(f"{func_name.upper()} - TPS × Send Rate / Throughput")
    plt.xlabel("TPS")
    plt.ylabel("TPS")
    plt.legend()
    plt.grid(True)
    plt.show()

    plt.figure(figsize=(10, 6))
    plt.plot(summary["TPS"], summary[cpu_col], marker="o", color="red")
    plt.title(f"{func_name.upper()} - TPS × CPU Média (%)")
    plt.xlabel("TPS")
    plt.ylabel("CPU Média (%)")
    plt.grid(True)
    plt.show()

    plt.figure(figsize=(10, 6))
    plt.plot(summary["TPS"], summary["Memory_used_GB"], marker="o", color="purple")
    plt.title(f"{func_name.upper()} - TPS × Memória Média (GB)")
    plt.xlabel("TPS")
    plt.ylabel("Memória Média (GB)")
    plt.grid(True)
    plt.show()

# =====================
# Execução principal
# =====================
if __name__ == "__main__":
    for func in FUNCTIONS:
        process_function(func)
