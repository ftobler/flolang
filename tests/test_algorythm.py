import pytest
from tests.context import resolve_path
from flolang import tokenize, default_environment, parse, interpret, to_native, eval


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


# @pytest.mark.skip(reason="not yet implementable. Arrays don't work right now")
def test_crc_calculation_1():

    assert eval("""

fn crc8(int[] dat, int polynomial=0x07, int init_value=0x00) int:

    let mut int crc = init_value
    for byte in dat:
        crc ^=byte
        for _ in 0..8:
            if crc & 0x80:
                crc = (crc << 1) ^ polynomial
            else:
                crc <<= 1
            crc &= 0xFF  # Ensure CRC remains 8-bit
    return crc

crc8([1,2,3,4])

""") == crc8([1, 2, 3, 4])


def test_crc_calculation_2():

    assert eval("""

fn crc8_update(int dat, int polynomial=0x07) int:
    crc ^= dat
    for int _ in 0..8:
        if crc & 0x80:
            crc = (crc << 1) ^ polynomial
        else:
            crc = crc << 1
        crc &= 0xFF  # Ensure CRC remains 8-bit
    return crc

let int init_value = 0x00
let mut int crc = init_value
for int i in 1..5:
    crc = crc8_update(i)

crc

""") == crc8([1, 2, 3, 4])


def test_crc_calculation_3():

    # this time overload the polynominal default value
    assert eval("""

fn crc8_update(int dat, int polynomial=0x07) int:
    crc ^= dat
    for int _ in 0..8:
        if crc & 0x80:
            crc = (crc << 1) ^ polynomial
        else:
            crc = crc << 1
        crc &= 0xFF  # Ensure CRC remains 8-bit
    return crc

let int init_value = 0x00
let int polynomial = 0x10
let mut int crc = init_value
for int i in 1..5:
    crc = crc8_update(i, polynomial)

crc

""") == crc8([1, 2, 3, 4], 0x10)


def test_factorial_variant_1():

    assert eval("""

# Factorial of a number using recursion

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

fac

""") == 5040


def test_factorial_variant_2():

    assert eval("""

# Factorial of a number using recursion

fn recur_factorial(int n) int:
    if n == 1:
        return n
    else:
        return n*recur_factorial(n-1)

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

fac

""") == 5040


def test_factorial_variant_3():

    assert eval("""

# Factorial of a number using recursion

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

fac

""") == 5040


# @pytest.mark.skip(reason="Need to debug what goes wrong here")
def test_factorial_variant_4():

    assert eval("""

# Factorial of a number using recursion

fn recur_factorial(int n) int:
    let mut int result = 0
    if n == 1:
        result = n
    else:
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

fac

""") == 5040


def test_calc_pi_variant_1():
    assert eval("""

fn printValueOfPi():
    let float newpi = round(2 * acos(0.0) * 1000) / 1000
    print(newpi)
    return newpi

printValueOfPi()

""") == 3.142


def test_calc_pi_variant_2():
    assert eval("""

# Function that prints the
# value of pi upto N
# decimal places
fn printValueOfPi() int:
    # Find value of pi upto 3 places
    # using acos() function
    let float newpi = round(2 * acos(0.0) * 1000) / 1000
    # Print value of pi upto
    # N decimal places
    print(newpi)
    return newpi

printValueOfPi()

""") == 3.142


def test_calc_pi_variant_3():
    assert eval("""

# Initialize denominator
let mut int k = 1

# Initialize sum
let mut float s = 0

let int n = 100
let mut int i = 0
while i < n:
    if i % 2 == 0: # even index elements are positive
        s += 4/k
    else:
        s -= 4/k # odd index elements are negative
    k += 2 # denominator is odd
    i += 1

s

""") == 3.1315929035585537


def test_calc_pi_variant_4():
    assert eval("""

# Initialize denominator
let mut int k = 1

# Initialize sum
let mut float s = 0

for int i in 100:
    if i % 2 == 0: # even index elements are positive
        s += 4/k
    else:
        s -= 4/k # odd index elements are negative
    k += 2 # denominator is odd
    i += 1

s

""") == 3.1315929035585537
