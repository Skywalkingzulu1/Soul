# Java Quick Reference

## Basics
```java
public class HelloWorld {
    public static void main(String[] args) {
        // Variables
        String name = "Alice";
        int age = 25;
        final double PI = 3.14159;
        
        System.out.println("Hello, " + name + "!");
    }
}
```

## Data Types
```java
// Primitive types
byte b = 127;
int i = 2147483647;
long l = 9223372036854775807L;
float f = 3.14f;
double d = 3.14159;
boolean bool = true;
char c = 'A';

// Arrays
int[] numbers = {1, 2, 3, 4, 5};
String[] names = new String[3];

// ArrayList
import java.util.ArrayList;
ArrayList<String> list = new ArrayList<>();
list.add("Apple");

// HashMap
import java.util.HashMap;
HashMap<String, Integer> map = new HashMap<>();
map.put("Alice", 25);
```

## Control Flow
```java
// If-else
if (age < 18) {
    System.out.println("Minor");
} else if (age == 18) {
    System.out.println("Just became adult");
} else {
    System.out.println("Adult");
}

// Switch
switch (day) {
    case 1: System.out.println("Monday"); break;
    case 2: System.out.println("Tuesday"); break;
    default: System.out.println("Other day");
}

// Loops
for (int i = 0; i < 5; i++) {
    System.out.println(i);
}

for (int num : numbers) {
    System.out.println(num);
}
```

## Classes
```java
public class Person {
    private String name;
    private int age;
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public void greet() {
        System.out.println("Hi, I'm " + name);
    }
}

class Student extends Person {
    private String grade;
    
    public Student(String name, int age, String grade) {
        super(name, age);
        this.grade = grade;
    }
}
```

## Interfaces
```interface Drawable {
    void draw();
    double getArea();
}

class Circle implements Drawable {
    private double radius;
    
    public Circle(double radius) { this.radius = radius; }
    
    @Override
    public void draw() {
        System.out.println("Drawing circle");
    }
    
    @Override
    public double getArea() {
        return Math.PI * radius * radius;
    }
}
```

## Lambda Expressions (Java 8+)
```java
import java.util.*;

List<String> names = Arrays.asList("Alice", "Bob", "Charlie");

names.forEach(name -> System.out.println(name));

names.sort((a, b) -> a.compareTo(b));
```