import { buildModule } from '@nomicfoundation/hardhat-ignition/modules'

const Simple = buildModule('simple', (m) => {
  const simple = m.contract('simple')

  return { simple }
})

export default Simple