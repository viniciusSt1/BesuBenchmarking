#!/bin/bash

# === CONFIGURÁVEIS ===
BASE_DIR="$(pwd)"  # Diretório atual
GENESIS_DIR="$BASE_DIR/networkFiles/genesis.json"
KEYS_DIR="$BASE_DIR/networkFiles/keys"
OUTPUT_DIR="$BASE_DIR/Permissioned-Network"
IP="127.0.0.1" # <<<<<<<< Edite o IP aqui
START_PORT=30303

# Garante que as pastas existem
mkdir -p "$OUTPUT_DIR"

# Limpa possíveis arquivos antigos
rm -f "$KEYS_DIR/.env"


# === GERA LISTA DE IDENTIFICADORES ===
cd "$KEYS_DIR" || exit 1
ls | grep 0x > .env

# === VARIÁVEIS DE ACUMULAÇÃO ===
accounts_allowlist=""
nodes_allowlist=""
node_index=1
port=$START_PORT

while IFS= read -r identifier; do
    account_id="$identifier"

    # Lê o conteúdo do key.pub (removendo 0x do início)
    pub_key=$(<"$identifier/key.pub")
    pub_key=${pub_key#0x}

    # Monta enode string
    enode="enode://$pub_key@$IP:$port"

    # Adiciona vírgulas se necessário
    if [ $node_index -gt 1 ]; then
        accounts_allowlist+=","
        nodes_allowlist+=","
    fi

    accounts_allowlist+="\"$account_id\""
    nodes_allowlist+="\"$enode\""

    # Cria diretório de destino
    NODE_DIR="$OUTPUT_DIR/Node-$node_index/data"
    mkdir -p "$NODE_DIR"

    # Copia chaves
    cp "$identifier/key" "$NODE_DIR/key"
    cp "$identifier/key.pub" "$NODE_DIR/key.pub"

    node_index=$((node_index+1))
    port=$((port+1))
done < .env

# === CRIA ARQUIVO permissions_config.toml ===
PERMISSIONS_CONFIG_PATH="$OUTPUT_DIR/permissions_config.toml"

cat <<EOF > "$PERMISSIONS_CONFIG_PATH"
nodes-allowlist=[$nodes_allowlist]
accounts-allowlist=[$accounts_allowlist]
EOF

# === COPIA permissions_config.toml PARA CADA NÓ ===
for i in $(seq 1 $((node_index-1))); do
    cp "$PERMISSIONS_CONFIG_PATH" "$OUTPUT_DIR/Node-$i/data/"
done

echo "Arquivo permissions_config.toml criado!"
echo "Chaves e permissões copiadas para cada nó!"
