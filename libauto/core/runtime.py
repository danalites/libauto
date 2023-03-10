import re
import os
import inspect

import asyncio
import functools

import time
import pygb
import pyperclip
# rom PIL import ImageGrab
import datetime

from contextlib import contextmanager
from libauto.utils.logger import LogError, LogInfo, LogWarning


def getEnv(key):
    if key == "NOW":
        return datetime.datetime.now().timestamp()
    elif key == "YEAR":
        return datetime.datetime.now().year
    elif key == "MONTH":
        return datetime.datetime.now().month
    elif key == "DAY":
        return datetime.datetime.now().day
    elif key == "HOUR":
        return datetime.datetime.now().hour
    elif key == "MOUSE":
        point = pygb.position()
        return [point[0], point[1]]

    elif key == "HOME":
        return os.path.expanduser('~')

    elif key == "CLIPBOARD":
        value = pyperclip.paste()
        if isinstance(value, str):
            return value.split("\n")
        else:
            # return ImageGrab.grabclipboard() 
            return None

    raise LogError(f"(getEnv) invalid $env key: {key}")


def format(val):
    if isinstance(val, str):
        return f"\"{val}\""
    return str(val)


def evalCleanupStr(expr):
    # escaping # as \# in YAML
    expr = expr.replace("\\#", "#")
    return expr.strip().strip("\"")

# get all key of interests in the nested dict
# https://stackoverflow.com/a/50444005


def gen_dict_extract(var, key):
    if isinstance(var, dict):
        for k, v in var.items():
            if k == key:
                yield v
            if isinstance(v, (dict, list)):
                yield from gen_dict_extract(v, key)
    elif isinstance(var, list):
        for d in var:
            yield from gen_dict_extract(d, key)


def getDictVal(d, keys):
    level = 0
    v = None

    for k in keys:
        level += 1
        if level == 1:
            if isinstance(d, list):
                v = d[int(k)]
            else:
                try:
                    v = d[k]
                except KeyError:
                    matches = [item for item in gen_dict_extract(d, k)]
                    if len(matches) == 0:
                        LogError(f"getDictVal: key {k} not found in {d}")
                    else:
                        LogWarning(f"getDictVal: approximate search {matches}")
                        v = matches
                except TypeError:
                    v = d[int(k)]
        else:
            if isinstance(v, list):
                v = v[int(k)]
            else:
                try:
                    v = v[k]
                except KeyError:
                    matches = [item for item in gen_dict_extract(v, k)]
                    if len(matches) == 0:
                        LogError(f"getDictVal: key {k} not found in {v}")
                    else:
                        LogWarning(f"getDictVal: approximate search {matches}")
                        v = matches
                except TypeError:
                    v = d[int(k)]
    return v


def evalExpr(expr, ctx) -> str:
    if not expr:
        return expr

    if isinstance(expr, type):
        return str()

    # 1. Eval objects $elem, $inputs[key]
    res = re.match("^\$(\w+)(\[\w+\])*$", expr)
    if res:
        entry, key = res.group(1), res.group(2)
        if entry in ("inputs", "env"):
            if not key:
                raise RuntimeError(f"invalid ${entry}: {expr}")
            if entry == "inputs":
                return ctx.inputs[key.strip("[]")]
            elif entry == "env":
                return getEnv(key.strip("[]"))
        else:
            ret = ctx.cache[entry]
            if key:
                return ret[key.strip("[]")]
            return ret

    # 2. Eval objects {{ [1,2] }}
    res = re.match("^\{\{(.*?)\}\}$", expr)
    single_curly_bracket = True
    if len(re.findall("\{\{(.*?)\}\}", expr)) > 1:
        single_curly_bracket = False

    if res and single_curly_bracket:
        content = res.group(1)
        # Match nested brackets: $resp[0][buttonState]
        match = re.findall("\$(\w+)(\[[a-zA-Z0-9\]_\[]+\])*", content)
        for m in match:
            entry, key = m
            keys = list()
            if key:
                keys = re.findall("\[(.*?)\]", key)
            if entry in ("inputs", "env"):
                if not key:
                    raise RuntimeError(
                        f"(evalExpr) invalid ${entry}: {content}")
                if entry == "inputs":
                    val = format(getDictVal(ctx.inputs, keys))
                    content = content.replace(f"${entry}{key}", val)

                elif entry == "env":
                    if len(keys) != 1:
                        raise RuntimeError(
                            f"(evalExpr) invalid ${entry}: {content}")
                    content = content.replace(f"${entry}{key}",
                                              format(getEnv(keys[0])))
            else:
                ret = ctx.cache[entry]
                if keys:
                    val = format(getDictVal(ret, keys))
                    content = content.replace(f"${entry}{key}", val)
                else:
                    # Check if ${entry} can be evaluated
                    # Input might be list of web elements
                    try:
                        v = eval(format(ret))
                    except Exception as e:
                        LogWarning(f"(evalExpr) cannot eval ${entry}: {e}")
                        LogWarning(format(ret))
                        v = 0
                        if isinstance(ret, list):
                            if len(ret) > 0:
                                v = 1
                        LogWarning(
                            f"(evalExpr) render ${entry}: [{ret[0]}, ...] to {v}")
                        ret = v
                    content = content.replace(f"${entry}", format(ret))
        return eval(content)

    # 3. Eval strings, e.g., http://{{$inputs[index] + 1}}
    match = re.findall("\{\{(.*?)\}\}", expr)
    for m in match:
        new_m = m
        sub_match = re.findall("\$(\w+)(\[[a-zA-Z0-9\]_\[]+\])*", m)

        for n in sub_match:
            entry, key = n
            keys = list()
            if key:
                keys = re.findall("\[(.*?)\]", key)
            if entry in ("inputs", "env"):
                if not key:
                    raise RuntimeError(f"invalid $inputs|env key: {new_m}")
                if entry == "inputs":
                    val = format(getDictVal(ctx.inputs, keys))
                    new_m = new_m.replace(f"${entry}{key}", val)

                elif entry == "env":
                    if len(keys) != 1:
                        raise RuntimeError(
                            f"(evalExpr) invalid ${entry}: {content}")
                    new_m = new_m.replace(f"${entry}{key}",
                                          format(getEnv(keys[0])))
            else:
                ret = ctx.cache[entry]
                if key:
                    key = key.strip("[]")
                    if key.isdigit():
                        key = int(key)
                    new_m = new_m.replace(f"${entry}[{key}]",
                                          format(ret[key]))
                else:
                    new_m = new_m.replace(f"${entry}",
                                          format(ret))
        # NB: to handle cases like http://...//{{$inputs[index] + 1}}
        new_m = str(eval(new_m))
        expr = expr.replace("{{" + m + "}}", new_m)
    return evalCleanupStr(expr)


def printOpArgs(fname, argnames, *args, **kwargs):
    # print arg information when function is called
    print("(OpArgs) ", fname, "(", end="")
    print(', '.join('% s = % r' % entry
                    for entry in zip(argnames, args[:len(argnames)])), end=", ")
    # variable length and keyword arguments
    print("args =", list(args[len(argnames):]), end=", ")
    print("kwargs =", kwargs, end="")
    print(")")


def registerOp(func):
    fname = func.__name__
    sig = inspect.signature(func)
    argnames = list(sig.parameters.keys())

    # Get params and its kind
    args = dict()
    for v_name, v in sig.parameters.items():
        if str(v.kind) == "VAR_POSITIONAL":
            args[v_name] = list()

        elif str(v.kind) == "VAR_KEYWORD":
            args[v_name] = dict()

        elif str(v.kind) == "POSITIONAL_OR_KEYWORD":
            args[v_name] = ''
            if v.default != inspect._empty:
                args[v_name] = v.default
        else:
            raise RuntimeError(f"(error) illegal {v}: {v.kind}")

    @ contextmanager
    def wrapping_logic():
        start_ts = time.time()
        yield
        dur = time.time() - start_ts
        fname = func.__name__.lower().replace("_", ".")
        LogInfo('{} exec time {:.2} (s)\n'.format(fname, dur))

    # https://stackoverflow.com/a/44176794
    @ functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not asyncio.iscoroutinefunction(func):
            with wrapping_logic():
                printOpArgs(fname, argnames, *args, **kwargs)
                return func(*args, **kwargs)
        else:
            async def tmp():
                with wrapping_logic():
                    printOpArgs(fname, argnames, *args, **kwargs)
                    return (await func(*args, **kwargs))
            return tmp()

    wrapper.argnames = argnames
    wrapper.defaults = args
    return wrapper
