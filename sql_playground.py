import sqlite3

def main():
    conn = sqlite3.connect('tweet.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tweets ORDER BY likes DESC")
    results = cursor.fetchall()
    print("results are:")
    print(results)
    for x in results:
        print("TWEET: %s LIKES: %d" % (x[0], x[2]))

main()

