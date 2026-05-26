def calculate(num1, operator, num2):
    if operator == "+":
        return (num1 + num2)
    elif operator == '-':
        return (num1 - num2)
    elif operator == '*':
        return (num1*num2)
    elif operator == '/':
        return (num1/num2)
    else:
        print ("Invalid operator")
num1 = int(input("What is your 1st number: "))
operator = input("What do you want to do with it: ")
num2 = int(input("What is your 2nd number: "))

print (calculate(num1, operator, num2))

