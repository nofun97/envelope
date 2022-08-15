#!/usr/bin/env python3

import difflib
from http import server
import json
import sys
import urllib.request

wiring = json.load(open(sys.argv[1]))
ingress = wiring['ingress']
foo = wiring['egresses']['foo']
bar = wiring['egresses']['bar']

def get(url):
    with urllib.request.urlopen(url) as f:
        return str(f.read(), 'utf-8')

class MyServer(server.BaseHTTPRequestHandler):
    def do_GET(self):
        print(self.path)
        try:
            fooData = get(foo)
            barData = get(bar)
            diff = difflib.context_diff(
                fooData.split('\n'),
                barData.split('\n'),
                fromfile='foo',
                tofile='bar',
                lineterm='',
            )

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            def p(s): self.wfile.write(bytes(s + '\n', 'utf-8'))
            p("<html><body><pre>")
            for line in diff:
                p(line)
            p("</pre></body></html>")
            print('done')
        except:
            print('oops!')
            raise

if __name__ == "__main__":
    (hostName, serverPort) = ingress.split(':')
    serverPort = int(serverPort)
    webServer = server.HTTPServer((hostName, serverPort), MyServer)
    print(f"Server listening at {hostName}:{serverPort}")
    print("downstreams:")
    print(f"  foo: {foo}")
    print(f"  bar: {bar}")

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
