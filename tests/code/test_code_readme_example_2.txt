#!flolang

fn recur_factorial(int n) int:
    let mut int result = n
    if n != 1:
        result = n*recur_factorial(n-1)
    return result

fn main():
    let int num = 7

    # check if the number is negative
    if num < 0:
        print("Sorry, factorial does not exist for negative numbers")
    elif num == 0:
        print("Factorial is 1.")
    else:
        let int fac = recur_factorial(num)
        print("Factorial is")
        print(fac)

main()