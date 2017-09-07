import inspect

# Type checking flags
NONE_SAFE = 1
NOT_SUBCLASS = 2


class InvalidTypeCheckException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


def i_t_e(c, v1, v2):
    if c:
        return v1
    else:
        return v2


def typed(f):
    def do_typecheck(v, t, v_name, flags=(False, False)):
        if type(t) is type:
            if flags[1]:
                if not (type(v) is t or (v is None and not flags[0])):
                    raise TypeError("Expected %s to be of type %s, but type %s received" %
                                    (v_name, t, type(v)), type(v), t)
            else:
                if not (issubclass(type(v), t) or (v is None and not flags[0])):
                    raise TypeError("Expected %s to be of type %s, but type %s received" %
                                    (v_name, t, type(v)), type(v), t)
        elif type(t) is tuple:
            if not len(v) == len(t):
                raise TypeError("Expected %s to be of a tuple of size %s, but size %s received" %
                                (v_name, len(t), len(v)), None, None)
            else:
                for i, val in enumerate(v):
                    do_typecheck(val, t[i], v_name)

        elif type(t) is dict:
            anno_flags = list(t.values())[0]
            nflags = list(flags)
            if type(anno_flags) is not list:
                raise InvalidTypeCheckException("Invalid type for flags list: %s" % type(anno_flags))
            for flag in anno_flags:
                if flag == NONE_SAFE:
                    nflags[0] = True
                elif flag == NOT_SUBCLASS:
                    nflags[1] = True
                else:
                    raise InvalidTypeCheckException("Invalid type checking flag")
            do_typecheck(v, list(t.keys())[0], v_name, flags=tuple(nflags))

        elif type(t) is set:
            if not type(v) in t:
                raise TypeError("Expected %s to be of types %s, but type %s received" %
                                (v_name, list(t), type(v)), type(v), t)
        elif type(t) is list:
            if len(t) != 2:
                raise InvalidTypeCheckException("Invalid structure typecheck %s, only 2 elements are allowed" % t)
            if type(v) == dict:
                iterable_val = v.values()
            elif type(v) == set or type(v) == list or type(v) == tuple:
                iterable_val = list(v)
            else:
                raise InvalidTypeCheckException("Invalid data structure for typechecking: %s" % type(v))

            for i in iterable_val:
                do_typecheck(i, t[1], v_name)

            if flags[1]:
                    if not(type(v) is t[0] or (v is None and not flags[0])):
                        raise TypeError("Expected data structure %s to be of type %s, but type %s received" %
                                    (v_name, t[0], type(v)), type(v), t[0])
            else:
                if not (issubclass(type(v), t[0])or (v is None and not flags[0])):
                    raise TypeError("Expected data structure %s to be of type %s, but type %s received" %
                                    (v_name, t[0], type(v)), type(v), t[0])
        else:
            raise InvalidTypeCheckException("Invalid type: %s" % t)

    annos = f.__annotations__

    def wrapper(*args, **kargs):
        args_dict = dict(zip(inspect.getfullargspec(f)[0], args))
        for k, v in args_dict.items():
            if k in annos.keys():
                do_typecheck(v, annos[k], k)
        for k2, v2 in kargs.items():
            if k2 in annos.keys():
                do_typecheck(v2, annos[k2], k2)

        f_ret = f(*args, **kargs)

        if "return" in annos.keys():
            do_typecheck(f_ret, annos["return"], "return")
        return f_ret

    return wrapper


def none_safe(f):
    def wrapper(*args, **kwargs):
        for arg in args:
            if arg is None:
                raise TypeError("None received in %s not accepted" % f.__name__)
        for karg in kwargs.values():
            if karg is None:
                raise TypeError("None received in %s not accepted" % f.__name__)
        return f(*args, **kwargs)

    return wrapper
