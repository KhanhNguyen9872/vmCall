#!/bin/python3

__import__('_pickle')
__import__('sys')
__import__('builtins')
__import__('marshal')
__import__('dis')
__import__('logging')

class makeVM:
    def __init__(self, code):
        self.VM_addr = __import__('builtins').hex(__import__('builtins').id(self))
        self.isFunction = False
        if str(type(code)) == "<class 'function'>":
            code = code.__code__
            self.isFunction = True
        elif str(type(code)) != "<class 'code'>":
            code = compile(code, "VM", "exec")

        self.code = code
        return None

    def __repr__(self):
        return "<makeVM object at {addr}>".format(addr = self.VM_addr)

    @property
    def pickle(self):
        return __import__('_pickle').dumps((self.code.co_code, self.code.co_consts, self.code.co_names, self.code.co_varnames, self.code.co_argcount, self.isFunction))

    @property
    def marshal(self):
        return __import__('marshal').dumps(self.code)

    def dis(self):
        __import__('dis').dis(self.code)
        return None

class VM:
    def __init__(self, pickle_data):
        self.pickle = __import__('_pickle')
        if str(type(pickle_data)) == "<class 'code'>":
            unpickle = (pickle_data.co_code, pickle_data.co_consts, pickle_data.co_names,)
        else:
            try:
                unpickle = self.pickle.loads(pickle_data)
            except Exception:
                raise TypeError("Cannot create VM from this code!")
        self.code = unpickle[0]
        self.consts = unpickle[1]
        self.names = unpickle[2]
        try:
            self.varnames = unpickle[3]
        except IndexError:
            self.varnames = ()
        try:
            self.arg_count = unpickle[4]
        except IndexError:
            self.arg_count = 0
        try:
            self.isFunction = unpickle[5]
        except IndexError:
            self.isFunction = False

        self.vmGlobals = vars(__import__('builtins')).copy()

        class dir:
            def __init__(self, addr):
                self.addr = addr
                return None
            def __call__(self):
                return []
            def __repr__(self):
                return "<built-in method __dir__ of VM object at {addr}>".format(addr = self.addr)
        self.VM_addr = __import__('builtins').hex(__import__('builtins').id(self))
        self.logging = __import__('logging')
        self.__dir__ = dir(self.VM_addr)
        self.opcodes = {
            "3.10": {
                "POP_TOP": 1,
                "PUSH_NULL": 2,
                "BINARY_ADD": 23,
                "BINARY_OP": 23,
                "STORE_NAME": 90,
                "LOAD_CONST": 100,
                "LOAD_NAME": 101,
                "LOAD_GLOBAL": 116,
                "CALL_FUNCTION": 131,
            },
            "3.11": {
                "CACHE": 0,
                "POP_TOP": 1,
                "PUSH_NULL": 2,
                "NOP": 9,
                "UNARY_POSITIVE": 10,
                "UNARY_NEGATIVE": 11,
                "UNARY_NOT": 12,
                "UNARY_INVERT": 15,
                "BINARY_SUBSCR": 25,
                "PUSH_EXC_INFO": 35,
                "CHECK_EXC_MATCH": 36,
                "GET_ITER": 68,
                "RETURN_VALUE": 83,
                "IMPORT_STAR": 84,
                "POP_EXCEPT": 89,
                "STORE_NAME": 90,
                "FOR_ITER": 93,
                "STORE_ATTR": 95,
                "DELETE_ATTR": 96,
                "LOAD_CONST": 100,
                "LOAD_NAME": 101,
                "BUILD_LIST": 103,
                "BUILD_SET": 104,
                "BUILD_MAP": 105,
                "LOAD_ATTR": 106,
                "COMPARE_OP": 107,
                "IMPORT_NAME": 108,
                "IMPORT_FROM": 109,
                "JUMP_FORWARD": 110,
                "POP_JUMP_FORWARD_IF_FALSE": 114,
                "POP_JUMP_FORWARD_IF_TRUE": 115,
                "LOAD_GLOBAL": 116,
                "IS_OP": 117,
                "RERAISE": 119,
                "COPY": 120,
                "BINARY_OP": 122,
                "LOAD_FAST": 124,
                "STORE_FAST": 125,
                "DELETE_FAST": 126,
                "POP_JUMP_FORWARD_IF_NOT_NONE": 128,
                "POP_JUMP_FORWARD_IF_NONE": 129,
                "RAISE_VARARGS": 130,
                "JUMP_BACKWARD": 140,
                "RESUME": 151,
                "FORMAT_VALUE": 155,
                "BUILD_CONST_KEY_MAP": 156,
                "BUILD_STRING": 157,
                "LOAD_METHOD": 160,
                "LIST_EXTEND": 162,
                "SET_UPDATE": 163,
                "DICT_MERGE": 164,
                "DICT_UPDATE": 165,
                "PRECALL": 166,
                "CALL": 171,
                "KW_NAMES": 172,
            },
            "3.12": {
                "CACHE": 0,
                "POP_TOP": 1,
                "PUSH_NULL": 2,
            }
        }

        self.version = "{major}.{minor}".format(major = __import__('sys').version_info.major, minor = __import__('sys').version_info.minor)
        self.opcodes = self.opcodes[self.version]
        return None

    @property
    def __dict__(self):
        return {}

    def __repr__(self):
        return "<VM object at {addr}>".format(addr = self.VM_addr)

    def __call__(self, *args, **kwargs):
        if args:
            for i in range(len(args)):
                if i < self.arg_count:
                    name = self.varnames[i]
                    self.vmGlobals[name] = args[i]
                else:
                    raise TypeError("VM takes {} positional arguments but {} were given".format(self.arg_count, len(args)))

        if kwargs:
            for name in kwargs:
                if name in self.varnames[:self.arg_count]:
                    self.vmGlobals[name] = kwargs[name]
                else:
                    raise TypeError("VM got an unexpected keyword argument '{}'".format(name))

        cx  = 0
        stk = []
        push = stk.append
        pop  = stk.pop
        args = []
        kwargs = {}

        while (cx < len(self.code)):
            # print(cx)
            if (cx % 2 != 0):
                raise ValueError("op must is even ({})".format(cx))

            op  = self.code[cx]
            arg = self.code[cx + 1]

            if op == self.opcodes["LOAD_GLOBAL"]:
                try:
                    if self.isFunction:
                        name = self.names[arg - 1]
                    else:
                        name = self.names[arg]
                except IndexError:
                    self.logging.error("LOAD_GLOBAL: Cannot get args[{}]".format(arg))

                try:
                    name = self.vmGlobals[name]
                    push(name)
                except KeyError:
                    raise NameError("LOAD_GLOBAL: Cannot get {} in GLOBAL".format(self.names[arg]))
            elif op == self.opcodes["LOAD_CONST"]:
                const = self.consts[arg]
                push(const)
            elif op == self.opcodes["LOAD_NAME"]:
                name = self.names[arg]
                try:
                    name = self.vmGlobals[name]
                except KeyError:
                    raise NameError("LOAD_NAME: Name '{}' is not defined".format(name))
                push(name)
            elif op == self.opcodes["BINARY_OP"]:
                b = pop()
                a = pop()
                c = False
                match arg:
                    case 0:
                        c = (a + b)
                    case 1:
                        c = (a & b)
                    case 2:
                        c = (a // b)
                    case 3:
                        c = (a << b)
                    case 4:
                        c = (a @ b)
                    case 5:
                        c = (a * b)
                    case 6:
                        c = (a % b)
                    case 7:
                        c = (a | b)
                    case 8:
                        c = (a ** b)
                    case 9:
                        c = (a >> b)
                    case 10:
                        c = (a - b)
                    case 11:
                        c = (a / b)
                    case 12:
                        c = (a ^ b)
                    case _:
                        self.logging.error("BINARY_OP: Unsupported ({arg})".format(arg = arg))

                push(c)
            elif op == self.opcodes["POP_TOP"]:
                try:
                    pop()
                except IndexError:
                    pass
            elif op == self.opcodes["PUSH_NULL"]:
                push(None)
            elif op == self.opcodes["STORE_NAME"]:
                v = pop()
                name = self.names[arg]
                self.vmGlobals[name] = v
            elif op == self.opcodes["STORE_FAST"]:
                v = pop()
                try:
                    name = self.varnames[arg]
                except IndexError:
                    name = "__varname__{}".format(arg)

                self.vmGlobals[name] = v
            elif op == self.opcodes["DELETE_FAST"]:
                try:
                    name = self.varnames[arg]
                except IndexError:
                    name = "__varname__{}".format(arg)

                try:
                    del self.vmGlobals[name]
                except KeyError:
                    pass
            elif op == self.opcodes["LOAD_FAST"]:
                try:
                    name = self.varnames[arg]
                except IndexError:
                    name = "__varname__{}".format(arg)

                try:
                    name = self.vmGlobals[name]
                    push(name)
                except KeyError:
                     raise NameError("LOAD_FAST: Name '{}' is not defined".format(name))
            elif op == self.opcodes["RETURN_VALUE"]:
                return pop()
            elif op == self.opcodes["BUILD_LIST"]:
                push([])
            elif op == self.opcodes["RESUME"]:
                cx = arg
            elif op == self.opcodes["CACHE"]:
                pass
            elif op == self.opcodes["COMPARE_OP"]:
                b = pop()
                try:
                    a = pop()
                except IndexError:
                    try:
                        a = copy
                    except NameError:
                        raise IndexError("pop from empty list")
                c = False

                match arg:
                    case 0:
                        c = (a < b)
                    case 1:
                        c = (a <= b)
                    case 2:
                        c = (a == b)
                    case 3:
                        c = (a != b)
                    case 4:
                        c = (a > b)
                    case 5:
                        c = (a >= b)
                    case _:
                        self.logging.error("COMPARE_OP: Unsupported ({arg})".format(arg = arg))
                    
                push(c)
            elif op == self.opcodes["PRECALL"]:
                for argc in range(arg):
                    try:
                        data = pop()
                        if str(type(data)) == "<class 'dict'>":
                            try:
                                name = list(data)[0]
                                if ("KW_NAMES__" + name in kwargs):
                                    kwargs[name] = kwargs.pop("KW_NAMES__" + name)
                                    continue
                            except ValueError:
                                pass
                        args.insert(0, data)
                    except IndexError:
                        self.logging.error("PRECALL: missing args[{}]".format(argc))

                if stk[-1] == None:
                    pop()
                function = pop()
            elif op == self.opcodes["CALL"]:
                push(function(*args, **kwargs))
                function = None
                args = []
                kwargs = {}
            elif op == self.opcodes["POP_JUMP_FORWARD_IF_TRUE"]: # uncompleted
                b = pop()
                arg = arg * 2

                if b:
                    if not stk:
                        push(b)
                    if self.isFunction:
                        cx += arg
                    while stk:
                        pop()
                        cx += arg
            elif op == self.opcodes["POP_JUMP_FORWARD_IF_FALSE"]: # uncompleted
                b = pop()
                arg = arg * 2

                if not b:
                    if not stk:
                        push(b)
                    if self.isFunction:
                        cx += arg
                    while stk:
                        pop()
                        cx += arg
                    # cx += arg
            elif op == self.opcodes["IS_OP"]:
                b = pop()
                a = pop()
                c = (a is b)
                if arg:
                    c = not c
                push(c)
            elif op == self.opcodes["UNARY_POSITIVE"]:
                push(+pop())
            elif op == self.opcodes["UNARY_NEGATIVE"]:
                push(-pop())
            elif op == self.opcodes["UNARY_NOT"]:
                push(not pop())
            elif op == self.opcodes["UNARY_INVERT"]:
                push(~pop())
            elif op == self.opcodes["RAISE_VARARGS"]:
                if arg == 1:
                    raise_var = pop()
            elif op == self.opcodes["NOP"]:
                pass
            elif op == self.opcodes["JUMP_FORWARD"]:
                if self.isFunction:
                    cx += arg
                while stk:
                    pop()
                    cx += arg
                cx += arg
            elif op == self.opcodes["JUMP_BACKWARD"]: # uncompleted
                # print(cx)
                if self.isFunction:
                    cx -= arg
                cx -= arg
                cx -= arg
                # print(stk)
                # print(cx)
                # print(stk)
                pass
            elif op == self.opcodes["PUSH_EXC_INFO"]:
                push(raise_var)
            elif op == self.opcodes["POP_EXCEPT"]:
                pass
            elif op == self.opcodes["CHECK_EXC_MATCH"]:
                b = pop()
                a = pop()
                push(a == b)
            elif op == self.opcodes["RERAISE"]: # uncompleted
                if arg == 1:
                    pass
            elif op == self.opcodes["COPY"]: # uncompleted
                if stk:
                    value = pop()
                try:
                    if copy != value:
                        copy = value
                except(NameError, UnboundLocalError):
                    copy = value
                push(copy)
            elif op == self.opcodes["GET_ITER"]:
                data = pop()
                t = str(type(data))
                if (t == "<class 'range'>"):
                    for i in range(data[-1], data[0] - 1, -1):
                        push(i)
                elif (t == "<class 'tuple'>") or (t == "<class 'list'>"):
                    for i in data[::-1]:
                        push(i)
                elif (t == "<class 'dict'>"):
                    pass
                push(None)
            elif op == self.opcodes["FOR_ITER"]:
                if list(set(stk)) == [None]:
                    for i in stk:
                        pop()
                        cx += arg
                pop()
            elif op == self.opcodes["LIST_EXTEND"]:
                if arg == 1:
                    extend = pop()
                    lst = pop()
                    for i in extend:
                        lst.append(i)
                push(lst)
            elif op == self.opcodes["BUILD_CONST_KEY_MAP"]:
                data = {}
                items = pop()
                for i in items[::-1]:
                    data[i] = pop()
                data = {key: value for key, value in list(data.items())[::-1]}
                push(data)
            elif op == self.opcodes["BINARY_SUBSCR"]:
                item = pop()
                data = pop()[item]
                push(data)
            elif op == self.opcodes["IMPORT_NAME"]:
                name = self.names[arg]
                push(__import__(name))
            elif op == self.opcodes["IMPORT_FROM"]:
                data = pop()
                name = pop()
                
                if arg != len(name):
                    push(name)
                push(data)
                push(getattr(data, name[arg - 1]))
            elif op == self.opcodes["LOAD_ATTR"]:
                name = self.names[arg]
                data = pop()
                push(getattr(data, name))
            elif op == self.opcodes["DELETE_ATTR"]:
                data = pop()
                name = self.names[arg]
                delattr(data, name)
            elif op == self.opcodes["STORE_ATTR"]:
                data = pop()
                value = pop()
                name = self.names[arg]
                setattr(data, name, value)
            elif op == self.opcodes["IMPORT_STAR"]:
                data = vars(pop())
                name = pop()

                for i in data:
                    self.vmGlobals[i] = data[i]
            elif op == self.opcodes["LOAD_METHOD"]:
                name = self.names[arg]
                data = pop()
                push(getattr(data, name))
            elif op == self.opcodes["POP_JUMP_FORWARD_IF_NONE"]:
                b = pop()
                b = b is None
                arg = arg * 2

                if b:
                    if not stk:
                        push(b)
                    if self.isFunction:
                        cx += arg
                    while stk:
                        pop()
                        cx += arg
            elif op == self.opcodes["POP_JUMP_FORWARD_IF_NOT_NONE"]:
                b = pop()
                b = b is None
                arg = arg * 2

                if not b:
                    if not stk:
                        push(b)
                    if self.isFunction:
                        cx += arg
                    
                    while stk:
                        pop()
                        cx += arg
            elif op == self.opcodes["BUILD_SET"]:
                push(set({}))
            elif op == self.opcodes["SET_UPDATE"]:
                value = pop()
                data = pop()
                data = set(value)
                push(data)
            elif op == self.opcodes["BUILD_MAP"]:
                push(set({}))
            elif op == self.opcodes["FORMAT_VALUE"]:
                value = pop()
                data = pop()
                if not data:
                    data = pop()
                push(data)
                push(value)
            elif op == self.opcodes["BUILD_STRING"]:
                value = ""
                data = stk[-arg:]
                for i in range(arg):
                    pop()
                for i in data:
                    value = value + i
                push(value)
            elif op == self.opcodes["KW_NAMES"]:
                data = {}
                const = self.consts[arg]
                while const:
                    name = const[-1]
                    const = const[:-1]
                    data[name] = pop()
                data = {key: value for key, value in list(data.items())[::-1]}
                
                for item in data:
                    name = {item: data[item]}
                    kwargs["KW_NAMES__" + str(item)] = data[item]
                    push(name)
            else:
                name_opcode = None
                for key, value in self.opcodes.items():
                    if value == op:
                        name_opcode = key + " (" + str(op) + ")"
                        break
                if not name_opcode:
                    name_opcode = str(op)
                
                self.logging.error("Unsupported opcode: " + name_opcode)

            cx += 2
