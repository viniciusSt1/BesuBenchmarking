import os
import re
import pandas as pd
from bs4 import BeautifulSoup

# Caminho da pasta com os relatórios HTML
REPORTS_DIR = "./reports_htmls/experiments"
# Pasta de saída para os CSVs gerados
OUTPUT_DIR = "./reports_csv/experiments"

# Cria a pasta base de saída, se não existir
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Função auxiliar para converter strings numéricas
def try_float(x):
    try:
        return float(x)
    except:
        return x

# Função para extrair o valor de TPS do nome do relatório
def extract_tps(report_name):
    match = re.search(r'_(\d+)_', report_name)
    return int(match.group(1)) if match else 0

# Percorre as subpastas (open, query, transfer)
for test_type in os.listdir(REPORTS_DIR):
    test_path = os.path.join(REPORTS_DIR, test_type)
    if not os.path.isdir(test_path):
        continue

    performance_data = []
    monitor_data = []

    # Percorre todos os arquivos HTML dentro da subpasta
    for filename in os.listdir(test_path):
        if not filename.endswith(".html"):
            continue

        filepath = os.path.join(test_path, filename)
        report_name = os.path.splitext(filename)[0]

        with open(filepath, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "lxml")

        # ---- TABELA DE PERFORMANCE ----
        perf_table = soup.find("h3", string=lambda s: s and "Performance metrics" in s)
        if perf_table:
            table = perf_table.find_next("table")
            headers = [th.text.strip() for th in table.find_all("th")]
            for row in table.find_all("tr")[1:]:
                values = [td.text.strip() for td in row.find_all("td")]
                if values:
                    record = dict(zip(headers, values))
                    record["Report"] = report_name
                    record["TPS"] = extract_tps(report_name)
                    performance_data.append(record)

        # ---- TABELA DE MONITORAMENTO ----
        monitor_table = soup.find("h4", string=lambda s: s and "Resource monitor" in s)
        if monitor_table:
            table = monitor_table.find_next("table").find_next("table")
            headers = [th.text.strip() for th in table.find_all("th")]
            for row in table.find_all("tr")[1:]:
                values = [td.text.strip() for td in row.find_all("td")]
                if values:
                    record = dict(zip(headers, values))
                    record["Report"] = report_name
                    record["TPS"] = extract_tps(report_name)
                    monitor_data.append(record)

    # ---- CRIA A PASTA DE SAÍDA PARA ESSE TIPO DE TESTE ----
    output_subdir = os.path.join(OUTPUT_DIR, test_type)
    os.makedirs(output_subdir, exist_ok=True)

    # ---- SALVA OS CSVs ORDENADOS PELO TPS ----
    if performance_data:
        perf_df = pd.DataFrame(performance_data)
        perf_df = perf_df.sort_values("TPS")
        perf_df.to_csv(os.path.join(output_subdir, "caliper_performance_metrics.csv"), index=False)

    if monitor_data:
        monitor_df = pd.DataFrame(monitor_data)
        monitor_df = monitor_df.sort_values("TPS")
        monitor_df.to_csv(os.path.join(output_subdir, "caliper_monitor_metrics.csv"), index=False)

    print(f"CSVs criados para '{test_type}' em {output_subdir}")
