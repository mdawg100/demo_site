# Webserver!

# you can have a dynamic website where the content is created in the definition, or you
# can use a static website where the content is an actual file

from aiohttp import web
import aiohttp_jinja2
import jinja2
import random
import sqlite3

@aiohttp_jinja2.template('bootstrap_test.html.jinja2')
async def home(request):
    conn = sqlite3.connect('tweet.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tweets ORDER BY likes DESC")
    results = cursor.fetchall()
    conn.close()
    return{"tweets": results, "name": "Influencer", "num_pics": 6}

@aiohttp_jinja2.template('pictures.html.jinja2')
async def pictures(request):
    conn = sqlite3.connect('tweet.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tweets ORDER BY likes DESC")
    results = cursor.fetchall()
    conn.close()
    return{"tweets": results, "mood": ["sad", "happy", "angry", "surprised", "chillin"], "num": random.randint(0,len("mood"))}

@aiohttp_jinja2.template('about_me.html.jinja2')
async def aboutme(request):
    conn = sqlite3.connect('tweet.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tweets ORDER BY likes DESC")
    results = cursor.fetchall()
    conn.close()
    return{"tweets": results, "places": ["Jalalabad", "Donetsk", "Vorkuta", "Ta'izz", "Bogota"]}

@aiohttp_jinja2.template('favorites.html.jinja2')
async def favorites(request):
    conn = sqlite3.connect('tweet.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tweets ORDER BY likes DESC")
    results = cursor.fetchall()
    conn.close()
    return{"tweets": results, "books": ["Fahrenheit 451", "To Kill a Mockingbird", "Catch 22", "Catcher in the Rye",
                     "For Whom the Bell Tolls"],
           "num": random.randint(0,len("mood"))}

@aiohttp_jinja2.template('tweets.html.jinja2')
async def tweets(request):
    conn = sqlite3.connect('tweet.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tweets ORDER BY likes DESC")
    results = cursor.fetchall()
    conn.close()
    return{"tweets": results}

async def add_tweet(request):
    data = await request.post()
    content = data['content']
    # INSERT INTO tweets(content, likes) VALUES ('new tweet!',0);
    query = "INSERT INTO tweets(content, likes) VALUES (\"%s\", 0)" % content
    print("QUERY: %s" % query)
    conn = sqlite3.connect('tweet.db')
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    print("The user tweeted: %s" % data['content'])
    raise web.HTTPFound('/tweets')

async def like(request):
    conn = sqlite3.connect('tweet.db')
    cursor = conn.cursor()
    id = str(request.query['id'])
    # get the current like count
    cursor.execute("SELECT likes FROM tweets WHERE id=%s" % id)
    like_count = cursor.fetchone()[0]
    # add one to like count and save it
    cursor.execute("UPDATE tweets SET likes=%d WHERE id=%s" % (like_count + 1, id))
    conn.commit()
    conn.close()
    raise web.HTTPFound('/tweets')

def main():

    app = web.Application()
    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader('templates'))
    app.add_routes([web.get('/bootstrap_test.html', home),
                    web.get('/about_me.html', aboutme),
                    web.get('/pictures.html', pictures),
                    web.get('/favorites.html', favorites),
                    web.get('/', home),
                    web.get('/tweets', tweets),
                    web.static('/static', 'static'),
                    web.post('/tweet', add_tweet),
                    web.get('/like', like)])
    print("webserver 1.0")
    # type in: host:port
    #web.run_app(app, host="0.0.0.0", port=80)
    web.run_app(app, host="127.0.0.1", port=3000)
    # WHAT IF I WERE TO TYPE IN SOMEONE ELSE'S IP ADDRESS FOR HOST ^^^


if __name__=="__main__":
    main()


