'use strict';
const OperationBase = require('./utils/reportStatus-base');

class reportStatus extends OperationBase {
    constructor() {
        super();
    }

    async submitTransaction() {
        const reportStatus = ["2", "0x17d03fd2be867379ac6cfa30d1d9fb4662fe52bc833f7bc49c24400ffe2ea6a8", "Problema Detectado"]
        await this.sutAdapter.sendRequests(this.createConnectorRequest('reportStatus', reportStatus));
    }
}

function createWorkloadModule() {
    return new reportStatus();
}

module.exports.createWorkloadModule = createWorkloadModule;