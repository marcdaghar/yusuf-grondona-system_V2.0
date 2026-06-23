// SPDX-License-Identifier: CC-BY-SA-4.0
// Author: Marc Daghar
// Yusuf Lending — Interest-free lending with profit-sharing

pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract YusufLending {
    struct Loan {
        address borrower;
        uint256 principal;
        uint256 profitShare;  // Basis points (e.g., 3000 = 30%)
        uint256 repaid;
        bool active;
    }

    mapping(uint256 => Loan) public loans;
    uint256 public loanCounter;
    IERC20 public token;

    event LoanCreated(uint256 indexed id, address borrower, uint256 principal);
    event ProfitDistributed(uint256 indexed id, uint256 profit);

    constructor(address _token) {
        token = IERC20(_token);
    }

    function createLoan(address borrower, uint256 principal, uint256 profitShareBps) external {
        require(profitShareBps <= 5000, "Max 50% profit share");
        require(token.transferFrom(msg.sender, borrower, principal), "Transfer failed");

        loanCounter++;
        loans[loanCounter] = Loan(borrower, principal, profitShareBps, 0, true);
        emit LoanCreated(loanCounter, borrower, principal);
    }

    function distributeProfit(uint256 loanId, uint256 totalProfit) external {
        Loan storage l = loans[loanId];
        require(l.active, "Loan inactive");

        uint256 lenderShare = totalProfit * (10000 - l.profitShare) / 10000;
        uint256 borrowerShare = totalProfit - lenderShare;

        require(token.transferFrom(l.borrower, msg.sender, lenderShare + l.principal), "Repayment failed");

        l.repaid += l.principal + lenderShare;
        l.active = false;

        emit ProfitDistributed(loanId, totalProfit);
    }
}
