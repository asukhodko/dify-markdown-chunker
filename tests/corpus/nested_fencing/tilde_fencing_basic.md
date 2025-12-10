# Tilde Fencing Guide

## Introduction

This guide demonstrates the use of tilde fencing as an alternative to backticks in markdown.

## Basic Tilde Fencing

Use triple tildes for standard code blocks:

~~~python
def greet(name):
    return f"Hello, {name}!"

# Call the function
result = greet("World")
print(result)
~~~

## Nested Tilde Fencing

For documentation that shows tilde-fenced examples:

~~~~markdown
To display Python code with tildes:

~~~python
def calculate_area(radius):
    import math
    return math.pi * radius ** 2
~~~
~~~~

## Mixed Content Example

Combining text and tilde-fenced code:

~~~javascript
function factorial(n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

console.log(factorial(5));  // Output: 120
~~~

The recursive approach is elegant but may cause stack overflow for large values.
