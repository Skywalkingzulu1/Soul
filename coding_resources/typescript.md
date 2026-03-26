# TypeScript Quick Reference

## Basics
```typescript
// Variables with type annotations
let name: string = "Alice";
let age: number = 25;
let isActive: boolean = true;
let data: any = { key: "value" }; // Any type

// Type inference
let inferredString = "TypeScript will know this is string";
```

## Types and Interfaces
```typescript
// Type alias
type Person = {
    name: string;
    age: number;
    email?: string; // Optional property
    readonly id: number; // Read-only
};

// Interface
interface User {
    name: string;
    age: number;
    email?: string;
}

// Union types
type Status = "active" | "inactive" | "pending";

// Generics
interface Repository<T> {
    findById(id: string): Promise<T>;
    save(entity: T): Promise<T>;
}
```

## Classes
```typescript
class Animal {
    protected name: string;
    private age: number;
    
    constructor(name: string, age: number) {
        this.name = name;
        this.age = age;
    }
    
    public makeSound(): string {
        return "Some sound";
    }
}

class Dog extends Animal {
    constructor(name: string, age: number) {
        super(name, age);
    }
    
    public makeSound(): string {
        return "Woof!";
    }
}
```

## Functions
```typescript
// Arrow functions
const add = (a: number, b: number): number => a + b;

// Function with default parameters
function greet(name: string, greeting: string = "Hello"): string {
    return `${greeting}, ${name}!`;
}

// Generic functions
function firstElement<T>(array: T[]): T | undefined {
    return array[0];
}
```

## Utility Types
```typescript
interface User { id: number; name: string; email: string; age: number; }

// Partial - all optional
type PartialUser = Partial<User>;

// Pick - select specific properties
type UserBasic = Pick<User, "id" | "name">;

// Omit - remove properties
type UserNoEmail = Omit<User, "email">;
```