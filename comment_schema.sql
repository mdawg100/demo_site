CREATE TABLE "comment" (
	"content"	TEXT NOT NULL,
	"tweet_id"	INTEGER,
	"likes"	NUMERIC,
	"location"	TEXT,
	"id"	INTEGER NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
