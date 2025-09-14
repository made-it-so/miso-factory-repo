
def add(num1, num2):
    return num1 + num2

def main():
    print("Welcome to the Calculator!")
    while True:
        user_input = input("Enter an operation (+/-/*) and two numbers (or 'q' to quit): ")
        if user_input.lower() == 'q':
            break
        try:
            op, num1_str, num2_str = user_input.split()
            num1 = float(num1_str)
            num2 = float(num2_str)
            if op in ['+', '-', '*']:
                result = eval(f"{num1} {op} {num2}")
                print(f"Result: {result:.2f}")
        except ValueError:
            print("Invalid input! Try again.")
        except ZeroDivisionError:
            print("Cannot divide by zero! Try again.")

if __name__ == "__main__":
    main()
