from __future__ import unicode_literals
from __future__ import print_function
import binascii
import cgi
try:
    from html import escape as escape_html
except ImportError:
    from cgi import escape as escape_html
from distutils.version import LooseVersion
import glob
import multiprocessing.pool
import operator
import os
import platform
import random
import re
import select
import socket
import string
import subprocess
import sys
from itertools import chain

import http.server as SimpleHTTPServer
import socketserver as SocketServer
from urllib.parse import parse_qs

# This code is (heavily) adapted from the fish shell web config functionality. Many thanks to them!
# Find more info about fish here: https://fishshell.com/

def isMacOS10_12_5_OrLater():
    """ Return whether this system is macOS 10.12.5 or a later version. """
    version = platform.mac_ver()[0]
    return version and LooseVersion(version) >= LooseVersion('10.12.5')

def is_wsl():
    """ Return whether we are running under the Windows Subsystem for Linux """
    if 'linux' in platform.system().lower():
        with open('/proc/version', 'r') as f:
            if 'Microsoft' in f.read():
                return True
    return False

# Disable CLI web browsers
term = os.environ.pop('TERM', None)
# This import must be done with an empty $TERM, otherwise a command-line browser may be started
# which will block the whole process - see https://docs.python.org/3/library/webbrowser.html
import webbrowser
if term:
    os.environ['TERM'] = term

try:
    import json
except ImportError:
    import simplejson as json


class AugurConfigTCPServer(SocketServer.TCPServer):
    """TCPServer that only accepts connections from localhost (IPv4/IPv6)."""
    WHITELIST = set(['::1', '::ffff:127.0.0.1', '127.0.0.1'])

    address_family = socket.AF_INET6 if socket.has_ipv6 else socket.AF_INET

    def verify_request(self, request, client_address):
        return client_address[0] in AugurConfigTCPServer.WHITELIST


class AugurConfigHTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        p = self.path

        authpath = '/' + authkey
        if self.secure_startswith(p, authpath):
            p = p[len(authpath):]
        else:
            return self.send_error(403)
        self.path = p

        return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

        # Return valid output
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # Output JSON
        self.write_to_wfile(json.dumps(output))

    def do_POST(self):
        p = self.path

        authpath = '/' + authkey
        if self.secure_startswith(p, authpath):
            p = p[len(authpath):]
        else:
            return self.send_error(403)
        self.path = p

        ctype, pdict = cgi.parse_header(self.headers['content-type'])

        length = int(self.headers['content-length'])
        url_str = self.rfile.read(length).decode('utf-8')
        postvars = {}
        for key, value in parse_qs(url_str, keep_blank_values=1).items():
            postvars[key] = value[0]

        with open('../temp.config.json', 'w') as temp_config_file:
            temp_config_file.write(json.dumps(postvars, indent=4))

        # Return valid output
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def secure_startswith(self, haystack, needle):
        if len(haystack) < len(needle):
            return False
        bits = 0
        for x, y in zip(haystack, needle):
            bits |= ord(x) ^ ord(y)
        return bits == 0

    def log_request(self, code='-', size='-'):
        """ Disable request logging """
        pass

    def log_error(self, format, *args):
        if format == 'code %d, message %s':
            # This appears to be a send_error() message
            # We want to include the path
            (code, msg) = args
            format = 'code %d, message %s, path %s'
            args = (code, msg, self.path)
        SimpleHTTPServer.SimpleHTTPRequestHandler.log_error(self, format, *args)

redirect_template_html = """
<!DOCTYPE html>
<html>
 <head>
  <meta http-equiv="refresh" content="0;URL='%s'" />
 </head>
 <body>
  <p><a href="%s">Starting the Augur web config</a></p>
 </body>
</html>
"""

initial_wd = os.getcwd()

# Generate a 16-byte random key as a hexadecimal string
authkey = binascii.b2a_hex(os.urandom(16)).decode('ascii')

# Try to find a suitable port
PORT = 8000
HOST = "::" if socket.has_ipv6 else "localhost"
while PORT <= 9000:
    try:
        Handler = AugurConfigHTTPRequestHandler
        httpd = AugurConfigTCPServer((HOST, PORT), Handler)
        # Success
        break
    except socket.error:
        err_type, err_value = sys.exc_info()[:2]
        # str(err_value) handles Python3 correctly
        if 'Address already in use' not in str(err_value):
            print(str(err_value))
            break
    PORT += 1

if PORT > 9000:
    # Nobody say it
    # But if you must, say it quietly please. There are people trying to work
    print("Unable to find an open port between 8000 and 9000")
    sys.exit(-1)

url = 'http://localhost:%d/%s/' % (PORT, authkey)

# Create temporary file to hold redirect to real server. This prevents exposing
# the URL containing the authentication key on the command line (see
# CVE-2014-2914 or https://github.com/fish-shell/fish-shell/issues/1438).
if 'XDG_CACHE_HOME' in os.environ:
    dirname = os.path.expanduser(os.path.expandvars('$XDG_CACHE_HOME/augur/'))
else:
    dirname = os.path.expanduser('~/.cache/augur/')

os.umask(0o0077)
try:
    os.makedirs(dirname, 0o0700)
except OSError as e:
    if e.errno == 17:
        pass
    else:
        raise e

randtoken = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for _ in range(6))
filename = dirname + 'web_config-%s.html' % randtoken

f = open(filename, 'w')
f.write(redirect_template_html % (url, url))
f.close()

# Open temporary file as URL
# Use open on macOS >= 10.12.5 to work around #4035.
fileurl = 'file://' + filename
print("Web config started at '%s'. Hit enter to stop." % fileurl)
if isMacOS10_12_5_OrLater():
    subprocess.check_call(['open', fileurl])
elif is_wsl():
    subprocess.call(['cmd.exe', '/c', "start %s" % url])
else:
    webbrowser.open(fileurl)

# Select on stdin and httpd
stdin_no = sys.stdin.fileno()
try:
    while True:
        ready_read = select.select([sys.stdin.fileno(), httpd.fileno()], [], [])
        if ready_read[0][0] < 1:
            print("Shutting down.")
            # Consume the newline so it doesn't get printed by the caller
            sys.stdin.readline()
            break
        else:
            httpd.handle_request()
except KeyboardInterrupt:
    print("\nShutting down.")

# Clean up temporary file
os.remove(filename)
