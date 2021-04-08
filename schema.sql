CREATE TABLE IF NOT EXISTS "tweets" (
	"content"	TEXT NOT NULL,
	"timestamp"	INTEGER,
	"likes"	INTEGER,
	"location"	TEXT,
	"id"	INTEGER NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "comment" (
	"content"	TEXT NOT NULL,
	"tweet_id"	INTEGER,
	"likes"	NUMERIC,
	"location"	TEXT,
	"id"	INTEGER NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "users" (
    "username" TEXT NOT NULL UNIQUE,
    "password" TEXT,
    "cookie" TEXT,
    "salt" TEXT
);

