# Mixed Fence Types Documentation

## Overview

This document demonstrates mixing backtick and tilde fences in the same document.

## Backtick Fences Containing Tildes

When documenting tilde-based examples using backticks:

````markdown
Here's how to use tilde fences:

~~~bash
#!/bin/bash
echo "Script using tilde fences"
ls -la
~~~
````

## Tilde Fences Containing Backticks

When documenting backtick-based examples using tildes:

~~~~markdown
Here's how to use backtick fences:

```python
def process_data(items):
    """Process a list of items."""
    return [item.strip() for item in items]
```
~~~~

## Real-World Use Case

A tutorial showing both fence types:

````markdown
### Option 1: Using Backticks

```javascript
const greeting = "Hello, World!";
console.log(greeting);
```

### Option 2: Using Tildes

~~~javascript
const farewell = "Goodbye!";
console.log(farewell);
~~~
````

## Alternating Examples

First example with backticks:

```go
package main

import "fmt"

func main() {
    fmt.Println("Hello from Go")
}
```

Second example with tildes:

~~~rust
fn main() {
    println!("Hello from Rust");
}
~~~

Both fence types work seamlessly together.
