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

logged_in_secret = "--invalid--"

# @aiohttp_jinja2.template('bootstrap_test.html.jinja2')
async def home(request):
    # does the user have the cookie at all?
    if "logged_in" not in request.cookies:
        raise web.HTTPFound('/login')
    # is the cookie correct
    if request.cookies['logged_in'] != logged_in_secret:
        # they aren't logged in
        raise web.HTTPFound('/login')
    # if they ARE logged in
    print("Is the user logged in? %s" % request.cookies['logged_in'])
    print("user is coming from %s" % request.remote)
    conn = sqlite3.connect('tweet.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tweets ORDER BY likes DESC")
    results = cursor.fetchall()
    context = {"results": results, "lucky_number": random.randint(0, 100), "name": "Influencer"}
    response = aiohttp_jinja2.render_template('bootstrap_test.html.jinja2', request, context)
    response.set_cookie('logged_in', 'yes')
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
    id = data['content'][0]
    ip = request.remote
    location = get_location(ip)
    content = data['content'][1:]
    # INSERT INTO tweets(content, likes) VALUES ('new tweet!',0);
    conn = sqlite3.connect('tweet.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO comment(content, tweet_id, likes, location) VALUES (?, ?, 0, ?)",
                   (content, id, location))
    conn.commit()
    print("The user commented: %s" % data['content'][1:])
    print("The tweet id is: %s" % data['content'][0])
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
    data = await request.post()
    print(data)
    username = data["username"]
    password = data["password"]
    # connect to data base and check username and password, check if authorized
    if(username=="Bill" and password=="1234"):
        # if they match, make a cookie
        response = web.Response(text="congrats!",
                                status=302,
                                headers={'Location': "/"})
        # set cookie to a random string (in this case, 32 random values)
        logged_in_secret = secrets.token_hex(16)
        response.cookies['logged_in'] = logged_in_secret
    else:
        # if they fail, send them back to home
        raise web.HTTPFound('/')
    return response

async def logout(request):
    global logged_in_secret
    # delete their cookie
    response = aiohttp_jinja2.render_template('show_login.html.jinja2', request, {})
    response.cookies['logged_in'] = ''
    logged_in_secret = "--invalid--"
    return response


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

    #sqlite3 tweet.db < schema.sql
    #sudo systemctl restart webserver


def get_location(ip_address):
    api_key = "ef864d79b484fc119c87882e7257cf8b"

    result = requests.get("http://api.ipstack.com/%s?access_key=%s" % (ip_address, api_key))
    data = result.json()
    return "%s, %s" % (data["city"], data["region_code"])


if __name__ == "__main__":
    main()
