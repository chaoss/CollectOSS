# API

## General API Information

1. It is served via Flask and Gunicorn 


## API Developer Details

### Starting API

The api is started using a subprocess.Popen() on this command gunicorn -c `<gunicorn_location>` -b `<bind>` --preload augur.api.server:app. This loads the gunicorn configuration from the location specified in the variable `<guicorn_location>`, and binds the gunicorn process to the ip and port specified in the `<bind>` variable. The gunicorn_location is a path to the `gunicorn_config.py` file in the `augur/api` directory. Then is tries to find the app variable in augur.api.server so it can use this as the Flask app. This cases these three lines of code to execute at the bottom of server.py: 
```python
server = Server()
server.create_app()
app = server.get_app()
```
So then Gunicorn uses this app to load the server. Note: Those three lines above are executed first because we are using preloading. This means that the Flask app is created first and then gunicorn gets it and copies it to all the workers.  

### Config

The config located in `augur/api/gunicorn_conf.py` loads a default configuration and then if the config table in the augur_operation schema contains gunicorn config values they override the defaults. 

### Routes

The routes are located in the augur/api/routes directory. These are added to the Flask app in the create_app() method in the Server class. This is done by calling create_all_routes() and passing the Flask app to it. create_all_routes() then gets a list of all of route files in the routes folder, and imports them. Then it calls the create_routes() function which must be defines in all the route files, and passes the flask app so the routes can be added to the app. For more information on routes please see the README in the rotues directory. 

### Metrics

The metrics are located in the augur/api/metrics directory. They are a special kind of route that are created using the `@register_metric` decorator instead of the `@app.route` decorator. These are added to the Flask app in the create_app() method in the Server class. This is done by calling create_metrics(). create_metrics() then gets list of the metrics files in the metrics direcory, and imports them. Then it calls add_metrics() and passes the metrics file. add_metrics() then gets all the functions that are metrics and adds them to the Flask app. This is a very simplified version of how the metrics are added to the Flask app. Please see the README in the metrics direcory to learn more. 