#!/bin/bash
set -e  # para o script se algo falhar

# === CONFIGURAÇÕES ===
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUTPUT_DIR="$BASE_DIR/besu/Permissioned-Network"
IMAGE_NAME="besu-image-local:25.10.0"
NETWORK_NAME="besu-network"
IP="127.0.0.1"
START_RPC_HTTP_PORT=8545
START_RPC_WS_PORT=8645
START_METRICS_PORT=9545
START_P2P_PORT=30303

# Arquivo final do docker-compose
COMPOSE_FILE="$BASE_DIR/besu/docker-compose.yml"

# === CONTA QUANTOS NÓS EXISTEM ===
NUM_NODES=$(find "$OUTPUT_DIR" -maxdepth 1 -type d -name "Node-*" | wc -l)

if [ "$NUM_NODES" -eq 0 ]; then
  echo "Nenhum no encontrado em $OUTPUT_DIR. Execute primeiro o script de criacao de nos."
  exit 1
fi

echo "Gerando docker-compose.yml para $NUM_NODES nos..."

# === BUSCA AUTOMÁTICA DAS CHAVES PARA BOOTNODES ===
BOOTNODE1_KEY_FILE="$OUTPUT_DIR/Node-1/data/key.pub"
BOOTNODE3_KEY_FILE="$OUTPUT_DIR/Node-3/data/key.pub"

if [[ -f "$BOOTNODE1_KEY_FILE" && -f "$BOOTNODE3_KEY_FILE" ]]; then
  KEY1=$(<"$BOOTNODE1_KEY_FILE"); KEY1=${KEY1#0x}
  KEY3=$(<"$BOOTNODE3_KEY_FILE"); KEY3=${KEY3#0x}

  BOOTNODE1_PORT=$START_P2P_PORT
  BOOTNODE2_PORT=$((START_P2P_PORT + 2))
  BOOTNODES="enode://$KEY1@$IP:$BOOTNODE1_PORT,enode://$KEY3@$IP:$BOOTNODE2_PORT"
  echo "Bootnodes detectados automaticamente:"
  echo "  Node-1 -> $KEY1:$BOOTNODE1_PORT"
  echo "  Node-3 -> $KEY3:$BOOTNODE2_PORT"
else
  echo "Nao foi possivel encontrar as chaves de Node-1 e Node-3"
  echo "Bootnodes serao deixados em branco."
  BOOTNODES=""
fi

# === CABEÇALHO DO DOCKER-COMPOSE ===
cat <<EOF > "$COMPOSE_FILE"
version: "3.8"

services:
EOF

# === LOOP PARA GERAR CADA SERVIÇO ===
for i in $(seq 1 "$NUM_NODES"); do
  RPC_HTTP_PORT=$((START_RPC_HTTP_PORT + i - 1))
  RPC_WS_PORT=$((START_RPC_WS_PORT + i - 1))
  METRICS_PORT=$((START_METRICS_PORT + i - 1))
  P2P_PORT=$((START_P2P_PORT + i - 1))

  NODE_NAME="node-besu${i}"
  NODE_PATH="$OUTPUT_DIR/Node-${i}/data"

  echo "  Gerando config para $NODE_NAME (RPC: $RPC_HTTP_PORT, P2P: $P2P_PORT)..."

  # O Node-1 não usa bootnodes; os demais sim
  if [ "$i" -eq 1 ] || [ -z "$BOOTNODES" ]; then
    BOOTNODE_CMD=""
  else
    BOOTNODE_CMD="--bootnodes=$BOOTNODES"
  fi

cat <<EOF >> "$COMPOSE_FILE"
  node${i}:
    image: ${IMAGE_NAME}
    container_name: ${NODE_NAME}
    network_mode: "host"
    command: >
      --data-path=/opt/besu/data
      --genesis-file=/opt/besu/genesis.json
      ${BOOTNODE_CMD}
      --rpc-http-enabled
      --host-allowlist="*"
      --rpc-http-cors-origins="all"
      --profile=ENTERPRISE
      --metrics-enabled
      --rpc-http-host=0.0.0.0
      --rpc-http-api=WEB3,ETH,NET,TRACE,DEBUG,ADMIN,TXPOOL,PERM,QBFT
      --rpc-ws-api=WEB3,ETH,NET,TRACE,DEBUG,ADMIN,TXPOOL,PERM,QBFT
      --data-storage-format=BONSAI
      --tx-pool-min-gas-price=0
      --min-gas-price=0
      --rpc-ws-enabled=true
      --rpc-ws-port=${RPC_WS_PORT}
      --tx-pool-limit-by-account-percentage=1
      --tx-pool-max-size=4096
      --metrics-port=${METRICS_PORT}
      --p2p-port=${P2P_PORT}
      --rpc-http-port=${RPC_HTTP_PORT}
      --permissions-accounts-config-file-enabled
      --permissions-nodes-config-file-enabled
    volumes:
      - ${OUTPUT_DIR}/genesis.json:/opt/besu/genesis.json
      - ${NODE_PATH}:/opt/besu/data

EOF
done

# === ADICIONA REDE EXTERNA ===
cat <<EOF >> "$COMPOSE_FILE"
networks:
  default:
    name: ${NETWORK_NAME}
    external: true
EOF

echo "docker-compose.yml criado com sucesso em $COMPOSE_FILE"
