// SPDX-License-Identifier: CC-BY-SA-4.0
// Author: Marc Daghar
// Convertibility Registry — Corridors for X/CBU exchange

pragma solidity ^0.8.20;

contract ConvertibilityRegistry {
    struct Corridor {
        address zone;
        uint256 floorRate;     // Minimum X per CBU
        uint256 ceilingRate;   // Maximum X per CBU
        bool active;
    }

    mapping(bytes32 => Corridor) public corridors;
    bytes32[] public corridorList;

    event CorridorAdded(bytes32 indexed id, address zone, uint256 floor, uint256 ceiling);
    event RateUpdated(bytes32 indexed id, uint256 newFloor, uint256 newCeiling);

    function addCorridor(bytes32 id, address zone, uint256 floor, uint256 ceiling) external {
        require(floor < ceiling, "Invalid spread");
        corridors[id] = Corridor(zone, floor, ceiling, true);
        corridorList.push(id);
        emit CorridorAdded(id, zone, floor, ceiling);
    }

    function updateRates(bytes32 id, uint256 floor, uint256 ceiling) external {
        require(corridors[id].active, "Corridor inactive");
        corridors[id].floorRate = floor;
        corridors[id].ceilingRate = ceiling;
        emit RateUpdated(id, floor, ceiling);
    }

    function getValidRate(bytes32 id, uint256 proposedRate) external view returns (bool) {
        Corridor memory c = corridors[id];
        return c.active && proposedRate >= c.floorRate && proposedRate <= c.ceilingRate;
    }
}
