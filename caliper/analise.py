import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

EXPERIMENTS_BASE = "reports_csv/experiments"
OUTPUT_DIR = "analysis_results"

os.makedirs(OUTPUT_DIR, exist_ok=True)

FUNCTIONS = ["open", "query", "transfer"]

# =====================
# Funções auxiliares
# =====================

def load_csvs(func_dir):
    perf = os.path.join(func_dir, "caliper_performance_metrics.csv")
    mon = os.path.join(func_dir, "caliper_monitor_metrics.csv")

    if not (os.path.isfile(perf) and os.path.isfile(mon)):
        return None, None

    return pd.read_csv(perf), pd.read_csv(mon)


def normalize_monitor_df(mon_df):
    # CPU
    if "CPU%(avg)" in mon_df.columns:
        mon_df["CPU"] = pd.to_numeric(mon_df["CPU%(avg)"], errors="coerce")

    # Memória
    if "Memory(avg) [GB]" in mon_df.columns:
        mon_df["Memory_GB"] = pd.to_numeric(mon_df["Memory(avg) [GB]"], errors="coerce")
    elif "Memory(avg) [MB]" in mon_df.columns:
        mon_df["Memory_GB"] = (
            pd.to_numeric(mon_df["Memory(avg) [MB]"], errors="coerce") / 1024
        )

    return mon_df


# =====================
# Análise por experimento
# =====================

def analyze_experiment(exp_path):
    exp_name = os.path.basename(exp_path)
    print(f"\n{'='*80}")
    print(f"EXPERIMENTO: {exp_name}")
    print(f"{'='*80}")

    results = []

    for func in FUNCTIONS:
        func_dir = os.path.join(exp_path, func)
        if not os.path.isdir(func_dir):
            continue

        perf_df, mon_df = load_csvs(func_dir)
        if perf_df is None:
            print(f"  {func}: CSVs nao encontrados, pulando...")
            continue

        # Conversões numéricas
        for col in [
            "Send Rate (TPS)",
            "Throughput (TPS)",
            "Avg Latency (s)",
            "Min Latency (s)",
            "Max Latency (s)",
            "TPS",
        ]:
            if col in perf_df.columns:
                perf_df[col] = pd.to_numeric(perf_df[col], errors="coerce")

        mon_df = normalize_monitor_df(mon_df)

        print(f"\n▶ FUNCAO: {func.upper()}")
        print("-" * 60)

        for tps in sorted(perf_df["TPS"].unique()):
            df_tps = perf_df[perf_df["TPS"] == tps]

            throughput = df_tps["Throughput (TPS)"].mean()
            latency = df_tps["Avg Latency (s)"].mean()

            cpu_avg = mon_df["CPU"].mean()
            cpu_max = mon_df["CPU"].max()
            mem_avg = mon_df["Memory_GB"].mean()
            mem_max = mon_df["Memory_GB"].max()

            print(
                f"TPS={tps:>4} | "
                f"Throughput={throughput:8.2f} | "
                f"Latency={latency:6.3f}s | "
                f"CPU(avg/max)={cpu_avg:5.1f}/{cpu_max:5.1f}% | "
                f"Mem(avg/max)={mem_avg:.3f}/{mem_max:.3f} GB"
            )

            results.append({
                "Experiment": exp_name,
                "Function": func,
                "TPS": tps,
                "Throughput_TPS": throughput,
                "Avg_Latency_s": latency,
                "CPU_avg_%": cpu_avg,
                "CPU_max_%": cpu_max,
                "Mem_avg_GB": mem_avg,
                "Mem_max_GB": mem_max,
            })

    return pd.DataFrame(results) if results else None


# =====================
# Gráficos
# =====================

def plot_metrics(df, exp_name):
    for func in df["Function"].unique():
        df_f = df[df["Function"] == func].sort_values("TPS")

        # Throughput
        plt.figure()
        plt.plot(df_f["TPS"], df_f["Throughput_TPS"], marker="o")
        plt.xlabel("TPS configurado")
        plt.ylabel("Throughput (TPS)")
        plt.title(f"{exp_name} | {func.upper()} | Throughput")
        plt.grid(True)
        plt.savefig(f"{OUTPUT_DIR}/{exp_name}_{func}_throughput.png")
        plt.close()

        # Latência
        plt.figure()
        plt.plot(df_f["TPS"], df_f["Avg_Latency_s"], marker="o")
        plt.xlabel("TPS configurado")
        plt.ylabel("Latencia media (s)")
        plt.title(f"{exp_name} | {func.upper()} | Latencia")
        plt.grid(True)
        plt.savefig(f"{OUTPUT_DIR}/{exp_name}_{func}_latency.png")
        plt.close()


# =====================
# Execução principal
# =====================

def main():
    experiments = []

    if len(sys.argv) > 1:
        exp = sys.argv[1]
        path = os.path.join(EXPERIMENTS_BASE, exp)
        if not os.path.isdir(path):
            print(f"Experimento nao encontrado: {exp}")
            sys.exit(1)
        experiments.append(path)
    else:
        experiments = [
            os.path.join(EXPERIMENTS_BASE, d)
            for d in sorted(os.listdir(EXPERIMENTS_BASE))
            if os.path.isdir(os.path.join(EXPERIMENTS_BASE, d))
        ]

    all_results = []

    for exp in experiments:
        df = analyze_experiment(exp)
        if df is not None:
            all_results.append(df)
            plot_metrics(df, os.path.basename(exp))

    if all_results:
        final_df = pd.concat(all_results, ignore_index=True)
        final_df.to_csv(f"{OUTPUT_DIR}/summary_all_experiments.csv", index=False)
        print(f"\nResumo consolidado salvo em {OUTPUT_DIR}/summary_all_experiments.csv")

    print("\nAnalise concluida com sucesso.")


if __name__ == "__main__":
    main()
