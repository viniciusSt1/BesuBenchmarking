#!/bin/bash
set -e

# === CONFIGURAÇÕES ===
BASE_DIR="./../Permissioned-Network"

# === DEFINA AQUI A CONTA QUE DESEJA ADICIONAR ===
NEW_ACCOUNT="0xfe3b557e8fb62b89f4916b721be55ceb828dbd73"  # <<< edite aqui, (0x..., chave pública)

# === DEFINA O NUMERO DO NÓ QUE DESEJA VALIDAR PERMISSAO ===
NUM_NODE="1"

PERMISSIONS_FILE="$BASE_DIR/Node-$NUM_NODE/data/permissions_config.toml"

# === VALIDA SE O ARQUIVO EXISTE ===
if [ ! -f "$PERMISSIONS_FILE" ]; then
  echo "❌ Arquivo $PERMISSIONS_FILE não encontrado!"
  exit 1
fi

# === NORMALIZA A CONTA ===
account=$(echo "$NEW_ACCOUNT" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')
[[ $account != 0x* ]] && account="0x${account}"

# === LER O ARRAY ATUAL ===
current_accounts=$(grep -E '^accounts-allowlist=' "$PERMISSIONS_FILE" | sed 's/^accounts-allowlist=//')

# Limpa colchetes e espaços
clean_list=$(echo "$current_accounts" | tr -d '[]' | tr -d '"' | tr -d ' ')

# Converte em array bash
IFS=',' read -r -a accounts_array <<< "$clean_list"

# === VERIFICA SE JÁ EXISTE ===
found=false
for existing in "${accounts_array[@]}"; do
  if [[ "$existing" == "$account" ]]; then
    found=true
    break
  fi
done

if [ "$found" = true ]; then
  echo "ℹ️ Conta $account já está presente no Node-$NUM_NODE."
  exit 0
fi

# === ADICIONA A NOVA CONTA ===
accounts_array+=("$account")

# === RECONSTRÓI O ARRAY ===
new_accounts="accounts-allowlist=["
for i in "${!accounts_array[@]}"; do
  new_accounts+="\"${accounts_array[$i]}\""
  if [ "$i" -lt $(( ${#accounts_array[@]} - 1 )) ]; then
    new_accounts+=","
  fi
done
new_accounts+="]"

# === SUBSTITUI NO ARQUIVO ===
sed -i "s|^accounts-allowlist=.*|$new_accounts|" "$PERMISSIONS_FILE"

echo "✅ Conta $account adicionada com sucesso ao Node-$NUM_NODE!"
