# Routes

## What are Routes?

The routes directory contains basic routes that are defined using the `@app.route()` decorator to specify the path to the route and the valid HTTP request methods. 

## How to Define a New Route?

1. To define a route either add a new file to the routes directory or add a onto to an existing file
    - WARNING: The route file name cannot start with `__`
2. Define a create_routes() function that takes app as a paramater
3. Define all the routes inside the create_routes() function. It should look something like this
```python
def create_routes(app):

    @app.route('/{}/route_1'.format(AUGUR_API_VERSION), methods=["GET"])
    def first_route():

        # code to get data
       
        return Response(response=data, status=200, mimetype="application/json")

    @app.route('/{}/route_2'.format(AUGUR_API_VERSION), methods=["GET", "POST"])
    def route_2():
        
        # code to get data

        return Response(response=data, status=200, mimetype="application/json")

    @app.route('/{}/route_3'.format(AUGUR_API_VERSION), methods=["GET"])
    def route_3():
        
        # code to get data

        return Response(response=data, status=200, mimetype="application/json")
```

#### Notes on Routes
1. The function name does not have to match the route path, although it is usually very similar
2. You can specify whatever methods you want in the methods list
3. If errors occur you should return a Response object with the correct status code


## How Routes are Added to Flask App

1. First Gunicorn creates the Flask app when it asks for the app from `server.py`
2. This casues the left most indented code in server.py to execute which calls create_app (code shown below) 
```python
server = Server()
server.create_app()
app = server.get_app()
```
3. Then `create_app()` calls the function `create_all_routes(app)` and passes the Flask app
4. Then `create_all_routes(app)`
    1. Gets a list of route files from the `augur/api/rotues` directory
    2. Loops through the list of route files and imports them all
    3. Loops through the list of route files and calls each files create_route(app) function and passes the Flask app
5. The `create_route(app)` function in each file then use the `app` to define all the routes using `@app.route()`
