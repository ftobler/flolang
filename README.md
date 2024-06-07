# flolang

[![Python package](https://github.com/ftobler/flolang/actions/workflows/python-package.yml/badge.svg)](https://github.com/ftobler/flolang/actions/workflows/python-package.yml)

**This is a programming language project.**

Goal is to be able to compile to C and seamlessly integrate it in existing C / C++ projects. Target platforms are small microcontrollers.

Code should be simple and easy to write in a high level syntax. Useful when speed is not an issue, but time to market and memory footprint is of importance.

## project state

*very much a work in progress*

works:
* there is a interpreter which works.
* mathematical and logical evaluations work.
* core building blocks work. (functions, loops, if).

progress:
* variables and types are still in concept. (int works, but accepts everything)
* return and break statements do not work correctly.
* error handling. Too many run time errors that should be checked at compile time.

concepts:
* Class and structure type system still in concept.
* C backend is in planning
* Pool allocation concepts, garbage disposal (not collector).

## install

1. clone repository
2. `pip install -e .` to install for development with the `-e` editable option
3. You now can import flolang in python or you can execute it directly in console using `flolang`. This requires the `python3##/scripts/` directory to be in path.
4. `pip uninstall flolang` to uninstall



## variables

### fixed size "variables" `let`
`class` `array` `int` `float` `number` `bool` `enum` `char` & C equivalent primitive types `u8`..`i64`..`f32`..

They are allocated on the current call stack. They are copied when re-assigned or returned. They have a fixed size.

### fixed size "statics" `const`
`class` `array` `int` `float` `number` `bool` `enum` `char` & C equivalent primitive types `u8`..`i64`..`f32`..

They are allocated globally. They are always passed by reference when re-assigned or returned. They have a fixed size.

### dynamic sized allocated "objects" `dyn`
`string` `dict` `list` `set`

They are allocated on a dynamic allocation pool. This could be `malloc` (from C) or a builtin pool:
 * pool of fixed size as `let` to live on the stack
 * pool of fixed size as `const` to live in global scope
 * pool of fixed size as `dyn` (allocated through another pool)
 * pool of dynamic size falling back to heap (`malloc`)

 A pool of fixed size can be purged of all data at runtime. This is something the user needs to do manually, or let the pool go out of scope. A fixed sized pool is a write only allocator. As such, a fixed size pool is very fast at allocating memory.
