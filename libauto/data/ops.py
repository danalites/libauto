import re
import requests
import pyperclip
from datetime import datetime

from libauto.utils.logger import LogError, LogWarning
from libauto.core.runtime import registerOp


@registerOp
async def DATA_READ(ctx, source, ret: str = ""):
    if source == "clipboard":
        # 1. Load data from clipboard
        items = pyperclip.paste().split("\n")
        items = list(filter(lambda v: v != "\t", items))
        vals = list()
        for item in items:
            if "\t" in item:
                vals.append(item.split("\t"))
            else:
                vals.append(item)

        ctx.cache[ret] = vals
        ctx.log_warning(f"DATA_READ from {items}: loaded \"{vals}\"")

    elif not isinstance(source, str):
        # 2. Load data from rendered input
        if "|" in ret:
            ret = ret.split("|")
            for i, v in enumerate(ret):
                ctx.cache[v] = source[i]
        else:
            ctx.cache[ret] = source

    else:
        # 3. Rendered input is a string
        ctx.cache[ret] = source

    await ctx.set_next_op()


@registerOp
async def DATA_UPDATE(ctx, target, key, val=0):
    if ctx.cache.get(target, None):
        ctx.cache[target][key] = val
    await ctx.set_next_op()

@registerOp
async def DATA_PARSE(ctx, source: str = "", config=dict(), ret: str = ""):
    if "regex" in config:
        regex = config["regex"]
        matches = re.findall(regex, source)
        if not matches:
            LogError(f"Not found {regex} in \"{source}\"")
        else:
            if len(matches) > 1:
                LogWarning(f"Multiple instances found \"{matches}\"")
            ctx.cache[ret] = matches[0]

    else:
        if "type" not in config:
            LogError("DATA_PARSE: type is required")

        dim = config["type"]
        lang = config.get("lang", "en_US")
        url = 'http://localhost:8868/parse'
        data = f'locale={lang}&text="{source}"&dims="["{dim}"]"'
        value = requests.post(url, data=data).text
        ctx.cache[ret] = value

    await ctx.set_next_op()
