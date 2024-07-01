from werkzeug.debug import DebuggedApplication
from werkzeug.serving import make_server
import threading

class ServerThread(threading.Thread):
    """
    Create a runnable Flask server app that automatically launches on a separate
    thread.
    """
    def __init__(self, app, port = 5000, address = "0.0.0.0", reraise = False):
        threading.Thread.__init__(self)

        # Required to enable debugging with make_server
        if reraise:
            app.config['PROPAGATE_EXCEPTIONS'] = True
            app.config['TESTING'] = True
            app.config['DEBUG'] = True
            app.config['TRAP_HTTP_EXCEPTIONS'] = True
            app.config['TEMPLATES_AUTO_RELOAD'] = True

        debug_app = DebuggedApplication(app, True)

        self.server = make_server(address, port, debug_app, threaded = True, passthrough_errors=True)
        self.ctx = app.app_context()
        self.ctx.push()

        # For compatibility with subprocesses
        self.terminate = self.shutdown
        self.wait = self.join

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()