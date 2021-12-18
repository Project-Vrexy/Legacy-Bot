import sqlite3
import sys
sys.path.append("..")

from cogs.utils.path import path



p = path()
try:
    con = sqlite3.connect(p + '/db/database.sqlite3')
except sqlite3.OperationalError:
    os.mkdir(p + "/db")
    con = sqlite3.connect(p + '/db/database.sqlite3')
cur = con.cursor()

with con:
    print("Please wait...")
    cur.execute(
        """
        CREATE TABLE "reminders" (
            "id"	INTEGER UNIQUE,
            "user_id"	INTEGER NOT NULL,
            "reminder"	TEXT NOT NULL,  
            "time"	TEXT NOT NULL,
            PRIMARY KEY("id" AUTOINCREMENT)
        );
        """
    )
    print("Created Reminders Table")

    cur.execute(
        """
        CREATE TABLE "snipes" (
            "channel_id"	INTEGER NOT NULL UNIQUE,
            "user_id"	INTEGER NOT NULL,
            "text"	TEXT NOT NULL,
            "time"	TEXT NOT NULL,
            PRIMARY KEY("channel_id")
        );
        """
    )
    print("Created Snipes Table")

    cur.execute(
        """
        CREATE TABLE "tags" (
            "id"	INTEGER UNIQUE,
            "guild_id"	INTEGER NOT NULL,
            "user_id"	INTEGER NOT NULL,
            "name"	NUMERIC NOT NULL,
            "text"	TEXT NOT NULL,
            "date"	TEXT NOT NULL,
            PRIMARY KEY("id" AUTOINCREMENT)
        );
        """
    )
    print("Created Tags Table")

    cur.execute(
        """
        CREATE TABLE "tempbans" (
            "guild"	INTEGER NOT NULL,
            "mod"	INTEGER NOT NULL,
            "user"	INTEGER NOT NULL,
            "time"	TEXT NOT NULL
        );
        """
    )

    print("Created Tempbans Table")

    cur.execute(
        """
        CREATE TABLE "suggestions" (
            "id"	INTEGER UNIQUE,
            "guild"	INTEGER,
            "user"	INTEGER,
            "suggestion"	TEXT,
            "time"	TEXT,
            PRIMARY KEY("id" AUTOINCREMENT)
        );
        """
    )
    print("Created Suggestions Table")

    cur.execute(
        """
        CREATE TABLE "config" (
            "id"	INTEGER NOT NULL UNIQUE,
            "delete_swear"	TEXT,
            "swears"	TEXT,
            "log_channel"	INTEGER,
            "wildcard"	TEXT,
            "suggestions"	INTEGER,
            "prefix"	TEXT,
            "prefix_warn"	TEXT,
            "disabled_commands"	TEXT,
            PRIMARY KEY("id")
        );
        """
    )
    print("Created Config table")
    print("Done!")
