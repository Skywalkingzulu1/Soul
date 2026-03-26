# Solidity Quick Reference

## Basics
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MyContract {
    // State variables
    uint256 public myNumber = 42;
    string public myString = "Hello";
    address public owner;
    
    // Constructor
    constructor() {
        owner = msg.sender;
    }
}
```

## Data Types
```solidity
// Value types
bool public isActive = true;
uint256 public maxUint = type(uint256).max;
address public contractAddress = address(this);

// Arrays
uint256[] public dynamicArray;

// Mappings
mapping(address => uint256) public balances;

// Structs
struct Person {
    string name;
    uint256 age;
}
```

## Functions
```solidity
// Public function
function setValue(uint256 _value) public {
    value = _value;
}

// View function (read-only)
function getValue() public view returns (uint256) {
    return value;
}

// Pure function (no state)
function add(uint256 a, uint256 b) public pure returns (uint256) {
    return a + b;
}

// Function modifiers
modifier onlyOwner() {
    require(msg.sender == owner, "Only owner");
    _;
}
```

## Control Flow
```solidity
function conditional(uint256 x) public pure returns (string memory) {
    if (x > 100) return "Large";
    else if (x > 50) return "Medium";
    else return "Small";
}
```

## Error Handling
```solidity
function deposit(uint256 amount) public {
    require(amount > 0, "Amount must be > 0");
    balance += amount;
}

function withdraw(uint256 amount) public {
    require(balance >= amount, "Insufficient balance");
    balance -= amount;
}
```

## Events
```solidity
event Transfer(address indexed from, address indexed to, uint256 amount);

function transfer(address to, uint256 amount) public {
    // transfer logic
    emit Transfer(msg.sender, to, amount);
}
```

## Inheritance
```solidity
contract Animal {
    function makeSound() public pure virtual returns (string memory) {
        return "Some sound";
    }
}

contract Dog is Animal {
    function makeSound() public pure override returns (string memory) {
        return "Woof!";
    }
}
```