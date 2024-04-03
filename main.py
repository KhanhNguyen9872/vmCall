from vmCall import makeVM, VM

code1 = """
def outer_function():
    x = 10
    y = 10
    a = 1
    def inner_function():
        print(x)
    return inner_function()
print(outer_function())
"""

code1 = """
print({'name': 'Khanh', 'nickname': 'KhanhNguyen9872'}['nickname'])

while 1:
    if True:
        print("Oh")
        break
    else:
        continue

for i in range(0, 9):
    print(f"i={str(i)},", end = ' ', flush = True)

value = 1
value2 = 3

if value == None:
    exit(0)
elif value == False:
    exit(0)
else:
    value = 2

match value:
    case 1:
        print(1)
    case 2:
        print("value is 2")
    case 3:
        print(3)

match value2:
    case 1:
        print(1)
    case 2:
        print(2)
    case 3:
        value2 = True

print(value2)
value = "Khanh"

print(f"My name is {value}")
"""


code1 = """
def solve_quadratic(a, b, c):
    delta = b**2 - 4*a*c
    
    if delta > 0:
        x1 = (-b + delta**0.5) / (2*a)
        x2 = (-b - delta**0.5) / (2*a)
        return x1, x2
    elif delta == 0:
        x = -b / (2*a)
        return x
    else:
        return None

a = 1
b = -3
c = 2
x1, x2 = solve_quadratic(a, b, c)
print("Nghiệm của phương trình {}x^2 + {}x + {} là: {} {}".format(a, b, c, x1, x2))
"""

code1 = r"""
a = 12345
def is_prime(n = 7, divisor = 2):
    if n <= 1:
        return False
    elif n == 2:
        return True
    elif n % divisor == 0:
        return False
    elif divisor * divisor > n:
        return True
    else:
        return is_prime(n, divisor + 1)

# Kiểm tra số 7 có phải là số nguyên tố hay không
print(is_prime())  # Output: True

# Kiểm tra số 10 có phải là số nguyên tố hay không
print(is_prime(10))  # Output: False
"""

# code1 = """


# """

# make pickle
codeObj1 = makeVM(code1)
# codeObj2 = makeVM(code2)
# print(codeObj1)
# print(codeObj2)

# codeObj1.dis()
# print(__import__('pickle').loads(codeObj1.pickle))

# create VM
# obj = VM(b'\x80\x04\x95W\x00\x00\x00\x00\x00\x00\x00C*d\x00Z\x00e\x01e\x00d\x01\x17\x00\x83\x01\x01\x00e\x01\x83\x00\x01\x00e\x01d\x02g\x01d\x03g\x01\x17\x00\x83\x01\x01\x00d\x04S\x00\x94(\x8c\nhello worl\x94\x8c\x01d\x94K\x02K\x03Nt\x94\x8c\x01v\x94\x8c\x05print\x94\x86\x94\x87\x94.')
obj1 = VM(codeObj1.obj)
# obj1.__dis__()
# obj2 = VM(codeObj2.pickle)
# print(obj)
# print(obj1)
# print(obj2)

# execute VM
obj1()
# print("> obj return: " + str(obj()))
# print("> obj1 return: " + str(obj1()))
# print("> obj2 return: " + str(obj2()))
