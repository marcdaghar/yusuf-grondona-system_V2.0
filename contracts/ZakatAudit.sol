// SPDX-License-Identifier: CC-BY-SA-4.0
// Author: Marc Daghar
// Zakat Audit — On-chain Zakat collection and distribution

pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract ZakatAudit is Ownable {
    enum Category {
        AL_FUQARA,    // Poor
        AL_MASAKIN,   // Needy
        AL_AMILIN,    // Collectors
        AL_MUALLAFATI,// Hearts to reconcile
        FI_AL_RIQAB,  // Freed slaves
        AL_GHARIMIN,  // Debtors
        FI_SABILILLAH,// In the path of God
        IBN_AL_SABIL  // Wayfarers
    }

    struct Distribution {
        Category category;
        uint256 amount;
        address recipient;
        uint256 timestamp;
    }

    IERC20 public nuqudToken;
    uint256 public totalCollected;
    uint256 public totalDistributed;
    Distribution[] public distributions;

    mapping(address => uint256) public zakatPaid;

    event ZakatCollected(address indexed payer, uint256 amount);
    event ZakatDistributed(Category indexed category, uint256 amount, address recipient);

    constructor(address _nuqudToken) Ownable(msg.sender) {
        nuqudToken = IERC20(_nuqudToken);
    }

    function payZakat(uint256 amount) external {
        require(nuqudToken.transferFrom(msg.sender, address(this), amount), "Transfer failed");
        totalCollected += amount;
        zakatPaid[msg.sender] += amount;
        emit ZakatCollected(msg.sender, amount);
    }

    function distribute(Category category, uint256 amount, address recipient) external onlyOwner {
        require(amount <= totalCollected - totalDistributed, "Insufficient funds");
        require(nuqudToken.transfer(recipient, amount), "Distribution failed");

        totalDistributed += amount;
        distributions.push(Distribution(category, amount, recipient, block.timestamp));

        emit ZakatDistributed(category, amount, recipient);
    }

    function autoDistribute(address[8] memory recipients) external onlyOwner {
        uint256 share = (totalCollected - totalDistributed) / 8;
        require(share > 0, "Nothing to distribute");

        for (uint i = 0; i < 8; i++) {
            distribute(Category(i), share, recipients[i]);
        }
    }

    function getReport() external view returns (uint256, uint256, uint256) {
        return (totalCollected, totalDistributed, distributions.length);
    }
}
