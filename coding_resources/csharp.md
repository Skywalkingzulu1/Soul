# C# Quick Reference

## Basics
```csharp
using System;

class Program
{
    static void Main(string[] args)
    {
        // Variables
        string name = "Alice";
        int age = 25;
        const double PI = 3.14159;
        
        Console.WriteLine($"Hello, {name}! You are {age} years old.");
    }
}
```

## Data Types
```csharp
// Value types
int i = 42;
float f = 3.14f;
double d = 3.14159;
decimal m = 3.14159m;
bool b = true;
char c = 'A';

// Reference types
string s = "Hello";
object o = new object();

// Arrays
int[] numbers = {1, 2, 3, 4, 5};
int[,] matrix = new int[3, 3];

// Collections
using System.Collections.Generic;
List<string> list = new List<string>();
Dictionary<string, int> dict = new Dictionary<string, int>();
Queue<int> queue = new Queue<int>();
Stack<int> stack = new Stack<int>();
```

## Control Flow
```csharp
// If-else
if (age < 18)
    Console.WriteLine("Minor");
else if (age == 18)
    Console.WriteLine("Just became adult");
else
    Console.WriteLine("Adult");

// Switch
switch (day)
{
    case 1:
        Console.WriteLine("Monday");
        break;
    case 2:
        Console.WriteLine("Tuesday");
        break;
    default:
        Console.WriteLine("Other day");
        break;
}

// Loops
for (int i = 0; i < 10; i++)
    Console.WriteLine(i);

foreach (var item in collection)
    Console.WriteLine(item);

while (condition)
{
    // code
}

do
{
    // code
} while (condition);
```

## Classes
```csharp
public class Person
{
    // Properties
    public string Name { get; set; }
    public int Age { get; private set; }
    
    // Constructor
    public Person(string name, int age)
    {
        Name = name;
        Age = age;
    }
    
    // Methods
    public void Greet()
    {
        Console.WriteLine($"Hi, I'm {Name}");
    }
    
    // Static method
    public static int GetCount() => ++count;
    
    private static int count = 0;
}

// Inheritance
public class Student : Person
{
    public string Grade { get; set; }
    
    public Student(string name, int age, string grade) 
        : base(name, age)
    {
        Grade = grade;
    }
}
```

## LINQ
```csharp
using System.Linq;

// Query syntax
var results = from item in collection
              where item.Property > 10
              orderby item.Name
              select item.Name;

// Method syntax
var results2 = collection
    .Where(x => x.Property > 10)
    .OrderBy(x => x.Name)
    .Select(x => x.Name);

// Aggregation
int count = collection.Count();
int sum = collection.Sum(x => x.Value);
var avg = collection.Average(x => x.Value);
```

## Async/Await
```csharp
public async Task<string> GetDataAsync()
{
    await Task.Delay(1000);
    return "Data loaded";
}

public async Task ProcessAsync()
{
    var data = await GetDataAsync();
    Console.WriteLine(data);
}
```

## Error Handling
```csharp
try
{
    int result = a / b;
}
catch (DivideByZeroException ex)
{
    Console.WriteLine($"Error: {ex.Message}");
}
catch (Exception ex)
{
    Console.WriteLine($"Error: {ex.Message}");
}
finally
{
    Console.WriteLine("Cleanup");
}
```