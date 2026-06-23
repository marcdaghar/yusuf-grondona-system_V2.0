// SPDX-License-Identifier: CC-BY-SA-4.0
// Author: Marc Daghar
// Commenda (Qirad/Mudaraba) — Islamic profit-sharing contract

pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Commenda is Ownable {
    struct Deal {
        address mudarib;
        uint256 totalCapital;
        uint256 profitShareMudarib;
        uint256 repaidAmount;
        bool active;
    }

    IERC20 public nuqudToken;
    uint256 public dealCounter;
    mapping(uint256 => Deal) public deals;
    mapping(uint256 => mapping(address => uint256)) public investorShares;

    event DealCreated(uint256 indexed dealId, address mudarib, uint256 totalCapital);
    event ProfitDistributed(uint256 indexed dealId, uint256 totalProfit);

    constructor(address _nuqudToken) Ownable(msg.sender) {
        nuqudToken = IERC20(_nuqudToken);
    }

    function createDeal(
        address mudarib,
        uint256 totalCapital,
        uint256 profitShareMudarib
    ) external onlyOwner returns (uint256) {
        require(totalCapital > 0, "Capital must be positive");
        require(profitShareMudarib <= 5000, "Mudarib share cannot exceed 50%");

        uint256 dealId = ++dealCounter;
        deals[dealId] = Deal({
            mudarib: mudarib,
            totalCapital: totalCapital,
            profitShareMudarib: profitShareMudarib,
            repaidAmount: 0,
            active: true
        });
        emit DealCreated(dealId, mudarib, totalCapital);
        return dealId;
    }

    function invest(uint256 dealId, uint256 amount) external {
        Deal storage d = deals[dealId];
        require(d.active, "Deal not active");
        require(nuqudToken.transferFrom(msg.sender, address(this), amount), "Transfer failed");

        investorShares[dealId][msg.sender] += amount;
    }

    function distributeProfit(uint256 dealId, uint256 totalProfit) external onlyOwner {
        Deal storage d = deals[dealId];
        require(d.active, "Deal not active");

        uint256 mudaribShare = (totalProfit * d.profitShareMudarib) / 10000;
        uint256 investorsShare = totalProfit - mudaribShare;

        require(nuqudToken.transfer(d.mudarib, mudaribShare), "Mudarib transfer failed");

        d.repaidAmount += totalProfit;
        emit ProfitDistributed(dealId, totalProfit);
    }

    function closeDeal(uint256 dealId) external onlyOwner {
        Deal storage d = deals[dealId];
        require(d.active, "Already closed");
        require(d.repaidAmount >= d.totalCapital, "Capital not fully returned");
        d.active = false;
    }
}
