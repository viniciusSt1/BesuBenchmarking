import os
import re
import pandas as pd
from bs4 import BeautifulSoup

# ==========================================
# CONFIGURACOES
# ==========================================

# Diretório base onde ficam os experimentos
REPORTS_DIR = "./reports_htmls/experiments"

# Diretório base de saída para CSVs
OUTPUT_DIR = "./reports_csv/experiments"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================================
# FUNCOES AUXILIARES
# ==========================================

def extract_tps(report_name: str):
    """
    Extrai o TPS do nome do arquivo HTML.
    Ex: open_tps160.html -> 160
    """
    match = re.search(r"tps(\d+)", report_name.lower())
    return int(match.group(1)) if match else None


def try_float(x):
    """
    Tenta converter string para float quando possível
    """
    try:
        return float(x)
    except:
        return x


# ==========================================
# PROCESSAMENTO
# ==========================================

print("🔍 Iniciando extração de CSVs do Caliper...\n")

# Percorre todos os experimentos
for experiment in sorted(os.listdir(REPORTS_DIR)):
    experiment_path = os.path.join(REPORTS_DIR, experiment)

    if not os.path.isdir(experiment_path):
        continue

    print(f"📁 Processando experimento: {experiment}")

    # Percorre os tipos de teste (open, query, transfer)
    for test_type in sorted(os.listdir(experiment_path)):
        test_path = os.path.join(experiment_path, test_type)

        if not os.path.isdir(test_path):
            continue

        performance_data = []
        monitor_data = []

        # Percorre os relatórios HTML
        for filename in sorted(os.listdir(test_path)):
            if not filename.endswith(".html"):
                continue

            filepath = os.path.join(test_path, filename)
            report_name = os.path.splitext(filename)[0]
            tps = extract_tps(report_name)

            if tps is None:
                print(f"⚠️  TPS não identificado em {filename}, ignorando...")
                continue

            with open(filepath, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "lxml")

            # ===============================
            # TABELA DE PERFORMANCE
            # ===============================
            perf_table = soup.find(
                "h3", string=lambda s: s and "Performance metrics" in s
            )

            if perf_table:
                table = perf_table.find_next("table")
                headers = [th.text.strip() for th in table.find_all("th")]

                for row in table.find_all("tr")[1:]:
                    values = [td.text.strip() for td in row.find_all("td")]
                    if not values:
                        continue

                    record = dict(zip(headers, values))
                    record["Experiment"] = experiment
                    record["TestType"] = test_type
                    record["TPS"] = tps
                    record["Report"] = report_name

                    performance_data.append(record)

            # ===============================
            # TABELA DE MONITORAMENTO
            # ===============================
            monitor_table = soup.find(
                "h4", string=lambda s: s and "Resource monitor" in s
            )

            if monitor_table:
                table = monitor_table.find_next("table").find_next("table")
                headers = [th.text.strip() for th in table.find_all("th")]

                for row in table.find_all("tr")[1:]:
                    values = [td.text.strip() for td in row.find_all("td")]
                    if not values:
                        continue

                    record = dict(zip(headers, values))
                    record["Experiment"] = experiment
                    record["TestType"] = test_type
                    record["TPS"] = tps
                    record["Report"] = report_name

                    monitor_data.append(record)

        # ===============================
        # SALVAR CSVs
        # ===============================
        output_subdir = os.path.join(OUTPUT_DIR, experiment, test_type)
        os.makedirs(output_subdir, exist_ok=True)

        if performance_data:
            perf_df = pd.DataFrame(performance_data)
            perf_df = perf_df.sort_values("TPS")
            perf_df.to_csv(
                os.path.join(output_subdir, "caliper_performance_metrics.csv"),
                index=False
            )

        if monitor_data:
            monitor_df = pd.DataFrame(monitor_data)
            monitor_df = monitor_df.sort_values("TPS")
            monitor_df.to_csv(
                os.path.join(output_subdir, "caliper_monitor_metrics.csv"),
                index=False
            )

        print(f"  ✅ CSVs gerados para '{test_type}'")

    print()

print("🎉 Extração finalizada com sucesso!")
print(f"📂 CSVs disponíveis em: {OUTPUT_DIR}")
