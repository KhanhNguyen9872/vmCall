from vmCall import makeVM, VM

code1 = """
a = 2
b = 5
print(b)
print("Hello World!")
if ~b:
    print(not b is a)
else:
    print(a)
"""

def code2():
    try:
        a = 1
        raise KeyError
    except KeyError:
        try:
            raise MemoryError
        except MemoryError:
            a = 3
    return a

# make pickle
codeObj1 = makeVM(code1)
codeObj2 = makeVM(code2)
print(codeObj1)
print(codeObj2)

# create VM
obj = VM(b'\x80\x04\x95W\x00\x00\x00\x00\x00\x00\x00C*d\x00Z\x00e\x01e\x00d\x01\x17\x00\x83\x01\x01\x00e\x01\x83\x00\x01\x00e\x01d\x02g\x01d\x03g\x01\x17\x00\x83\x01\x01\x00d\x04S\x00\x94(\x8c\nhello worl\x94\x8c\x01d\x94K\x02K\x03Nt\x94\x8c\x01v\x94\x8c\x05print\x94\x86\x94\x87\x94.')
obj1 = VM(codeObj1.pickle)
obj2 = VM(codeObj2.pickle)
print(obj)
print(obj1)
print(obj2)

# execute VM
print("> obj return: " + str(obj()))
print("> obj1 return: " + str(obj1()))
print("> obj2 return: " + str(obj2()))
