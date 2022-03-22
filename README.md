# lox-interpreter
Interpreter for lox language from the book [Crafting interpreters](http://craftinginterpreters.com/) with some of my changes and additions.

## Installation
### Install with pip
```sh
$ pip install git+https://github.com/EdvardsF/lox-interpreter.git
```

**Usage**
```sh
$ pylox                             # Starts a lox repl
$ pylox path/to/source_code.lox     # Executes the file
```

### Install without pip
1. Clone the repo
    ```sh
    $ git clone https://github.com/EdvardsF/lox-interpreter.git
    ```
2. Navigate to source code directory.
    ```sh
    $ cd lox
    ```
3. Running:
    ```sh
    $ python run.py                           # Starts a loxscript repl
    $ python run.py path/to/source_code.ls    # Executes the file
    ```
# Language Features

## Printing
```python
print "Hello World";
```

## Basic Data types
```js
"this is a string";  // string
true;false;  // booleans
1;2.3;  // numbers
nil; // None
```

## Arithmetic
```js
a-b;
a+b;
a/b;
c*b;
(a+b)*c; // grouping
-negate;
```
## Comparison and equality
Note: There is no implicit conversion
```js
a==b;
a!=b;
a>b;
a<b;
a>=b;
a<=b;
!true; // false
```

## Logical operators
```js
true and false; // false.
true and true;  // true.
false or false; // false.
true or false;  // true.
```
**Truthiness:** Aside from `false` and `nil` everything else is truthy 
## Variables
```js
var x = "New variable";
print x;
x = "New value"; // modifying existing variable
```
## Blockscope
Lox follows block scope
```js
{
    var x = 10;
}
print x; // error: Undefined variable x
```

## Conditionals
```js
if (a==b) {
    print "a is equal to b";
} else if (a==c) {
    print "a is equal to c";
} else {
    print "a is not equal to b";
}
```
## Lists
```js
var a = [1, 2, 3];
print a[0]; // 1
```

## Looping
Lox supports `while` and `for` loop
```js
var a = 1;
while (a < 10) {
  print a;
  a = a + 1;
}
```
Equivalent `for` loop:
```js
for (var a = 1; a < 10; a = a + 1) {
  print a;
}
```

## Functions
```js
fun add(a,b) {
    return a+b;
}
print add(1, 2);
```

## Closures
Functions are first-class citizens in Lox.
```js
fun returnFunction() {
  var outside = "outside";

  fun inner() {
    print outside;
  }

  return inner;
}

var fn = returnFunction();
fn();
```

## Classes
```js
class Foo {
    init(x) {
        this.x = x;
    }
    test() {
        print ("x is " + this.x);
    }
}
var foo = Foo('VALUE OF XXXXX');
foo.test(); // x is VALUE OF XXXXX
```

## Inheritance
```js
class BaseClass {
    init() {
        this.x = 'XX';
    }
    method() {
        print "this is a method of base class!";
        print "And the value of x is " + this.x;
    }
}

class SubClass < BaseClass {
    init() {
        this.x = 'SUBCLASS';
    }
    method() {
        super.method();
    }
}
var subclass = SubClass();
subclass.method();
// This prints
// this is a method of base class!
// And the value of x is SUBCLASS
```
