#!/bin/python3

__import__('_pickle')
__import__('sys')
__import__('builtins')
__import__('marshal')
__import__('dis')
__import__('logging')
__import__('types')
__import__('sys').setrecursionlimit(1000000000)

class makeVM:
    def __init__(self, code):
        self.VM_addr = __import__('builtins').hex(__import__('builtins').id(self))
        self.version = "{major}.{minor}".format(major = __import__('sys').version_info.major, minor = __import__('sys').version_info.minor)
        if self.version != "3.11":
            raise TypeError("makeVM(): Only supported makeVM in python3.11")
        self.logging = __import__('logging')
        self.isFunction = 0
        type_code = str(type(code))
        if type_code == "<class 'function'>" or type_code == "<class 'method'>":
            code = code.__code__
            self.isFunction = 1
        elif type_code == "<class 'str'>" or type_code == "<class 'bytes'>":
            code = compile(code, "VM", "exec")
        elif type_code == "<class 'code'>":
            pass
        else:
            raise TypeError("makeVM() arg 1 must be a string, bytes, method, code object or function. Found {} ({})".format(type(code), str(code)))

        self.code = code
        data = {}
        obj = [
            "FOR_ITER",
            "JUMP_FORWARD",
            "POP_JUMP_FORWARD_IF_FALSE",
            "POP_JUMP_FORWARD_IF_TRUE",
            "POP_JUMP_FORWARD_IF_NOT_NONE",
            "POP_JUMP_FORWARD_IF_NONE",
            "JUMP_BACKWARD",
            "POP_JUMP_BACKWARD_IF_NOT_NONE",
            "POP_JUMP_BACKWARD_IF_NONE",
            "POP_JUMP_BACKWARD_IF_FALSE",
            "POP_JUMP_BACKWARD_IF_TRUE"
        ]
        self.dis_data = self.__extract_dis__(self.__dis__(self.code.co_code))
        for i in self.dis_data:
            if self.dis_data[i]['name'] in obj:
                data[i] = self.dis_data[i]
                data[i].pop('name')
        self.obj = (self.code.co_code, self.code.co_consts, self.code.co_names, self.code.co_varnames, self.code.co_argcount, self.isFunction, data,)
        
        self.obj = list(self.obj)
        self.obj[1] = list(self.obj[1])
        for i in range(len(self.obj[1])):
            if str(type(self.obj[1][i])) == "<class 'code'>":
                # self.logging.warning("makeVM(): found 'code object' at co_consts[{}], this 'pickle data' will not work on another 'python{}'".format(i, self.version))
                data = makeVM(self.obj[1][i])
                data = list(data.obj)
                data[5] = 1
                data = tuple(data)
                self.obj[1][i] = {'vmObj': data}
                # self.obj[1][i] = {'codeObj': "__import__('marshal').loads(__import__('zlib').decompress(__import__('base64').b85decode({code})))".format(code = str(__import__('base64').b85encode(__import__('zlib').compress(__import__('marshal').dumps(self.obj[1][i])))))}
        self.obj[1] = tuple(self.obj[1])
        self.obj = tuple(self.obj)
        return None
    
    def __dis__(self, code = None):
        if code == None:
            code = self.code
        
        class std:
            def __init__(self):
                self.text = ""
                return
            def write(self, text):
                self.text = self.text + str(text)
                return

        stdout = __import__('sys').stdout
        __import__('sys').stdout = std()

        __import__('dis').dis(code)

        text = __import__('sys').stdout.text
        __import__('sys').stdout = stdout
        return text

    def __extract_dis__(self, dis):
        dis = [i for i in dis.split('\n') if i]
        for i in range(len(dis)):
            dis[i] = dis[i].split()
            if dis[i][0] == '>>':
                dis[i] = dis[i][1:]
            if dis[i][1] == 'COMPARE_OP':
                dis[i] = dis[i][:-1]
        new_dict = {}
        for i in dis:
            try:
                i[0] = int(i[0])
                j = {}
                for o in range(1, len(i), 1):
                    try:

                        if o == 1:
                            name = 'name'
                        elif o == 2:
                            i[o] = int(i[o])
                            name = 'arg'
                        elif o == 3:
                            if i[o] == '(to' or j['name'] == 'BINARY_OP':
                                continue
                            else:
                                name = i[o]
                                if name[0] == '(' and name[-1] == ')':
                                    i[o] = name[1:-1]
                                    name = 'varname'
                                else:
                                    continue
                                    print("case: {} - {}".format(o, i[1:]))
                                    # input()
                        elif o == 4:
                            name = 'jump_to'
                            i[o] = int(i[o][:-1])
                        else:
                            continue
                            print("case: {} - {}".format(o, i[1:]))
                            # input()

                        j[name] = i[o]
                    except ValueError:
                        continue
                    except Exception as e:
                        self.logging.error("__extract_dis__: {}".format(str(e)))

                new_dict[int(i[0])] = j
            except ValueError:
                continue

        return new_dict

    def __repr__(self):
        return "<makeVM object at {addr}>".format(addr = self.VM_addr)

    @property
    def pickle(self):
        return __import__('_pickle').dumps(self.obj)

    @property
    def marshal(self):
        return __import__('marshal').dumps(self.code)

    def dis(self):
        __import__('dis').dis(self.code)
        return None

class VM:
    def __init__(self, pickle_data):
        self.version = "{major}.{minor}".format(major = __import__('sys').version_info.major, minor = __import__('sys').version_info.minor)

        self.pickle = __import__('_pickle')
        if str(type(pickle_data)) == "<class 'code'>":
            unpickle = (pickle_data.co_code, pickle_data.co_consts, pickle_data.co_names,)
        elif str(type(pickle_data)) == "<class 'tuple'>":
            unpickle = pickle_data
        elif str(type(pickle_data)) == "<class 'bytes'>":
            try:
                unpickle = self.pickle.loads(pickle_data)
            except Exception as e:
                raise TypeError("Cannot create VM from this code! [{}]".format(e))
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
            self.isFunction = 0
        try:
            self.dis_data = unpickle[6]
        except IndexError:
            self.dis_data = 0

        self.mainClass = None
        self.vmGlobals2 = vars(__import__('builtins')).copy()
        self.vmGlobals = {
            '__name__': '__main__', 
            '__doc__': None, 
            '__file__': 'main.py',
            '__cached__': None,
            '__package__': None, 
            '__loader__': globals()['__loader__'], 
            '__spec__': None, 
            '__annotations__': {}, 
            '__builtins__': self.vmGlobals2,
        }
        # print(self.vmGlobals)
        # print(self.vmGlobals2)

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
        self.types = __import__('types')
        self.__dir__ = dir(self.VM_addr)
        self.opcodes = {
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
            "STORE_SUBSCR": 60,
            "GET_ITER": 68,
            "LOAD_BUILD_CLASS": 71,
            "LIST_TO_TUPLE": 82,
            "RETURN_VALUE": 83,
            "IMPORT_STAR": 84,
            "POP_EXCEPT": 89,
            "STORE_NAME": 90,
            "DELETE_NAME": 91,
            "UNPACK_SEQUENCE": 92,
            "FOR_ITER": 93,
            "STORE_ATTR": 95,
            "DELETE_ATTR": 96,
            "STORE_GLOBAL": 97,
            "DELETE_GLOBAL": 98,
            "SWAP": 99,
            "LOAD_CONST": 100,
            "LOAD_NAME": 101,
            "BUILD_TUPLE": 102,
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
            "CONTAINS_OP": 118,
            "RERAISE": 119,
            "COPY": 120,
            "BINARY_OP": 122,
            "LOAD_FAST": 124,
            "STORE_FAST": 125,
            "DELETE_FAST": 126,
            "POP_JUMP_FORWARD_IF_NOT_NONE": 128,
            "POP_JUMP_FORWARD_IF_NONE": 129,
            "RAISE_VARARGS": 130,
            "MAKE_FUNCTION": 132,
            "BUILD_SLICE": 133,
            "MAKE_CELL": 135,
            "LOAD_CLOSURE": 136,
            "STORE_DEREF": 138,
            "JUMP_BACKWARD": 140,
            "EXTENDED_ARG": 144,
            "LIST_APPEND_A": 145,
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
            "POP_JUMP_BACKWARD_IF_NOT_NONE": 173,
            "POP_JUMP_BACKWARD_IF_NONE": 174,
            "POP_JUMP_BACKWARD_IF_FALSE": 175,
            "POP_JUMP_BACKWARD_IF_TRUE": 176
        }

        # self.opcodes = self.opcodes[self.version]
        return None

    @property
    def __dict__(self):
        return {}

    def __repr__(self):
        return "<VM object at {addr}>".format(addr = self.VM_addr)

    def __call__(self, *args, **kwargs):

        def get_jump_to(name, cx):
            try:
                return self.dis_data[cx]['jump_to'] - 2
            except (IndexError, ValueError, KeyError):
                raise TypeError("{}: cannot get jump_to from dis_data (op = {})".format(name, cx))

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

        if len(args) < self.arg_count and self.isFunction == 1:
            try:
                data = self.consts[-1]['default']
                if type(data) == type([]):   
                    args = self.arg_count - len(args)
                    argc = len(self.varnames) - 1
                    for i in range(args):
                        name = self.varnames[argc - i]
                        self.vmGlobals[name] = data[-i]
            except (TypeError, KeyError, IndexError):
                pass

        if self.isFunction == 2:
            class vmSelf:
                pass
            self.mainClass = vmSelf


        if self.mainClass is not None:
            self.vmGlobals['self'] = self.mainClass

        # main
        cx  = 0
        arg = 0
        previous_arg = [False, arg]
        EXTENDED_ARG = 0
        stk = []
        push = stk.append
        pop  = stk.pop
        argc = 0
        args = []
        kwargs = {}
        build_class = False
        raise_var = None
        range_for = []

        while (cx < len(self.code)):
            # print(cx)
            if (cx % 2 != 0):
                raise ValueError("op must is even ({})".format(cx))

            op  = self.code[cx]
            arg = self.code[cx + 1]
            if EXTENDED_ARG > 0:
                arg = arg + EXTENDED_ARG
                EXTENDED_ARG = 0

            if raise_var:
                if op == self.opcodes["PUSH_EXC_INFO"]:
                    pass
                elif op == self.opcodes["RERAISE"]:
                    pass
                else:
                    cx += 2
                    previous_arg[1] = arg
                    continue

            if op == self.opcodes["LOAD_GLOBAL"]:
                try:
                    if self.isFunction == 1:
                        if arg > 0:
                            name = self.names[arg - 1]
                        else:
                            name = self.names[arg]
                    else:
                        name = self.names[arg]
                except IndexError:
                    if self.isFunction == 1:
                        name = self.names[-1]
                    else:
                        self.logging.error("LOAD_GLOBAL: Cannot get args[{}]".format(arg))

                try:
                    name = self.vmGlobals[name]
                except KeyError:
                    try:
                        name = self.vmGlobals2[name]
                    except KeyError:
                        raise NameError("LOAD_GLOBAL: Cannot get '{}' in GLOBAL".format(self.names[arg]))
                push(name)
            elif op == self.opcodes["LOAD_CONST"]:
                const = self.consts[arg]
                push(const)
            elif op == self.opcodes["LOAD_NAME"]:
                name = self.names[arg]
                try:
                    name = self.vmGlobals[name]
                except KeyError:
                    try:
                        name = self.vmGlobals2[name]
                    except KeyError:
                        raise NameError("LOAD_NAME: Name '{}' is not defined".format(name))
                push(name)
            elif op == self.opcodes["BINARY_OP"]:
                b = pop()
                a = pop()
                c = False

                if arg == 0 or arg == 13:
                    c = (a + b)
                elif arg == 1 or arg == 14:
                    c = (a & b)
                elif arg == 2 or arg == 15:
                    c = (a // b)
                elif arg == 3 or arg == 16:
                    c = (a << b)
                elif arg == 4 or arg == 17:
                    c = (a @ b)
                elif arg == 5 or arg == 18:
                    c = (a * b)
                elif arg == 6 or arg == 19:
                    c = (a % b)
                elif arg == 7 or arg == 20:
                    c = (a | b)
                elif arg == 8 or arg == 21:
                    c = (a ** b)
                elif arg == 9 or arg == 22:
                    c = (a >> b)
                elif arg == 10 or arg == 23:
                    c = (a - b)
                elif arg == 11 or arg == 24:
                    c = (a / b)
                elif arg == 12 or arg == 25:
                    c = (a ^ b)
                else:
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
                if self.isFunction == 2:
                    try:
                        if (str(type(v)) == "<class 'tuple'>" and len(v) == 7 and str(type(v[0])) == "<class 'bytes'>"):
                            v = VM(v)
                            v.mainClass = vmSelf
                    except Exception as e:
                        self.logging.error("STORE_NAME: {}".format(str(e)))
                    setattr(self.consts[-1]['classObj'], name, v)
                    setattr(vmSelf, name, v)

            elif op == self.opcodes["STORE_FAST"]:
                v = pop()
                name = self.varnames[arg]
                self.vmGlobals[name] = v

            elif op == self.opcodes["DELETE_FAST"]:
                name = self.varnames[arg]

                try:
                    del self.vmGlobals[name]
                except KeyError:
                    pass
            elif op == self.opcodes["LOAD_FAST"]:
                name = self.varnames[arg]
                
                try:
                    name = self.vmGlobals[name]
                except KeyError:
                    raise NameError("LOAD_FAST: Name '{}' is not defined".format(name))
                push(name)
            elif op == self.opcodes["RETURN_VALUE"]:
                data = pop()

                if self.isFunction == 1:
                    return data
                elif self.isFunction == 2:
                    try:
                        self.mainClass = None
                        return self.consts[-1]['classObj']
                    except (IndexError, KeyError):
                        pass
                return data
                # push(data)
            elif op == self.opcodes["BUILD_LIST"]:
                lst = []
                for i in range(0, arg):
                    lst.append(pop())
                push(lst)
            elif op == self.opcodes["RESUME"]:
                pass
                # cx = arg
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

                if arg == 0:
                    c = (a < b)
                elif arg == 1:
                    c = (a <= b)
                elif arg == 2:
                    c = (a == b)
                elif arg == 3:
                    c = (a != b)
                elif arg == 4:
                    c = (a > b)
                elif arg == 5:
                    c = (a >= b)
                else:
                    self.logging.error("COMPARE_OP: Unsupported ({arg})".format(arg = arg))
                    
                push(c)
            elif op == self.opcodes["PRECALL"]:
                # print(stk)
                # if arg == 0 and previous_arg[0]:
                #     pop()
                #     arg = previous_arg[1]
                #     previous_arg[0] = False

                if build_class:
                    arg = arg - 1

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
                        
                function = pop()
                # print(stk, function, args)
            elif op == self.opcodes["CALL"]:
                if "<function <listcomp> at " in str(function):
                    data = []
                    for i in args:
                        data.append(i)
                    args = [tuple(data)]

                if build_class:
                    args = []

                type_func = str(type(function))

                # if type_func == "<class 'method'>":
                #     args.insert(0, pop())
                
                if not (str(type(function)) == "<class 'tuple'>" and len(function) == 7 and str(type(function[0])) == "<class 'bytes'>"):
                    try:
                        data = function(*args, **kwargs)
                        if stk:
                            if stk[-1] == None:
                                pop()
                        push(data)
                    except (Exception, KeyboardInterrupt) as ex:
                        raise_var = ex
                else:
                    try:
                        VMobj = makeVM(function)
                        VMobj = VM(VMobj.obj)
                    except TypeError:
                        VMobj = VM(function)

                    # VMobj.vmGlobals2 = self.vmGlobals
                    VMobj.vmGlobals2.update(self.vmGlobals2)
                    VMobj.vmGlobals2.update(self.vmGlobals)
                    if build_class:
                        VMobj.isFunction = 2
                    data = VMobj(*args, **kwargs)
                    if stk:
                        if stk[-1] == None:
                            pop()

                    push(data)
                    
                function = None
                args = []
                kwargs = {}
                if build_class:
                    build_class = False
            elif op == self.opcodes["POP_JUMP_FORWARD_IF_TRUE"]:
                b = pop()

                if b:
                    cx = get_jump_to("POP_JUMP_FORWARD_IF_TRUE", cx)
            elif op == self.opcodes["POP_JUMP_FORWARD_IF_FALSE"]:
                b = pop()

                if not b:
                    cx = get_jump_to("POP_JUMP_FORWARD_IF_FALSE", cx)
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
                    try:
                        self.code[cx + 2]
                        raise_var = pop()
                    except IndexError:
                        arg = -1

                if arg == -1:
                    raise pop()
            elif op == self.opcodes["NOP"]:
                pass
            elif op == self.opcodes["JUMP_FORWARD"]:
                cx = get_jump_to("JUMP_FORWARD", cx)
            elif op == self.opcodes["JUMP_BACKWARD"]:
                cx = get_jump_to("JUMP_BACKWARD", cx)
            elif op == self.opcodes["PUSH_EXC_INFO"]:
                push(raise_var)
                raise_var = None
            elif op == self.opcodes["POP_EXCEPT"]:
                pass
            elif op == self.opcodes["CHECK_EXC_MATCH"]:
                b = pop()
                a = pop()
                push(a)
                if type(a) != type(type):
                    a = type(a)

                if type(b) != type(()):
                    b = tuple([b])

                push(a in b)
            elif op == self.opcodes["RERAISE"]: # uncompleted
                if arg == 1:
                    raise pop()
                elif arg == 0:
                    if raise_var:
                        push(raise_var)
                        raise_var = None
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
                range_ = 0
                if (t == "<class 'range'>"):
                    for i in range(data[-1], data[0] - 1, -1):
                        range_ = range_ + 1
                        push(i)
                elif (t == "<class 'tuple'>") or (t == "<class 'list'>"):
                    for i in data[::-1]:
                        range_ = range_ + 1
                        push(i)
                elif (t == "<class 'str'>"):
                    for i in data[::-1]:
                        range_ = range_ + 1
                        push(i)
                elif (t == "<class 'dict'>"):
                    pass
                arg = arg + range_
                previous_arg[0] = True
                range_for.append([0, range_])
            elif op == self.opcodes["FOR_ITER"]:
                if stk == [] or range_for[-1][0] >= range_for[-1][1]:
                    try:
                        del range_for[-1]
                    except IndexError:
                        pass
                    cx = get_jump_to("FOR_ITER", cx)
                else:
                    range_for[-1][0] += 1
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
                key = pop()
                data = pop()
                try:
                    if (type(key) == type(())):
                        if (len(key) == 2):
                            data = data[key[0]:key[1]]
                        elif (len(key) == 3):
                            data = data[key[0]:key[1]:key[2]]
                        else:
                            self.logging.error("BINARY_SUBSCR: Unsupported key ({} > 3)".format(arg))
                    else:
                        data = data[key]
                    push(data)
                except IndexError as ex:
                    raise_var = ex
                
            elif op == self.opcodes["IMPORT_NAME"]:
                name = self.names[arg]
                push(__import__(name))
            elif op == self.opcodes["IMPORT_FROM"]:
                name = self.names[arg]
                data = pop()
                item = pop()
                for i in range(len(item)):
                    if item[i] == name:
                        try:
                            v = getattr(data, item[i])
                        except AttributeError:
                            try:
                                data = __import__("{}.{}".format(data.__name__, item[i]))
                            except ModuleNotFoundError:
                                raise ImportError("cannot import name '{}' from '{}'".format(item[i], data.__name__))
                            v = getattr(data, item[i])
                        item = list(item)
                        item.remove(name)
                        item = tuple(item)
                        if len(item) > 0:
                            push(item)
                            push(data)
                        push(v)
                        break                
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
                item = getattr(data, name)
                # if str(type(item)) == "<class 'method'>":
                #     push(data)
                push(item)
            elif op == self.opcodes["POP_JUMP_FORWARD_IF_NONE"]:
                b = pop()
                b = b is None

                if b:
                    cx = get_jump_to("POP_JUMP_FORWARD_IF_NONE", cx)
            elif op == self.opcodes["POP_JUMP_FORWARD_IF_NOT_NONE"]:
                b = pop()
                b = b is None

                if not b:
                    cx = get_jump_to("POP_JUMP_FORWARD_IF_NOT_NONE", cx)
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
                    value = value + str(i)
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
            elif op == self.opcodes["MAKE_FUNCTION"]:
                function = pop()

                try:
                    if str(type(function)) == "<class 'code'>":
                        raise TypeError()
                    elif str(type(function)) == "<class 'dict'>":
                        if type(function['vmObj']) == type(tuple()):
                            function = function['vmObj']
                            function = list(function)

                            if arg == 0:
                                pass
                            if arg == 1:
                                arg = pop()
                                function[1] = function[1] + ({'default': list(arg[::-1])},)
                            else:
                                pass

                            if build_class:
                                function[1] = function[1] + ({'classObj': pop()},)

                            func = tuple(function)
                        else:
                            raise TypeError
                    else:
                        raise TypeError()
                except TypeError:
                    if arg == 0:
                        pass
                    if arg == 1:
                        arg = pop()
                        function = function.replace(co_consts=function.co_consts + ({'default': list(arg[::-1])},))
                    else:
                        pass

                    if build_class:
                        function = function.replace(co_consts=function.co_consts + ({'classObj': pop()},))

                    try:
                        func = self.types.FunctionType(function, globals())
                    except TypeError:
                        closure = pop()
                        if type(closure) == type(()):
                            closure = closure + (pop(),)
                        else:
                            raise TypeError("cannot create function!")
                        func = self.types.FunctionType(function, globals(), closure=())
                push(func)
            elif op == self.opcodes["UNPACK_SEQUENCE"]:
                data = pop()
                item = -1
                for i in range(arg):
                    push(data[item])
                    item = item - 1
            elif op == self.opcodes["MAKE_CELL"]:
                try:
                    if cx == 0:
                        data = None
                    else:
                        data = stk[-1]
                except IndexError:
                    data = None

                try:
                    name = self.varnames[arg]
                except IndexError:
                    name = 'x'

                self.vmGlobals[name] = data
            elif op == self.opcodes["BUILD_TUPLE"]:
                data = tuple()
                for i in range(arg):
                    data = data + (pop(),)
                data = data[::-1]
                push(data)
            elif op == self.opcodes["STORE_DEREF"]:
                v = pop()
                try:
                    name = self.varnames[arg]
                except IndexError:
                    name = 'x'

                self.vmGlobals[name] = v
            elif op == self.opcodes["LOAD_CLOSURE"]:    # uncompleted
                try:
                    name = self.varnames[arg]
                except IndexError:
                    name = 'x'

                data = self.vmGlobals[name]
                push(data)
            elif op == self.opcodes["SWAP"]:
                data = []
                for i in range(arg):
                    data.append(pop())
                for i in data:
                    push(i)
            elif op == self.opcodes["STORE_SUBSCR"]:
                key = pop()
                data = pop()
                value = pop()

                if (type(key) == type(())):
                    if (len(key) == 2):
                        data[key[0]:key[1]] = value
                    elif (len(key) == 3):
                        data[key[0]:key[1]:key[2]] = value
                    else:
                        self.logging.error("STORE_SUBSCR: Unsupported key ({} > 3)".format(arg))
                else:
                    data[key] = value
            elif op == self.opcodes["LOAD_BUILD_CLASS"]:
                class data:
                    pass
                push(data)
                build_class = True
            elif op == self.opcodes["STORE_GLOBAL"]:
                data = pop()
                name = self.names[arg]
                self.vmGlobals[name] = v
            elif op == self.opcodes["DELETE_GLOBAL"]:
                name = self.varnames[arg]

                try:
                    del self.vmGlobals[name]
                except KeyError:
                    pass
            elif op == self.opcodes["POP_JUMP_BACKWARD_IF_NOT_NONE"]:
                b = pop()
                b = b is None

                if not b:
                    cx = get_jump_to("POP_JUMP_BACKWARD_IF_NOT_NONE", cx)
            elif op == self.opcodes["POP_JUMP_BACKWARD_IF_NONE"]:
                b = pop()
                b = b is None

                if b:
                    cx = get_jump_to("POP_JUMP_BACKWARD_IF_NONE", cx)
            elif op == self.opcodes["POP_JUMP_BACKWARD_IF_FALSE"]: # uncompleted
                b = pop()

                if not b:
                    cx = get_jump_to("POP_JUMP_BACKWARD_IF_FALSE", cx)
            elif op == self.opcodes["POP_JUMP_BACKWARD_IF_TRUE"]:
                b = pop()

                if b:
                    cx = get_jump_to("POP_JUMP_BACKWARD_IF_TRUE", cx)
            elif op == self.opcodes["EXTENDED_ARG"]:
                EXTENDED_ARG = arg
            elif op == self.opcodes["BUILD_SLICE"]:
                step, stop, start = None, None, None
                if arg == 2:
                    stop = pop()
                    start = pop()
                elif arg == 3:
                    step = pop()
                    stop = pop()
                    start = pop()
                else:
                    self.logging.error("BUILD_SLICE: Unsupported arg = {}".format(arg))
                
                push((start, stop, step))
                # data = data[start:stop:step]
                # push({'value': data})
                # push('value')
            elif op == self.opcodes["LIST_APPEND_A"]:
                value = pop()
                lst = pop()
                lst.append(value)
                push(lst)
            elif op == self.opcodes["LIST_TO_TUPLE"]:
                lst = pop()
                push(tuple(lst))
            elif op == self.opcodes["CONTAINS_OP"]:
                a = pop()
                b = pop()
                push(b in a)
            elif op == self.opcodes["DELETE_NAME"]:
                name = self.names[arg]

                try:
                    del self.vmGlobals[name]
                except KeyError:
                    pass
            else:
                name_opcode = None
                for key, value in self.opcodes.items():
                    if value == op:
                        name_opcode = key + " (" + str(op) + ")"
                        break
                if not name_opcode:
                    name_opcode = str(op)
                
                self.logging.error("Unsupported opcode: " + name_opcode + " at op=" + str(cx))

            cx += 2
            previous_arg[1] = arg

        return 0

"""
NOT WORKING: 
1. <listcomp>
2. closure on function
3. class object, bug store_name 'self'
"""