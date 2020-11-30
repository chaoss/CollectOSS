import http.server
import socketserver
import logging
import cgi
import json
from pathlib import Path
import re

PORT = 8003

class ServerHandler(http.server.SimpleHTTPRequestHandler):

    def generateHTML(self, json_data):
        print(json_data)

        if "path" not in json_data:
            print("'path' is missing for data: " + json_data)
            return
        log_file = Path(json_data["path"]).stem

        worker_name = re.search("[a-z_]{1,20}worker", log_file).group()
        if not worker_name:
            print("Failed to get worker name, so cannot associate input data with any augur worker. Data: " + json_data)
            return

        if "error" not in json_data:
            print("'error' is missing for data: " + json_data)
            return
        if "@timestamp" not in json_data:
            print("'@timestamp' is missing for data: " + json_data)
            return
        data = """

<table class="%s">
    <tr>
        <th>Error message</th>
        <td id="error">%s</td>
    </tr>
    <tr>
        <th>Log file</th>
        <td>%s</td>
    </tr>
    <tr>
        <th>Time collected</th>
        <td>%s</td>
    </tr>
</table>
        """ % (
            worker_name,
            json_data["error"],
            json_data["path"],
            json_data["@timestamp"]
        )
        return data

    def do_GET(self):
        logging.error(self.headers)
        http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        http.server.SimpleHTTPRequestHandler.do_GET(self)
        content_lenght = self.headers['Content-Length']
        payload = self.rfile.read(int(content_lenght))
        data = json.loads(payload)
        self.wfile.write(payload)
        html = self.generateHTML(data)
        if not html:
            print("Failed to generate html form data: " + data)
        with open("index.html","a") as fp:
            fp.write(html)

Handler = ServerHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        print("serving at port", PORT)
        httpd.serve_forever()
    except:
        print("stopping the http server...")
        httpd.shutdown()