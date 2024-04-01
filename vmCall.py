#!/bin/python3

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
        # print((self.code.co_code, self.code.co_consts, self.code.co_names, self.code.co_varnames, self.code.co_argcount, self.isFunction))
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
                "BINARY_ADD": 23,
                "PUSH_EXC_INFO": 35,
                "CHECK_EXC_MATCH": 36,
                "RETURN_VALUE": 83,
                "POP_EXCEPT": 89,
                "STORE_NAME": 90,
                "LOAD_CONST": 100,
                "LOAD_NAME": 101,
                "BUILD_LIST": 103,
                "COMPARE_OP": 107,
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
                "RAISE_VARARGS": 130,
                "CALL_FUNCTION": 131,
                "RESUME": 151,
                "PRECALL": 166,
                "CALL": 171,
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

        while (cx < len(self.code)):
            op  = self.code[cx]
            arg = self.code[cx + 1]

            if op == self.opcodes["LOAD_GLOBAL"]:
                try:
                    if self.isFunction:
                        name = self.names[arg - 1]
                    else:
                        name = self.names[arg]
                except IndexError:
                    self.logging.error("LOAD_GLOBAL: Cannot get arg[{}]".format(arg))

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
            elif op == self.opcodes["BINARY_ADD"] or op == self.opcodes["BINARY_OP"]:
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
            elif op == self.opcodes["CALL_FUNCTION"]:
                args = []
                for argc in range(arg):
                    args.insert(0, pop())

                function = pop()
                push(function(*args))
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
                try:
                    name = self.names[arg]

                    lst = []

                    for _ in range(name):
                        item = pop()
                        lst.append(item)

                    push(lst)
                except Exception as e:
                    pass
            elif op == self.opcodes["RESUME"]:
                cx = arg
            elif op == self.opcodes["CACHE"]:
                pass
            elif op == self.opcodes["COMPARE_OP"]:
                b = pop()
                a = pop()
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
                args = []
                for argc in range(arg):
                    try:
                        args.insert(0, pop())
                    except IndexError:
                        self.logging.error("PRECALL: missing arg[{}]".format(argc))

                function = pop()
            elif op == self.opcodes["CALL"]:
                if arg:
                    push(function(*args))
                    function = None
                    args = []
            elif op == self.opcodes["POP_JUMP_FORWARD_IF_TRUE"]:
                b = pop()
                if b:
                    if self.isFunction:
                        cx += arg
                    while stk:
                        pop()
                        cx += arg
            elif op == self.opcodes["POP_JUMP_FORWARD_IF_FALSE"]:
                b = pop()
                if not b:
                    if self.isFunction:
                        cx += arg
                    if not stk:
                        cx += arg
                    while stk:
                        pop()
                        cx += arg
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
                cx += arg
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
                pass
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
