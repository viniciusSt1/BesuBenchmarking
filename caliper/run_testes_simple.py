import os
import subprocess
from datetime import datetime

num_testes = 4
# Caminhos para cada configuração de função
BENCHMARK_FILES = {
    "open": "benchmarks/scenario-monitoring/Simple/config-open.yaml",
    "query": "benchmarks/scenario-monitoring/Simple/config-query.yaml",
    "transfer": "benchmarks/scenario-monitoring/Simple/config-transfer.yaml",
    #"simple": "benchmarks/scenario-monitoring/Simple/config.yaml",
    #"getLatestStatus": 'benchmarks/scenario-monitoring/NodeHealthMonitor/config-getLatestStatus.yaml',
    #"reportStatus": 'benchmarks/scenario-monitoring/NodeHealthMonitor/config-reportStatus.yaml',
    #"statusReports": 'benchmarks/scenario-monitoring/NodeHealthMonitor/config-statusReports.yaml'
}

TPS_LIST_OPEN = [60, 80, 100, 120, 140, 160, 180] #open
TPS_LIST_QUERY = [100, 200, 300, 400, 500, 600, 700] # query
TPS_LIST_TRANSFER = [50, 60, 70, 80, 90, 100, 110] # transfer
TPS_LIST = [10]

# Atualiza o valor de TPS no arquivo de benchmark YAML
def update_tps_in_file(file_path, tps):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    new_lines = []
    for line in lines:
        if line.strip().startswith("tps:"):
            new_lines.append(f"          tps: {tps}\n")
        else:
            new_lines.append(line)

    with open(file_path, 'w') as file:
        file.writelines(new_lines)

# Executa o Caliper para uma função e TPS
def run_test(tps, function_name, benchmark_file):
    update_tps_in_file(benchmark_file, tps)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report_dir = f"reports_htmls/{function_name}"
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"{function_name}_report_{tps}_{timestamp}.html")

    cmd = [
        'npx', 'caliper', 'launch', 'manager',
        '--caliper-workspace', './',
        '--caliper-benchconfig', benchmark_file,
        '--caliper-networkconfig', 'networks/besu/networkconfig.json',
        '--caliper-bind-sut', 'besu:latest',
        '--caliper-flow-skip-install'
    ]

    subprocess.run(cmd)

    if os.path.exists('report.html'):
        os.rename('report.html', report_path)
        print(f"✅ Relatório salvo em {report_path}")
    else:
        print(f"⚠️ Relatório não encontrado para {function_name} @ {tps} TPS.")

# Executa todos os testes
if __name__ == "__main__":
    for i in range(num_testes):
        for function_name, benchmark_file in BENCHMARK_FILES.items():
            match(function_name):
                case "open":
                    TPS_LIST=TPS_LIST_OPEN
                case "query":
                    TPS_LIST=TPS_LIST_QUERY
                case "transfer":
                    TPS_LIST=TPS_LIST_TRANSFER

            print(f"\n🚀 Iniciando testes para função: {function_name}")
            for tps in TPS_LIST:
                run_test(tps, function_name, benchmark_file)
    
    print("\n📊 Convertendo relatórios HTML para CSV...")
    subprocess.run(["python3", "extract_csv.py"])
    print("✅ Conversão concluída! CSVs gerados em ./reports_csv/")
