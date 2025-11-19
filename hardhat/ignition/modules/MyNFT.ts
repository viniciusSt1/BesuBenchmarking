import { buildModule } from '@nomicfoundation/hardhat-ignition/modules'

const MyNFT = buildModule('MyNFT', (m) => {
  const mynft = m.contract('MyNFT')

  return { mynft }
})

export default MyNFT