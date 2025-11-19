## Requisitos

- Node.js v16+
- Hardhat
- npm

Antes de iniciar o deploy, certifique-se de configurar o arquivo hardhat.config.ts com os dados corretos da sua rede:
```
networks: {
  local: {
    url: "http://127.0.0.1:8545", // ou o endereço da sua rede
    accounts: ["SUA_CHAVE_PRIVADA"]
  }
}
```
## Instale as dependências e compile os contratos: 

```shell
npm install
npx hardhat compile
```

## Executando o Deploy e Inicialização

 Rode o seguinte comando para realizar o deploy dos contratos e inicializá-los na rede:

### Para fazer Deploy do NodeHealthMonitor:
```shell
npx hardhat ignition deploy ./ignition/modules/NodeHealthMonitor.ts --network local
```

### Para fazer Deploy do Simple:
```shell
npx hardhat ignition deploy ./ignition/modules/Simple.ts --network local
```

-> Implementar ERC721 correto para deploy e teste

## Endereços dos Contratos

Após a execução do comando, você verá os endereços dos contratos no terminal. Esses endereços são importantes para interagir com os contratos já implantados.

![Ignition Deploy and Initialize](./img/deploy.png)