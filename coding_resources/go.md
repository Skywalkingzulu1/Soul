# Go Quick Reference

## Basics
```go
package main

import "fmt"

func main() {
    // Variables
    var name string = "Alice"
    age := 25  // short declaration
    const pi = 3.14159
    
    fmt.Printf("Hello, %s! You are %d years old\n", name, age)
}
```

## Data Types
```go
// Basic types
var i int = 42
var f float64 = 3.14
var b bool = true
var s string = "Hello"

// Arrays
var arr [5]int = [5]int{1, 2, 3, 4, 5}

// Slices (dynamic)
var slice []int = []int{1, 2, 3}
slice = append(slice, 4)

// Maps
m := make(map[string]int)
m["alice"] = 25

// Pointers
x := 42
p := &x
fmt.Println(*p)
```

## Control Flow
```go
// If-else
if age < 18 {
    fmt.Println("Minor")
} else if age == 18 {
    fmt.Println("Just became adult")
} else {
    fmt.Println("Adult")
}

// Loops
for i := 0; i < 10; i++ {
    fmt.Println(i)
}

// Range
fruits := []string{"apple", "banana"}
for i, fruit := range fruits {
    fmt.Printf("%d: %s\n", i, fruit)
}
```

## Functions
```go
func add(a, b int) int {
    return a + b
}

// Multiple return values
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, fmt.Errorf("division by zero")
    }
    return a / b, nil
}

// Variadic
func sum(numbers ...int) int {
    total := 0
    for _, num := range numbers {
        total += num
    }
    return total
}
```

## Structs and Methods
```go
type Person struct {
    Name string
    Age  int
}

func (p Person) Greet() string {
    return fmt.Sprintf("Hi, I'm %s", p.Name)
}

// Pointer receiver for mutation
func (p *Person) HaveBirthday() {
    p.Age++
}
```

## Concurrency
```go
func worker(done chan bool) {
    fmt.Println("Working...")
    time.Sleep(2 * time.Second)
    done <- true
}

func main() {
    done := make(chan bool)
    go worker(done)
    <-done
}
```

## Error Handling
```go
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, fmt.Errorf("division by zero")
    }
    return a / b, nil
}

result, err := divide(10, 0)
if err != nil {
    fmt.Println("Error:", err)
} else {
    fmt.Println(result)
}
```