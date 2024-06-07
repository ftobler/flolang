import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.context import resolve_path
from flolang import tokenize, default_environment, parse, interpret, to_native, eval
import pytest

@pytest.mark.skip(reason="not yet implementable")
def test_crc_calculation():

    def crc8(data: bytes, polynomial=0x07, init_value=0x00):
        # Compute CRC-8 checksum.
        # :param data: Input data as bytes
        # :param polynomial: Polynomial to use for calculation (default is 0x07)
        # :param init_value: Initial value for CRC (default is 0x00)
        # :return: Computed CRC-8 value
        crc = init_value
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ polynomial
                else:
                    crc <<= 1
                crc &= 0xFF  # Ensure CRC remains 8-bit
        return crc

    assert eval("""

""") == 120


def test_factorial_variant_1():

    assert eval("""

# Factorial of a number using recursion

fn recur_factorial(int n) int:
    let int result = n
    if n != 1:
        result = n*recur_factorial(n-1)
    return result

let int num = 7
let int fac

# check if the number is negative
if num < 0:
    fac = "Sorry, factorial does not exist for negative numbers"
elif num == 0:
    fac = 1
else:
    fac = recur_factorial(num)

fac

""") == 5040

@pytest.mark.skip(reason="not yet implemented correctly. return in if case does not work")
def test_factorial_variant_2():

    assert eval("""

# Factorial of a number using recursion

fn recur_factorial(int n):
    if n == 1:
        return n
    else:
        return n*recur_factorial(n-1)

let int num = 7
let int fac

# check if the number is negative
if num < 0:
    fac = "Sorry, factorial does not exist for negative numbers"
elif num == 0:
    fac = 1
else:
    fac = recur_factorial(num)

fac

""") == 5040

def test_factorial_variant_3():

    assert eval("""

# Factorial of a number using recursion

fn recur_factorial(int n):
    let int result
    if n == 1:
        result = n
    else:
        result = n*recur_factorial(n-1)
    return result

let int num = 7
let int fac

# check if the number is negative
if num < 0:
    fac = "Sorry, factorial does not exist for negative numbers"
elif num == 0:
    fac = 1
else:
    fac = recur_factorial(num)

fac

""") == 5040

def test_calc_pi_variant_1():
    assert eval("""

fn printValueOfPi():
    let int newpi = round(2 * acos(0.0) * 1000) / 1000
    print(newpi)
    return newpi

printValueOfPi()

""") == 3.142

@pytest.mark.skip(reason="implementatnion error in whitespace. currently would fail")
def test_calc_pi_variant_2():
    assert eval("""

# Function that prints the
# value of pi upto N
# decimal places
fn printValueOfPi():
    # Find value of pi upto 3 places
    # using acos() function
    let int newpi = round(2 * acos(0.0) * 1000) / 1000
    # Print value of pi upto
    # N decimal places
    print(newpi)
    return newpi

printValueOfPi()

""") == 3.142

def test_calc_pi_variant_3():
    assert eval("""

# Initialize denominator
let int k = 1

# Initialize sum
let int s = 0

const int n = 100
let int i = 0
while i < n:
    if i % 2 == 0: # even index elements are positive
        s += 4/k
    else:
        s -= 4/k # odd index elements are negative
    k += 2 # denominator is odd
    i += 1

s

""") == 3.1315929035585537

