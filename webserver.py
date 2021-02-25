# Webserver!

# you can have a dynamic website where the content is created in the definition, or you
# can use a static website where the content is an actual file

from aiohttp import web
import aiohttp_jinja2
import jinja2
import random

@aiohttp_jinja2.template('bootstrap_test.html.jinja2')
async def home(request):
    return{"name": "Influencer", "num_pics": 6}

@aiohttp_jinja2.template('pictures.html.jinja2')
async def pictures(request):
    return{"mood": ["sad", "happy", "angry", "surprised", "chillin"], "num": random.randint(0,len("mood"))}

@aiohttp_jinja2.template('about_me.html.jinja2')
async def aboutme(request):
    return{"places": ["Jalalabad", "Donetsk", "Vorkuta", "Ta'izz", "Bogota"]}

@aiohttp_jinja2.template('favorites.html.jinja2')
async def favorites(request):
    return{"books": ["Fahrenheit 451", "To Kill a Mockingbird", "Catch 22", "Catcher in the Rye",
                     "For Whom the Bell Tolls"],
           "num": random.randint(0,len("mood"))}

def main():

    app = web.Application()
    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader('templates'))
    app.add_routes([web.get('/bootstrap_test.html', home),
                    web.get('/about_me.html', aboutme),
                    web.get('/pictures.html', pictures),
                    web.get('/favorites.html', favorites),
                    web.static('/static', 'static')])
    print("webserver 1.0")
    # type in: host:port
    web.run_app(app, host="127.0.0.1", port=3000)
    # WHAT IF I WERE TO TYPE IN SOMEONE ELSE'S IP ADDRESS FOR HOST ^^^


if __name__=="__main__":
    main()


