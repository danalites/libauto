
import os
import csv
import shutil
import sqlite3
from tempfile import NamedTemporaryFile

from libauto.utils.user import getUserHome
from libauto.core.runtime import registerOp
from libauto.utils.logger import LogError, LogWarning

appPath = getUserHome()

def readFromDb(db, table, key):
    conn = sqlite3.connect(db)
    # conn.row_factory = lambda cursor, row: row[0]

    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    tables = cur.execute(
        f"""SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'; """).fetchall()
    if len(tables) == 0:
        LogWarning(f"SQLite: table \"{table}\" does not exists.")
        return str()

    cur.execute(f"SELECT * FROM {table} WHERE key = ?", (key,))
    rows = cur.fetchall()

    if len(rows) == 0:
        LogWarning(f"SQLite: key \"{key}\" does not exits.")
        return str()

    return dict(rows[0])


def writeToDb(db, table, key, val=None, kwargs=dict()):
    # create database and table if not exists
    conn = sqlite3.connect(db)
    # conn.row_factory = lambda cursor, row: row[0]
    cur = conn.cursor()

    # request to write database at key
    if val:
        kwargs["value"] = val

    try:
        tables = cur.execute(
            f"""SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'; """).fetchall()

        # create table when it does not exist
        if len(tables) == 0:
            LogWarning(f"SQLite: table \"{table}\" not exists. creating table")
            keys = kwargs.keys()
            keyTypes = ", ".join(_ + " TEXT" for _ in keys)
            sql = f"CREATE TABLE {table} (key TEXT PRIMARY KEY, {keyTypes})"
            LogWarning(sql)
            cur.execute(sql)

    except Exception as err:
        LogError(err)

    values = kwargs.values()
    LogWarning(f"Updating {key} to \"{kwargs}\" in {table}")

    columns = ", ".join(kwargs.keys())
    placeholders = ', '.join('?' * len(kwargs))
    sql = f"INSERT OR IGNORE INTO {table} (key, {columns}) VALUES (?, {placeholders})"
    cur.execute(sql, (key, *values,))

    new_values = ", ".join([_ + " = ?" for _ in kwargs.keys()])
    sql = f"UPDATE {table} SET {new_values} WHERE key = ?"
    cur.execute(sql, (*values, key))
    conn.commit()

    cur.close()
    conn.close()


@registerOp
async def DB_INIT(ctx, target: str = "", config=dict(), ret: str = ""):
    if target.endswith(".csv"):
        headers = config["headers"]
        dirname = os.path.dirname(target)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        if not os.path.exists(target):
            with open(target, 'w') as csv_file:
                csv_writer = csv.writer(csv_file) 
                csv_writer.writerow(headers)
                
        ctx.cache[ret] = { "target": target, "headers": headers }
    
    elif target == "":
        LogWarning("DB_INIT: use default database")
        ctx.cache[ret] = { "target": "aba.db", "table": 'default' }

    await ctx.set_next_op()

    
@registerOp
async def STORE_GET(ctx, conn=dict(), params=dict(), default=0, ret: str = ""):
    if "target" not in conn:
        LogError(f"(STORE_GET) illegal target {conn}")

    # reading a row from csv file
    if conn["target"].endswith(".csv"):
        headers = conn["headers"]
        key = params["key"]

        with open(conn["target"], 'r', encoding='UTF8') as csv_file:
            csv_reader = csv.reader(csv_file)
            is_found = False
            for row in csv_reader:
                if row[0] == key:
                    is_found = True
                    ctx.cache[ret] = row
                    break
            if not is_found:
                LogWarning(f"STORE_GET: key \"{key}\" not found")
                ctx.cache[ret] = default
    
    elif conn["target"].endswith(".db"):
        location = os.path.join(appPath, db) + ".db"
        val = readFromDb(location, table, key)
        ctx.cache[ret] = val

    await ctx.set_next_op()


@registerOp
async def STORE_SET(ctx, conn=dict(), params=dict(),):
    if "target" not in conn:
        LogError(f"(STORE_GET) illegal target {conn}")

    if conn["target"].endswith(".csv"):
        is_empty = False
        headers = conn["headers"]
        key = params["key"]

        if (not os.path.exists(conn["target"])) or os.path.getsize(conn["target"]) == 0:
            is_empty = True

        tempfile = NamedTemporaryFile(mode='w', delete=False)

        with open(conn["target"], 'r', encoding='UTF8') as f, tempfile:
            writer = csv.writer(tempfile)
            reader = csv.reader(f)

            if is_empty:
                writer.writerow(headers)
            is_found = False
            for row in reader:
                if row[0] == key:
                    is_found = True
                    row = params["value"]
                writer.writerow(row)
            
            if not is_found:
                writer.writerow(params["value"])

        shutil.move(tempfile.name, conn["target"])

    elif conn["target"].endswith(".txt"):
        with open(conn["target"], 'a+', encoding='UTF8') as f:
            f.write(data)

    await ctx.set_next_op()
