import sqlite3
import secrets
import hashlib

def create_user(info):
    # 1) prompt user for info
    username = info[0]
    password = info[1]
    print("user: %s, password: %s" % (username, password))
    # 2) generate salt
    salt = secrets.token_hex(6)
    print("salt = %s" % salt)
    # 3) put together salt and password
    salted_password = password + salt
    # need to turn the string into bytes for hashlib, function produces binary (hex.digest coverts it into hex)
    hashed_password = hashlib.md5(salted_password.encode('ascii')).hexdigest()
    print("hashed password: %s" % hashed_password)
    # INSERT BOTTOM TAG OUT HERE

    # connect to data base
    conn = sqlite3.connect('tweet.db')
    cursor = conn.cursor()
    # get the salt from the row that contains the username
    cursor.execute("SELECT salt FROM users WHERE username=?", (username,))
    query_result = cursor.fetchone()
    # if there is no row with a username that matches the input, that means username isn't taken
    if query_result is None:
        cursor.execute("INSERT INTO users (username, password, salt) VALUES (?, ?, ?)",
                     (username, hashed_password, salt))
        conn.commit()
        cursor.close()
        conn.close()
        print("successfully created a new user")
        return True
    # if there is a row with that username, that means it is taken
    else:
        print("username taken: ", username)
        return False

    # conn = sqlite3.connect("tweet.db")
    # conn.execute("INSERT INTO users (username, password, salt) VALUES (?, ?, ?)",
    #              (username, hashed_password, salt))
    # cursor = conn.cursor()
    # conn. commit()
    # cursor.close()
    # conn.close()
