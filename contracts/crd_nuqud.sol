// SPDX-License-Identifier: CC-BY-SA-4.0
// Author: Marc Daghar
// CRD + Nuqud Tokenization — Commodity Reserve with gold/silver backing

pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract NuqudToken is ERC20, Ownable {
    string private _metalType;
    uint256 private _totalReserve;

    constructor(string memory name, string memory symbol, string memory metalType)
        ERC20(name, symbol) Ownable(msg.sender) {
        _metalType = metalType;
        _totalReserve = 0;
    }

    function mint(address to, uint256 grams) external onlyOwner {
        require(grams > 0, "Amount must be positive");
        _mint(to, grams);
        _totalReserve += grams;
    }

    function burn(address from, uint256 grams) external onlyOwner {
        require(balanceOf(from) >= grams, "Insufficient balance");
        _burn(from, grams);
        _totalReserve -= grams;
    }

    function totalReserve() external view returns (uint256) {
        return _totalReserve;
    }

    function metalType() external view returns (string memory) {
        return _metalType;
    }
}

contract CRD is Ownable {
    struct Commodity {
        uint256 floorPrice;
        uint256 ceilingPrice;
        uint256 stockpile;
    }

    mapping(string => Commodity) public commodities;
    mapping(address => uint256) public fulusBalances;
    uint256 public totalFulusSupply;

    event CRDBuy(address indexed buyer, string commodity, uint256 grams, uint256 fulusCreated);
    event CRDSell(address indexed seller, string commodity, uint256 grams, uint256 fulusDestroyed);

    constructor() Ownable(msg.sender) {
        commodities["gold"] = Commodity(50, 70, 0);
        commodities["silver"] = Commodity(8, 12, 0);
        commodities["copper"] = Commodity(8000, 12000, 0);
        commodities["wheat"] = Commodity(180, 220, 0);
    }

    function buyCommodity(string memory commodity, uint256 grams) external {
        Commodity storage c = commodities[commodity];
        require(c.floorPrice > 0, "Commodity not supported");

        uint256 fulusCreated = grams * c.floorPrice;
        fulusBalances[msg.sender] += fulusCreated;
        totalFulusSupply += fulusCreated;
        c.stockpile += grams;

        emit CRDBuy(msg.sender, commodity, grams, fulusCreated);
    }

    function sellCommodity(string memory commodity, uint256 grams) external {
        Commodity storage c = commodities[commodity];
        require(c.stockpile >= grams, "Insufficient stockpile");

        uint256 fulusDestroyed = grams * c.ceilingPrice;
        require(fulusBalances[msg.sender] >= fulusDestroyed, "Insufficient fulus");

        fulusBalances[msg.sender] -= fulusDestroyed;
        totalFulusSupply -= fulusDestroyed;
        c.stockpile -= grams;

        emit CRDSell(msg.sender, commodity, grams, fulusDestroyed);
    }

    function transferFulus(address to, uint256 amount) external {
        require(fulusBalances[msg.sender] >= amount, "Insufficient fulus");
        fulusBalances[msg.sender] -= amount;
        fulusBalances[to] += amount;
    }
}
