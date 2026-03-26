# Rust Quick Reference

## Basics
```rust
fn main() {
    // Variables
    let name = "Alice";           // immutable
    let mut age = 25;             // mutable
    const MAX_POINTS: u32 = 100; // constant
    
    println!("Hello, {}!", name);
}
```

## Data Types
```rust
// Primitive types
let integer: i32 = 42;
let float: f64 = 3.14;
let boolean: bool = true;

// Arrays
let arr: [i32; 5] = [1, 2, 3, 4, 5];

// Vectors
let mut v = vec![1, 2, 3];
v.push(4);

// Strings
let s = String::from("Hello");

// Tuples
let tuple: (i32, f64, bool) = (42, 3.14, true);
let (x, y, z) = tuple;
```

## Control Flow
```rust
// If expressions
let message = if age < 18 {
    "Minor"
} else {
    "Adult"
};

// Loops
for i in 0..5 {
    println!("{}", i);
}

// While
let mut count = 0;
while count < 5 {
    count += 1;
}

// Loop with break
let result = loop {
    counter += 1;
    if counter == 10 {
        break counter * 2;
    }
};
```

## Functions
```rust
fn add(a: i32, b: i32) -> i32 {
    a + b  // implicit return (no semicolon)
}

fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}
```

## Structs and Impl
```rust
struct Person {
    name: String,
    age: u32,
}

impl Person {
    fn new(name: String, age: u32) -> Person {
        Person { name, age }
    }
    
    fn greet(&self) -> String {
        format!("Hi, I'm {} and I'm {} years old", self.name, self.age)
    }
}
```

## Enums
```rust
enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
}

impl Message {
    fn process(&self) {
        match self {
            Message::Quit => println!("Quitting"),
            Message::Move { x, y } => println!("Move to ({}, {})", x, y),
            Message::Write(text) => println!("Writing: {}", text),
        }
    }
}
```

## Error Handling
```rust
fn divide(a: f64, b: f64) -> Result<f64, String> {
    if b == 0.0 {
        Err("Cannot divide by zero".to_string())
    } else {
        Ok(a / b)
    }
}

match divide(10.0, 2.0) {
    Ok(result) => println!("Result: {}", result),
    Err(e) => println!("Error: {}", e),
}
```