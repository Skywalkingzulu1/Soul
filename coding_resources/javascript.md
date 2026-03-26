# JavaScript Quick Reference

## Basics
```javascript
// Variables
let name = "Alice";           // mutable
const age = 25;               // immutable reference
var oldStyle = "deprecated"; // function scoped

// Data types
let str = "string";
let num = 42;
let bool = true;
let arr = [1, 2, 3];
let obj = { name: "John", age: 30 };

// Console output
console.log("Hello, World!");
console.log(`Hello, ${name}!`);
```

## Data Structures
```javascript
// Arrays
let fruits = ["apple", "banana", "orange"];
fruits.push("mango");
fruits.forEach(f => console.log(f));
let doubled = arr.map(n => n * 2);

// Objects
let person = { name: "John", age: 30 };
let { name, age } = person;

// Spread operator
let copy = { ...person };
let combined = [...fruits, "grape"];
```

## Functions
```javascript
// Function declaration
function greet(name) {
    return `Hello, ${name}!`;
}

// Arrow function
const add = (a, b) => a + b;

// Higher-order functions
const multiplyBy = (factor) => (number) => number * factor;
const double = multiplyBy(2);
console.log(double(5)); // 10
```

## Control Flow
```javascript
// If-else
if (age < 18) console.log("Minor");
else if (age === 18) console.log("Just became adult");
else console.log("Adult");

// Loops
for (let i = 0; i < 5; i++) console.log(i);
fruits.forEach(f => console.log(f));
```

## ES6+ Features
```javascript
// Template literals
let message = `Hello, ${name}!`;

// Destructuring
let { name, age } = person;
let [first, second] = fruits;

// Array methods
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(n => n * 2);
const evens = numbers.filter(n => n % 2 === 0);
const sum = numbers.reduce((a, b) => a + b, 0);
```

## Async Programming
```javascript
// Promises
const fetchData = () => {
    return new Promise((resolve, reject) => {
        setTimeout(() => resolve("Data loaded!"), 1000);
    });
};

fetchData()
    .then(data => console.log(data))
    .catch(error => console.error(error));

// Async/await
async function loadData() {
    try {
        const data = await fetchData();
        console.log(data);
    } catch (error) {
        console.error(error);
    }
}
```

## Classes
```javascript
class Person {
    constructor(name, age) {
        this.name = name;
        this.age = age;
    }
    
    greet() {
        return `Hi, I'm ${this.name}`;
    }
    
    static getSpecies() {
        return 'Homo sapiens';
    }
}

class Student extends Person {
    constructor(name, age, grade) {
        super(name, age);
        this.grade = grade;
    }
}
```