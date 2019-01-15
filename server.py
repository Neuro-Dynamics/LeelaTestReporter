from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
import sys
import webbrowser
import json
import os

eventHandlers = []
GUI = {}


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    # Handler for the GET requests
    def do_GET(self):
        if self.path == "/":
            self.path = "login.html"

        try:
            # Check the file extension required and
            # set the right mime type
            sendReply = False
            binary = False
            if self.path.endswith(".html"):
                mimetype = 'text/html'
                sendReply = True
            if self.path.endswith(".js"):
                mimetype = 'application/javascript'
                sendReply = True
            if self.path.endswith(".css"):
                mimetype = 'text/css'
                sendReply = True
            if self.path.endswith(".jpg"):
                mimetype = 'image/jpg'
                sendReply = True
                binary = True
            if self.path.endswith(".gif"):
                mimetype = 'image/gif'
                sendReply = True
                binary = True
            if self.path.endswith(".png"):
                mimetype = 'image/png'
                sendReply = True
                binary = True

            if sendReply == True:
                if binary:
                    # Open the static file requested and send it
                    f = open(self.path[1:], 'rb')
                    self.send_response(200)
                    self.send_header('Content-type', mimetype)
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()
                else:
                    f = open(self.path[1:])
                    self.send_response(200)
                    self.send_header('Content-type', mimetype)
                    self.end_headers()
                    self.wfile.write(bytes(f.read(), 'utf-8'))
                    f.close()
            return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):

        # Get post Command
        c = self.path.split('/')
        event = c[1]
        sender = c[2]

        # Get post data
        global GUI
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        body = body.decode('utf-8')
        # print(body)

        s = '{{"Event":"{}","Sender":"{}","Body":"{}"}}'.format(
            event, sender, body)
        # print(s)

        # Init GUI
        if event == 'init':
            GUI = json.loads(body, strict=False)
            handler(sender, event)

        # Quit Application
        if event == "quit":
            print('\nQuitting application...')
            saveGUI()
            self.stop_serving = True
            sys.exit(0)

        # Respond to click
        if event == 'click':
            GUI = json.loads(body, strict=False)
            handler(sender, event)

        # Respond to change
        if event == 'change':
            GUI = json.loads(body, strict=False)
            handler(sender, event)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(GUI), 'utf-8'))


def handler(sender, event):
    for s, e, h in eventHandlers:
        if sender == s and event == e:
            h()


def initGUI(func):
    eventHandlers.append(('application', 'init', func))


def onClick(id, func):
    eventHandlers.append((id, 'click', func))


def onChange(id, func):
    eventHandlers.append((id, 'change', func))


def startGUI(url):
    httpd = HTTPServer(('localhost', 8080), SimpleHTTPRequestHandler)
    webbrowser.open_new_tab('http://localhost:8080/' + url)
    httpd.serve_forever()


def saveGUI():
    with open('GUI.json', 'w') as f:
        json.dump(GUI, f)
