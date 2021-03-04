CREATE TABLE "tweets" (
	"content"	TEXT NOT NULL,
	"timestamp"	INTEGER,
	"likes"	INTEGER,
	"location"	TEXT,
	"id"	INTEGER NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);