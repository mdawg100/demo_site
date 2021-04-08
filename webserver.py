# Webserver!

# you can have a dynamic website where the content is created in the definition, or you
# can use a static website where the content is an actual file

from aiohttp import web
import aiohttp_jinja2
import jinja2
import sqlite3
import requests
import random
import secrets
import hashlib
import create_user as create_user_module


# @aiohttp_jinja2.template('bootstrap_test.html.jinja2')
async def home(request):
    conn = sqlite3.connect('tweet.db')
    cursor = conn.cursor()
    # does the user have the cookie at all? if not, send them back to login
    if "logged_in" not in request.cookies:
        raise web.HTTPFound('/login')
    cursor.execute("SELECT username FROM users WHERE cookie=?", (request.cookies["logged_in"],))
    result = cursor.fetchone()
    # if they have a cookie, but it isn't in the database
    if result is None:
        raise web.HTTPFound('/login')
    # if they ARE logged in
    print("Is the user is %s" % result[0])
    print("user is coming from %s" % request.remote)
    cursor.execute("SELECT * FROM tweets ORDER BY likes DESC")
    results = cursor.fetchall()
    context = {"results": results, "lucky_number": random.randint(0, 100), "name": "Influencer"}
    response = aiohttp_jinja2.render_template('bootstrap_test.html.jinja2', request, context)
    # response.set_cookie('logged_in', 'yes')
    return response


@aiohttp_jinja2.template('pictures.html.jinja2')
async def pictures(request):
    conn = sqlite3.connect('tweet.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tweets ORDER BY likes DESC")
    results = cursor.fetchall()
    conn.close()
    return {"tweets": results, "mood": ["sad", "happy", "angry", "surprised", "chillin"],
            "num": random.randint(0, len("mood"))}


@aiohttp_jinja2.template('about_me.html.jinja2')
async def aboutme(request):
    conn = sqlite3.connect('tweet.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tweets ORDER BY likes DESC")
    results = cursor.fetchall()
    conn.close()
    return {"tweets": results, "places": ["Jalalabad", "Donetsk", "Vorkuta", "Ta'izz", "Bogota"]}


@aiohttp_jinja2.template('favorites.html.jinja2')
async def favorites(request):
    conn = sqlite3.connect('tweet.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tweets ORDER BY likes DESC")
    results = cursor.fetchall()
    conn.close()
    return {"tweets": results, "books": ["Fahrenheit 451", "To Kill a Mockingbird", "Catch 22", "Catcher in the Rye",
                                         "For Whom the Bell Tolls"],
            "num": random.randint(0, len("mood"))}


@aiohttp_jinja2.template('tweets.html.jinja2')
async def tweets(request):
    conn = sqlite3.connect('tweet.db')
    cursor = conn.cursor()
    # does the user have the cookie at all? if not, send them back to login
    if "logged_in" not in request.cookies:
        raise web.HTTPFound('/login')
    cursor.execute("SELECT username FROM users WHERE cookie=?", (request.cookies["logged_in"],))
    result = cursor.fetchone()
    # if they have a cookie, but it isn't in the database
    if result is None:
        raise web.HTTPFound('/login')
    # END check for cookie
    cursor.execute("SELECT * FROM tweets ORDER BY likes DESC")
    results = cursor.fetchall()
    cursor.execute("SELECT * FROM comment ORDER BY likes DESC")
    comments = cursor.fetchall()
    conn.close()
    return {"tweets": results, "comments": comments}


async def add_tweet(request):
    print("logged in?")
    data = await request.post()
    print(data)
    ip = request.remote
    location = get_location(ip)
    content = data['content']
    # INSERT INTO tweets(content, likes) VALUES ('new tweet!',0);
    conn = sqlite3.connect('tweet.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tweets(content, likes, location) VALUES (?, 0, ?)", (content, location))
    conn.commit()
    print("The user tweeted: %s" % data['content'])
    raise web.HTTPFound('/tweets')


async def comment(request):
    data = await request.post()
    string = data['content']
    print("string is: %s" % string)
    new_data = string.split('&')
    id = new_data[0]
    print("id is: %s" % id)
    content = new_data[1]
    ip = request.remote
    location = get_location(ip)
    # INSERT INTO tweets(content, likes) VALUES ('new tweet!',0);
    conn = sqlite3.connect('tweet.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO comment(content, tweet_id, likes, location) VALUES (?, ?, 0, ?)",
                   (content, id, location))
    conn.commit()
    raise web.HTTPFound('/tweets')


async def like(request):
    conn = sqlite3.connect('tweet.db')
    cursor = conn.cursor()
    tweet_id = str(request.query['id'])
    # get the current like count
    # even if a single value being input, still needs to be in a list
    cursor.execute("SELECT likes FROM tweets WHERE id=?", (tweet_id,))
    like_count = cursor.fetchone()[0]
    # add one to like count and save it
    cursor.execute("UPDATE tweets SET likes=? WHERE id=?", (like_count + 1, tweet_id))
    conn.commit()
    conn.close()
    raise web.HTTPFound('/tweets')


def like_json(request):
    conn = sqlite3.connect('tweet.db')
    cursor = conn.cursor()
    tweet_id = str(request.query['id'])
    # get the current like count
    # even if a single value being input, still needs to be in a list
    cursor.execute("SELECT likes FROM tweets WHERE id=?", (tweet_id,))
    like_count = cursor.fetchone()[0]
    # add one to like count and save it
    cursor.execute("UPDATE tweets SET likes=? WHERE id=?", (like_count + 1, tweet_id))
    conn.commit()
    conn.close()
    return web.json_response(data={"like_count": like_count + 1})


@aiohttp_jinja2.template('show_login.html.jinja2')
async def show_login(request):
    return {}


# going to use post instead of get because post doesn't show in the URL

async def login(request):
    global logged_in_secret
    # getting the data from the post
    data = await request.post()
    print(data)
    username = data["username"]
    password = data["password"]

    # connect to data base
    conn = sqlite3.connect('tweet.db')
    cursor = conn.cursor()

    # get the salt from the row that contains the username
    cursor.execute("SELECT salt FROM users WHERE username=?", (username,))
    query_result = cursor.fetchone()

    # if there is no row with a username that matches the input, send them back to the login
    if query_result is None:
        print("invalid username: ", username)
        raise web.HTTPFound('/login')

    # hash the password they submitted with the salt you got from the database (always returns a list, hence the [0])
    salt = query_result[0]
    salted_password = password + salt
    hashed_password = hashlib.md5(salted_password.encode('ascii')).hexdigest()
    print("using hashed password: ", hashed_password)

    # Check to see if the username and password match. Returns the number of users that match this condition
    cursor.execute("SELECT COUNT(*) FROM users WHERE username=? AND password=?",
                   (username, hashed_password))
    # cursor executes a query, fetchone fetches the first row in the response

    # now we have a 1 (there is one user with that matching info) or a 0 (there are no users that match)
    query_result = cursor.fetchone()
    user_exists = query_result[0]
    print("user query: %d" % user_exists)

    # if there's no user that matches in the database, send them back to log in
    if user_exists == 0:
        print('failed login')
        raise web.HTTPFound('/login')

    # if they match, make a cookie and return it to them.
    response = web.Response(text="congrats!",
                            status=302,
                            headers={'Location': "/tweets"})
    # set cookie to a random string (in this case, 32 random values)
    logged_in_secret = secrets.token_hex(16)
    response.cookies['logged_in'] = logged_in_secret
    # store the cookie in our own database at their username so we can validate
    cursor.execute("UPDATE users SET cookie=? WHERE username=?",
                   (logged_in_secret, username))
    conn.commit()
    print("successful login with cookie: ", logged_in_secret)
    conn.close()
    return response

async def logout(request):
    global logged_in_secret
    # delete their cookie
    response = aiohttp_jinja2.render_template('show_login.html.jinja2', request, {})
    response.cookies['logged_in'] = ''
    logged_in_secret = "--invalid--"
    return response

async def test(request):
    # pretend we got this variable from a data base
    print("query received when test button pushed: ", request.query)
    # query comes bck as a multidictproxy (dictionary). LIke a dict inside an array
    info_from_jquery = str(request.query['id'])
    # use the passed info to get stuff from the data base
    database = {"tag": "test-worked"}
    response = database[info_from_jquery]
    return web.json_response(data={"database_data": response})

async def create_user(request):
    context = {"place_holder": 69}
    response = aiohttp_jinja2.render_template('create_user.html.jinja2', request, context)
    return response

async def call_user(request):
    data = await request.post()
    print(data)
    username = data["username"]
    password = data["password"]
    info = [username, password]
    success = create_user_module.create_user(info)
    if success:
        raise web.HTTPFound('/login')
    else:
        raise web.HTTPFound('/create_user')

def main():
    app = web.Application()
    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader('templates'))
    app.add_routes([web.get('/bootstrap_test.html', home),
                    web.get('/about_me.html', aboutme),
                    web.get('/pictures.html', pictures),
                    web.get('/favorites.html', favorites),
                    web.get('/', home),
                    web.get('/login', show_login),
                    web.post('/login', login),
                    web.get('/logout', logout),
                    web.get('/tweets', tweets),
                    web.static('/static', 'static'),
                    web.post('/tweet', add_tweet),
                    web.post('/comment', comment),
                    web.get('/test', test),
                    web.get('/create_user', create_user),
                    web.post('/create_user', call_user),
                    web.get('/like', like),
                    web.get('/like.json', like_json)])
    print("webserver 1.0")
    # type in: host:port
    # choose one of the below for either actual website or self-testing
    web.run_app(app, host="0.0.0.0", port=80)
    # web.run_app(app, host="127.0.0.1", port=3000)

    # in the SSH console to update all changes:
    # git pull
    # sudo systemctl restart webserver

    # tweet",10)-- to control the likes

    # TO CONNECT IN TERMINAL: sqlite3 tweet.db
    # sqlite3 tweet.db < schema.sql
    #sudo systemctl restart webserver

    # updating the database based on the schema
    # sqlite3 tweet.db < schema.sql

    # class is .
    # id is #


def get_location(ip_address):
    api_key = "ef864d79b484fc119c87882e7257cf8b"

    result = requests.get("http://api.ipstack.com/%s?access_key=%s" % (ip_address, api_key))
    data = result.json()
    return "%s, %s" % (data["city"], data["region_code"])


if __name__ == "__main__":
    main()
