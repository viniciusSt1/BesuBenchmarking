Instale as dependencias com:

```
npm install
```

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