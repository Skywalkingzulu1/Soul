# Python Quick Reference

## Basics
```python
# Variables and types
name = "Alice"          # string
age = 25               # integer
height = 5.6           # float
is_student = True      # boolean

# Print output
print(f"Name: {name}, Age: {age}")

# Input
user_input = input("Enter something: ")
```

## Data Structures
```python
# Lists
fruits = ["apple", "banana", "orange"]
fruits.append("mango")
for fruit in fruits:
    print(fruit)

# Dictionaries
person = {"name": "John", "age": 30, "city": "New York"}
for key, value in person.items():
    print(f"{key}: {value}")

# Sets
numbers = {1, 2, 3, 4, 5}

# Tuples
coordinates = (10, 20)
```

## Control Flow
```python
# If-elif-else
if age < 18:
    print("Minor")
elif age == 18:
    print("Just became adult")
else:
    print("Adult")

# Loops
for i in range(5):
    print(i)

count = 0
while count < 5:
    print(count)
    count += 1
```

## Functions
```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

# Lambda functions
multiply = lambda x, y: x * y

# Decorators
def timer(func):
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        result = func(*args, **kwargs)
        print(f"Took {time.time() - start:.2f}s")
        return result
    return wrapper
```

## Classes
```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        return f"Hi, I'm {self.name}"

class Student(Person):
    def __init__(self, name, age, grade):
        super().__init__(name, age)
        self.grade = grade
    
    def study(self, subject):
        return f"Studying {subject}"
```

## File Operations
```python
# Reading files
with open("file.txt", "r") as f:
    content = f.read()

# Writing files
with open("output.txt", "w") as f:
    f.write("Hello, World!")
```

## Error Handling
```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero")
except Exception as e:
    print(f"Error: {e}")
finally:
    print("Cleanup code")
```

## Popular Libraries
```python
# NumPy
import numpy as np
arr = np.array([1, 2, 3, 4, 5])

# Pandas
import pandas as pd
df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})

# Requests
import requests
response = requests.get("https://api.example.com/data")
```