from vmCall import makeVM, VM

code1 = """
print({'name': 'Khanh', 'nickname': 'KhanhNguyen9872'}['nickname'])

for i in range(0, 5):
    print(i, end=' ')

value = 2
value2 = 3

match value:
    case 1:
        print(1)
    case 2:
        print("khanh")
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

if value == 1:
    print(value)
elif not value2 == False:
    print(value2)
else:
    print(f"not none {str(value)} a b {str(value2)} d")
"""


# def code2():
#     try:
#         a = 1
#         raise KeyError
#     except KeyError:
#         try:
#             raise MemoryError
#         except MemoryError:
#             a = 3
#     return a

# make pickle
codeObj1 = makeVM(code1)
# codeObj2 = makeVM(code2)
# print(codeObj1)
# print(codeObj2)

codeObj1.dis()
print(__import__('pickle').loads(codeObj1.pickle))

# create VM
# obj = VM(b'\x80\x04\x95W\x00\x00\x00\x00\x00\x00\x00C*d\x00Z\x00e\x01e\x00d\x01\x17\x00\x83\x01\x01\x00e\x01\x83\x00\x01\x00e\x01d\x02g\x01d\x03g\x01\x17\x00\x83\x01\x01\x00d\x04S\x00\x94(\x8c\nhello worl\x94\x8c\x01d\x94K\x02K\x03Nt\x94\x8c\x01v\x94\x8c\x05print\x94\x86\x94\x87\x94.')
obj1 = VM(codeObj1.pickle)
# obj2 = VM(codeObj2.pickle)
# print(obj)
# print(obj1)
# print(obj2)

# execute VM
obj1()
# print("> obj return: " + str(obj()))
# print("> obj1 return: " + str(obj1()))
# print("> obj2 return: " + str(obj2()))
