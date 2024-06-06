# flolang

[![Python package](https://github.com/ftobler/flolang/actions/workflows/python-package.yml/badge.svg)](https://github.com/ftobler/flolang/actions/workflows/python-package.yml)

**This is a programming language project.**

Goal is to be able to compile to C and seamlessly integrate it in existing C / C++ projects. Target platforms are small microcontrollers.

Code should be simple and easy to write in a high level syntax. Useful when speed is not an issue, but time to market and memory footprint is of importance.

## project state

* very much a work in progress
* there is a interpreter
* C backend is in planning

## install

1. clone repository
2. `pip install -e .` to install for development with the `-e` editable option
3. You now can import flolang in python or you can execute it directly in console using `flolang`. This requires the `python3##/scripts/` directory to be in path.
4. `pip uninstall flolang` to uninstall