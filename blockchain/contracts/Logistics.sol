// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract Logistics {
    struct LogisticsRecord {
        uint256 id;
        string shipmentId;
        uint256 predictedDeliveryHours;
        uint256 timestamp;
        address recordedBy;
    }

    uint256 private recordCount;
    mapping(uint256 => LogisticsRecord) private records;

    event LogisticsRecorded(
        uint256 indexed id,
        string shipmentId,
        uint256 predictedDeliveryHours,
        uint256 timestamp,
        address indexed recordedBy
    );

    function recordLogistics(string calldata shipmentId, uint256 predictedDeliveryHours) external returns (uint256 id) {
        recordCount += 1;
        id = recordCount;
        records[id] = LogisticsRecord(id, shipmentId, predictedDeliveryHours, block.timestamp, msg.sender);
        emit LogisticsRecorded(id, shipmentId, predictedDeliveryHours, block.timestamp, msg.sender);
    }

    function getRecord(uint256 id) external view returns (LogisticsRecord memory) {
        require(id > 0 && id <= recordCount, "Record does not exist");
        return records[id];
    }

    function getRecordCount() external view returns (uint256) {
        return recordCount;
    }
}
