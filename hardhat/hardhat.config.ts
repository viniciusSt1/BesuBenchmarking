import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";

const config: HardhatUserConfig = {
  solidity: "0.8.24",
  networks: {
    local: // Nome da sua rede
    {
      url: `http://127.0.0.1:8545`, // COLOQUE O IP E PORTA DE SUA REDE
      chainId: 381660001,
      accounts: ['0x8f2a55949038a9610f50fb23b5883af3b4ecb3c3bb792cbcefbd1542c692be63'] // SUA CHAVE PRIVADA
    }
  }

};

export default config;
