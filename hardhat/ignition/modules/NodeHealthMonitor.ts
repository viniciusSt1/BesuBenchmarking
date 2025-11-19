import { buildModule } from '@nomicfoundation/hardhat-ignition/modules'

const NodeHealthMonitorModule = buildModule('NodeHealthMonitorModule', (m) => {
  const nodeHealthMonitor = m.contract('NodeHealthMonitor')

  return { nodeHealthMonitor }
})

export default NodeHealthMonitorModule
