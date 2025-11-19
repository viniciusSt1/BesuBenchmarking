'use strict';
const OperationBase = require('./utils/statusReports-base');

class StatusReports extends OperationBase {
    constructor() {
        super();
    }

    async submitTransaction() {
        const StatusReports = ["0x7a5583095f747317be8a48d9a944aa0a9508f1d2", 0]
        await this.sutAdapter.sendRequests(this.createConnectorRequest('statusReports', StatusReports));
    }
}

function createWorkloadModule() {
    return new StatusReports();
}

module.exports.createWorkloadModule = createWorkloadModule;