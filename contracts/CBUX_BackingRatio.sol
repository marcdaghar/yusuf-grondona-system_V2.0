// SPDX-License-Identifier: CC-BY-SA-4.0
// Author: Marc Daghar
// CBU-X Backing Ratio — On-chain verification of physical backing

pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract CBUXToken is ERC20, Ownable {
    uint256 public constant SCALE_PHYSICAL = 10**18;
    uint256 public constant SCALE_CBU = 10**6;

    uint256 public physicalValue;  // Total physical backing in USD * SCALE
    uint256 public totalCBU;       // Total CBU supply

    enum BackingLevel { GREEN, YELLOW, ORANGE, RED }

    event BackingUpdated(uint256 physicalValue, uint256 totalCBU, uint256 ratio);
    event FreezeGradual(BackingLevel level, uint256 taxRate);

    constructor() ERC20("CBU-X", "CBUX") Ownable(msg.sender) {}

    function updateBacking(uint256 _physicalValue, uint256 _totalCBU) external onlyOwner {
        physicalValue = _physicalValue;
        totalCBU = _totalCBU;
        emit BackingUpdated(_physicalValue, _totalCBU, backingRatio());
    }

    function backingRatio() public view returns (uint256) {
        if (totalCBU == 0) return SCALE_PHYSICAL;
        return (physicalValue * SCALE_PHYSICAL) / (totalCBU * SCALE_CBU);
    }

    function getBackingLevel() public view returns (BackingLevel) {
        uint256 ratio = backingRatio();
        if (ratio >= SCALE_PHYSICAL) return BackingLevel.GREEN;
        if (ratio >= 8 * SCALE_PHYSICAL / 10) return BackingLevel.YELLOW;
        if (ratio >= 5 * SCALE_PHYSICAL / 10) return BackingLevel.ORANGE;
        return BackingLevel.RED;
    }

    function mint(address to, uint256 amount) external onlyOwner {
        BackingLevel level = getBackingLevel();
        uint256 tax = 0;

        if (level == BackingLevel.YELLOW) {
            tax = amount * (SCALE_PHYSICAL - backingRatio()) * 20 / SCALE_PHYSICAL / 100;
        } else if (level == BackingLevel.ORANGE) {
            require(amount <= 1000 * SCALE_CBU, "Daily limit exceeded");
        } else if (level == BackingLevel.RED) {
            revert("Complete freeze — restructuring required");
        }

        _mint(to, amount - tax);
        if (tax > 0) _mint(owner(), tax);
        totalCBU += amount;

        emit FreezeGradual(level, tax);
    }

    function burn(address from, uint256 amount) external onlyOwner {
        _burn(from, amount);
        totalCBU -= amount;
    }
}
