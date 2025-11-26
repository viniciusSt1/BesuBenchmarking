#!/usr/bin/env python3
import sys
import re

def update_yaml_containers(yaml_file, num_nodes):
    with open(yaml_file, 'r') as f:
        content = f.read()

    # Gerar lista de containers
    containers = '\n'.join([f'          - /node-besu{i}' for i in range(1, num_nodes + 1)])

    # Padrão para encontrar a seção containers até stats
    pattern = r'(        containers:\n)((?:          - /node-besu\d+\n)+)(        stats:)'

    # Substituir
    replacement = r'\1' + containers + '\n' + r'\3'
    new_content = re.sub(pattern, replacement, content)

    # Escrever de volta
    with open(yaml_file, 'w') as f:
        f.write(new_content)

    return True

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Uso: update_yaml_nodes.py <arquivo.yaml> <num_nodes>")
        sys.exit(1)

    yaml_file = sys.argv[1]
    num_nodes = int(sys.argv[2])

    if update_yaml_containers(yaml_file, num_nodes):
        print(f"Atualizado {yaml_file} para {num_nodes} nodes")
    else:
        print(f"Falha ao atualizar {yaml_file}")
        sys.exit(1)
