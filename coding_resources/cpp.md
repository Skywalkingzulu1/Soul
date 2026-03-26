# C++ Quick Reference

## Basics
```cpp
#include <iostream>
#include <string>

int main() {
    // Variables
    std::string name = "Alice";
    int age = 25;
    const double PI = 3.14159;
    
    std::cout << "Hello, " << name << "! You are " << age << std::endl;
    return 0;
}
```

## Data Types
```cpp
// Basic types
int integer = 42;
float floating = 3.14f;
double doublePrec = 3.14159;
bool boolVar = true;
char character = 'A';

// Arrays
int arr[5] = {1, 2, 3, 4, 5};

// Vectors (C++11+)
#include <vector>
std::vector<int> vec = {1, 2, 3, 4, 5};
vec.push_back(6);

// Strings
std::string str = "Hello, World!";

// Pointers and References
int x = 42;
int* ptr = &x;
int& ref = x;
```

## Control Flow
```cpp
// If-else
if (age < 18) {
    std::cout << "Minor" << std::endl;
} else if (age == 18) {
    std::cout << "Just became adult" << std::endl;
} else {
    std::cout << "Adult" << std::endl;
}

// Switch
switch (day) {
    case 1: std::cout << "Monday"; break;
    case 2: std::cout << "Tuesday"; break;
    default: std::cout << "Other day";
}

// Loops
for (int i = 0; i < 5; i++) {
    std::cout << i << " ";
}

for (int num : vec) {
    std::cout << num << " ";
}
```

## Functions
```cpp
// Basic function
int add(int a, int b) {
    return a + b;
}

// Default parameters
void greet(std::string name = "Guest") {
    std::cout << "Hello, " << name << "!" << std::endl;
}

// Template function
template<typename T>
T findMax(T a, T b) {
    return (a > b) ? a : b;
}

// Lambda (C++11+)
auto add = [](int a, int b) { return a + b; };
```

## Classes
```cpp
class Person {
private:
    std::string name;
    int age;
    
public:
    // Constructor
    Person(const std::string& name, int age) : name(name), age(age) {}
    
    // Methods
    void greet() const {
        std::cout << "Hi, I'm " << name << std::endl;
    }
    
    // Getters/Setters
    std::get_name() const { return name; }
    void set_age(int a) { age = a; }
};

// Inheritance
class Student : public Person {
private:
    std::string grade;
    
public:
    Student(const std::string& name, int age, const std::string& grade)
        : Person(name, age), grade(grade) {}
};
```

## Modern C++ Features (C++11+)
```cpp
// Auto
auto x = 42;  // int
auto str = "hello";  // const char*

// Range-based for
for (const auto& item : collection) {
    // process item
}

// Smart pointers
#include <memory>
auto ptr = std::make_unique<int>(42);
std::shared_ptr<int> shared = std::make_shared<int>(42);

// Move semantics
std::vector<int> v1 = {1, 2, 3};
std::vector<int> v2 = std::move(v1);
```