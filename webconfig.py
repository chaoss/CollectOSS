#!/usr/bin/env python

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

FISH_BIN_PATH = False  # will be set later
IS_PY2 = sys.version_info[0] == 2

if IS_PY2:
    import SimpleHTTPServer
    import SocketServer
    from urlparse import parse_qs
else:
    import http.server as SimpleHTTPServer
    import socketserver as SocketServer
    from urllib.parse import parse_qs

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


class FishConfigTCPServer(SocketServer.TCPServer):
    """TCPServer that only accepts connections from localhost (IPv4/IPv6)."""
    WHITELIST = set(['::1', '::ffff:127.0.0.1', '127.0.0.1'])

    address_family = socket.AF_INET6 if socket.has_ipv6 else socket.AF_INET

    def verify_request(self, request, client_address):
        return client_address[0] in FishConfigTCPServer.WHITELIST


class FishConfigHTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def write_to_wfile(self, txt):
        self.wfile.write(txt.encode('utf-8'))

redirect_template_html = """
<!DOCTYPE html>
<html>
 <head>
  <meta http-equiv="refresh" content="0;URL='%s'" />
 </head>
 <body>
  <p><a href="%s">Start the Fish Web config</a></p>
 </body>
</html>
"""

# We want to show the demo prompts in the directory from which this was invoked,
# so get the current working directory
initial_wd = os.getcwd()

# Make sure that the working directory is the one that contains the script
# server file, because the document root is the working directory.
# where = os.path.dirname(sys.argv[0])
# os.chdir(where)

# Generate a 16-byte random key as a hexadecimal string
authkey = binascii.b2a_hex(os.urandom(16)).decode('ascii')

# Try to find a suitable port
PORT = 8000
HOST = "::" if socket.has_ipv6 else "localhost"
while PORT <= 9000:
    try:
        Handler = FishConfigHTTPRequestHandler
        httpd = FishConfigTCPServer((HOST, PORT), Handler)
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
    print("Unable to find an open port between 8000 and 9000")
    sys.exit(-1)

# Get any initial tab (functions, colors, etc)
# Just look at the first letter

url = 'http://localhost:%d/%s/' % (PORT, authkey)

# Create temporary file to hold redirect to real server. This prevents exposing
# the URL containing the authentication key on the command line (see
# CVE-2014-2914 or https://github.com/fish-shell/fish-shell/issues/1438).
if 'XDG_CACHE_HOME' in os.environ:
    dirname = os.path.expanduser(os.path.expandvars('$XDG_CACHE_HOME/fish/'))
else:
    dirname = os.path.expanduser('~/.cache/fish/')

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
