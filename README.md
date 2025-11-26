## Requisitos

- Ambiente Linux
- Node.js 18+ (recomendado 20+)
- Docker e Docker Compose
- Python 3.8+
- jq (JSON processor)
- wget, curl, git

## Instalacao

Clone o repositorio e instale as dependencias:

```bash
git clone https://github.com/viniciusSt1/BesuBenchmarking.git
cd BesuBenchmarking
npm install
```

## Uso

Execute um experimento especifico:

```bash
./run-experiment.sh <nodes> <blocktime> <consensus> <version>

# Exemplo: 6 nos, 5s de bloco, QBFT, versao 25.10.0
./run-experiment.sh 6 5 qbft 25.10.0
```

Execute todos os experimentos da lista:

```bash
./run-all-experiments.sh
```

Analise os resultados:

```bash
cd caliper

# Analisar todos os experimentos
python3 analise.py

# Analisar experimento especifico
python3 analise.py 6n-5s-qbft-v25.10.0_20251124_204041
```