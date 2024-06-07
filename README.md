# flolang

[![Python package](https://github.com/ftobler/flolang/actions/workflows/python-package.yml/badge.svg)](https://github.com/ftobler/flolang/actions/workflows/python-package.yml)

**This is a programming language project.**

Goal is to be able to compile to C and seamlessly integrate it in existing C / C++ projects. Target platforms are small microcontrollers.

Code should be simple and easy to write in a high level syntax. Useful when speed is not an issue, but time to market and memory footprint is of importance.

## project state

*very much a work in progress*

works:
* There is a interpreter which works. It is written in python.
* Mathematical and logical evaluations work.
* Core building blocks work. (functions, loops, if).

progress:
* Variables and types are still in concept. (int works, but accepts everything)
* Return and break statements do not work correctly.
* Error handling. Too many run time errors that should be checked at compile time.

concepts:
* Class and structure type system still in concept.
* C backend is in planning
* Pool allocation concepts, garbage disposal (not collector).


## syntax

With return and break not yet working, use is inconvenient. But below samples execute with the interpreter.
```python
#!flolang
fn crc8_update(int data, int polynomial=0x07) int:
    crc ^= data
    for int _ in 0..8:
        if crc & 0x80:
            crc = (crc << 1) ^ polynomial
        else:
            crc = crc << 1
        crc &= 0xFF  # Ensure CRC remains 8-bit
    return crc

let int init_value = 0x00
let mut int crc = init_value
for int i in 1..4:
    crc = crc8_update(i)

# print result
print(crc)
```

```python
#!flolang
fn recur_factorial(int n) int:
    let mut int result = n
    if n != 1:
        result = n*recur_factorial(n-1)
    return result

let int num = 7
let mut int fac = 0

# check if the number is negative
if num < 0:
    print("Sorry, factorial does not exist for negative numbers")
    fac = -1
elif num == 0:
    fac = 1
else:
    fac = recur_factorial(num)
```
*(syntax highlighting similar to python works)*

## install

1. clone repository
2. `pip install -e .` to install for development with the `-e` editable option
3. You now can import flolang in python or you can execute it directly in console using `flolang`. This requires the `python3##/scripts/` directory to be in path.
4. `pip uninstall flolang` to uninstall

*but i don't want to install it..*

1. clone repository
2. run or import it using any of the below methods
    1. go into folder `./flolang/` and run `python main.py`
    2. run from repository root directly `python ./flolang/main.py`
    3. import form repository root `import flolang`

# usage

```python
#!python
import flolang
flolang.eval('print("Hello Wörld!")')
```

## variables

### fixed size variables
`class` `array` `int` `float` `number` `bool` `enum` `char` & C equivalent primitive types `u8`..`i64`..`f32`..

`let` to declare them local in a function.

`static` to declare them as global. Can be used in a function to make a global variable with local scope.

`mut` after `let` or `static  to mark the variable as mutable. All variables without the mut keyword cannot be changed once assigned.

### dynamic sized and allocated "objects" `dyn`
`string` `dict` `list` `set`

They are allocated on a dynamic allocation pool. This could be `malloc` (from C) or a builtin pool:
 * pool of fixed size as `let` to live on the stack
 * pool of fixed size as `static` to live in global scope
 * pool of fixed size as `dyn` (allocated through another pool)
 * pool of dynamic size falling back to heap (`malloc`)

A pool of fixed size can be purged of all data at runtime. This is something the user needs to do manually, or let the pool go out of scope. A fixed sized pool is a write only allocator. As such, a fixed size pool is very fast at allocating memory.
