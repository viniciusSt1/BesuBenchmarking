// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract NodeHealthMonitor {
    struct NodeStatus {
        address reporter;
        uint256 timestamp;
        bytes32 statusHash; // resumo das métricas
        uint8 severity; // 0: OK, 1: Warning, 2: Critical
        string optionalDetails; // opcional, usado em caso crítico
    }

    mapping(address => NodeStatus[]) public statusReports;

    event StatusReported(
        address indexed node,
        uint8 severity,
        bytes32 statusHash,
        uint256 timestamp
    );
    event CriticalAlert(
        address indexed node,
        string details,
        uint256 timestamp
    );

    function reportStatus(
        uint8 severity,
        bytes32 statusHash,
        string memory optionalDetails
    ) external {
        NodeStatus memory report = NodeStatus({
            reporter: msg.sender,
            timestamp: block.timestamp,
            statusHash: statusHash,
            severity: severity,
            optionalDetails: severity >= 2 ? optionalDetails : ""
        });

        statusReports[msg.sender].push(report);
        emit StatusReported(msg.sender, severity, statusHash, block.timestamp);

        if (severity >= 2) {
            emit CriticalAlert(msg.sender, optionalDetails, block.timestamp);
        }
    }

    function getLatestStatus(
        address node
    ) external view returns (NodeStatus memory) {
        uint256 len = statusReports[node].length;
        require(len > 0, "No reports yet");
        return statusReports[node][len - 1];
    }
}
