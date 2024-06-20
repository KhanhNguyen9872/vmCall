from vmCall import makeVM, VM
# import pickle

# code = compile(open('simple_ball_fix.py','rb').read(), '', 'exec')
# # print(code)
# """
# <code object <module> at 0x1691fd0, file "", line 1>
# """

# # make pickle
# codeObj = makeVM(code)
# # print(pickle.loads(codeObj.pickle))

# # print(codeObj.dis())
# # print(codeObj)
# """
# <makeVM object at 0x7f48f66a1cd0>
# """

# # write to file (you can read this file and make a vm below in another python version)
# open('test.pickle', 'wb').write(codeObj.pickle)

# make a vm emulated
data = open('simple_ball_311.pickle', 'rb').read()
obj = VM(data)
# print(obj)
"""
<VM object at 0x7fa092670a50>
"""

# execute object
obj()