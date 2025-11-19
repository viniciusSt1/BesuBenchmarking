'use strict';
const OperationBase = require('./utils/getLatestStatus-base');

class getLatestStatus extends OperationBase {
    constructor() {
        super();
    }

    async submitTransaction() {
        const getLatestStatus = ["0x7a5583095f747317be8a48d9a944aa0a9508f1d2"]
        await this.sutAdapter.sendRequests(this.createConnectorRequest('getLatestStatus', getLatestStatus));
    }
}

function createWorkloadModule() {
    return new getLatestStatus();
}

module.exports.createWorkloadModule = createWorkloadModule;