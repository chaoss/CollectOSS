from flask import Flask, request, session, render_template, url_for, redirect, send_file, Response
from sqlalchemy import MetaData, Table, create_engine
from bootstrap import ServerThread, Environment
from sqlalchemy.orm import Session
from metadata import __version__
from secrets import token_hex
from functools import wraps
from pathlib import Path

import threading, json, subprocess

top = Path.cwd()
template_dir = top / "augur/templates/"
static_dir = top / "augur/static/"
dbfile = top / "db.config.json"

def requires_key(func):
    global app
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = request.args.get("key") or request.form.get("key") or session.get("key")
        
        if not key or key != app.secret_key:
            return redirect(url_for("root"))
        return func(*args, **kwargs)
    
    return wrapper

def render_section(template, **kwargs):
    global app
    with app.app_context():
        return json.loads(render_template(f"json/{template}.j2", **kwargs))

def get_db_string(db_config):
    return f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database_name']}"

def first_time(setup_key, port = 5000):
    """
    Run first time setup for this instance.
    """
    env = Environment()
    global app
    app = Flask(__name__, static_folder=static_dir, template_folder=template_dir)
    app.secret_key = setup_key
    sections = []
    
    dbconf = {
        "user":"", 
        "password":"", 
        "host":"", 
        "port":"", 
        "database_name":""
    }
    
    if dbstring := env["AUGUR_DB"]:
        sections.append({ "title": "Database", "settings": [
            { "id": "connection_string",
                "display_name": "Database Connection String",
                "value": dbstring,
                "description": "This connection string was provided pre-setup as an environment variable."
            }
        ]})
    else:
        if dbfile.exists():
            dbconf = json.load(dbfile.open())
        sections.append(render_section("db.json", dbconf=dbconf, subtitle="Current config"))

    def all_in(source, update):
        for key in update.keys():
            if key not in source:
                return False
        return True

    # Create a multithreading context for message passing
    update_complete = threading.Condition()
    
    @app.route("/favicon.ico")
    def get_favicon():
        return send_file(static_dir / "favicon" / "favicon.ico")

    @app.route("/", methods = ["GET", "POST"])
    def root():
        key = request.args.get("key") or request.form.get("key") or session.get("key")
        
        if not key or key != app.secret_key:
            return render_template("first-time-key.j2")
        
        session["key"] = key
        return render_template("first-time.j2", sections = sections, version = __version__, gunicorn_placeholder = "")
    
    @app.route("/db/test")
    @requires_key
    def test_db():
        test = subprocess.Popen("augur db test-connection".split(), text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        result = test.communicate()
        if test.returncode:
            return result[1], 500
        elif result[0]:
            return result[0], 500
        return "Success!"
    
    @app.route("/db/version")
    @requires_key
    def version_db():
        out = subprocess.Popen("augur db print-db-version".split(), text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        result = out.communicate()[0]
        return result or "Undefined"
    
    @app.route("/db/versions/list")
    @requires_key
    def versions_db():
        out = subprocess.Popen("augur db check-for-upgrade".split(), text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        result = out.communicate()[0]
        return result or "Error"
    
    @app.route("/db/config/load")
    @requires_key
    def config_db():
        # try:
        dbstring = env["AUGUR_DB"] or get_db_string(dbconf)
        conn = create_engine(dbstring)
        meta = MetaData()
        meta.reflect(bind=conn, schema="augur_operations")
        config: Table = meta.tables["augur_operations.config"]
        session = Session(conn)
        result = session.query(config).all()
        desired = []
        for row in result:
            if row[2] in ["github_api_key", "gitlab_api_key", "repo_directory", "connection_string"]:
                print(row)
                desired.append(row)
        
        session.close()
        return "Success!"
    
    @app.route("/db/update")
    @requires_key
    def update_db():
        if dbstring := request.args.get("dbstring"):
            env["AUGUR_DB"] = dbstring
        else:
            dbconf = {
                "user": request.args.get("user"), 
                "password": request.args.get("password"), 
                "host": request.args.get("host"), 
                "port": request.args.get("port"), 
                "database_name": request.args.get("database_name")
            }
        
            json.dump(dbconf, dbfile.open("w"), indent=4)
        
        return redirect(url_for("root"))

    @app.route("/stop")
    @requires_key
    def shutdown():
        # Notify the primary thread that the temp server is going down
        update_complete.acquire()
        update_complete.notify_all()
        update_complete.release()
        return "Server shutting down"

    # Start a single-use server for first-time setup
    server = ServerThread(app, port = port, reraise = True)
    server.start()

    # Listen for the server /stop command, then shutdown the server
    update_complete.acquire()
    try:
        update_complete.wait()
    except KeyboardInterrupt as e:
        # Shutdown gracefully on interrupt and abort relaunch
        global autorestart
        if autorestart:
            return True
    except Exception as e:
        # On an unexpected exception, reraise after shutting down
        raise e
    finally:
        server.shutdown()
        update_complete.release()

if __name__ == "__main__":
    import sys
    autorestart = False
    if len(sys.argv) > 1:
        autorestart = True
    port = input("Enter the port to use for the configuration interface [8075]: ") or "8075"
    setup_key = "5" #token_hex()
    print("-" * 40)
    print("The configuration interface is starting up")
    print("You'll need the following key to unlock the interface:", setup_key)
    print("If you're hosting Augur locally, you can open this link to access the interface:")
    print(f"http://127.0.0.1:{port}?key={setup_key}")
    
    while first_time(setup_key, port):
        global app
        del app

    #     if not settings:
    #         # First time setup was aborted, so just quit
    #         os._exit(1)

    #     with open(config_location, "w") as config_file:
    #         yaml.dump(settings, config_file)

    # if not env["DEVELOPMENT"] and not gunicorn_location.is_file():
    #     with open(gunicorn_location, "w") as gunicorn_py:
    #         gunicorn_py.write(gunicorn_conf)

    # if env["DEVELOPMENT"]:
    #     from augur_view import app
    #     server = ServerThread(app, port = server_port, address = host_address, reraise = True)
    #     server.start()
    # else:
    #     server = subprocess.Popen(["gunicorn", "-c", str(gunicorn_location), "-b", f"{host_address}:{server_port}", "augur_view:app"])

    # try:
    #     server.wait()
    # except KeyboardInterrupt:
    #     # Shutdown gracefully on interrupt
    #     server.terminate()
    #     print("\nShutting down gracefully")