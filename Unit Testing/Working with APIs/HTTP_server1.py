# A simple HTTP Server 
# Connect from a web browser - 127.0.0.1:9999
# or from terminal - curl 127.0.0.1:9999
# or from postman - an HTTP client

from http.server import BaseHTTPRequestHandler, HTTPServer
import time

HOST = '127.0.0.1'
PORT = 9999

try:
    
    class MyHTTP(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type","text/html")
            self.end_headers()

            self.wfile.write(bytes("<html><body><h1>Hello World! </h1></body></html>","utf-8"))
            """
            date = time.strftime("%d-%m-%y %H:%M:%S", time.localtime(time.time()))
            self.wfile.write(bytes(date,"utf-8"))
            """

        def do_POST(self):
            
            content_length = int(self.headers['Content-Length'])                    # <--- Gets the size of data
            post_data = self.rfile.read(content_length)                             # <--- Gets the data itself
            print("\n",post_data.decode(),"\n")
            
            self.send_response(200)
            self.send_header("Content-type","text/html")
            self.end_headers()
            
            date = time.strftime("%d-%m-%y %H:%M:%S", time.localtime(time.time()))
            self.wfile.write(bytes(date,"utf-8"))
            
            #self.wfile.write(bytes("<html><body><h1>Hello World! </h1></body></html>","utf-8"))
            
            
            
    server = HTTPServer((HOST,PORT),MyHTTP)
    print("Server is running .....")
    server.serve_forever()
    server.server_close()
    print("Server stopped.....") 

except KeyboardInterrupt:
    print("Server has stopped running.....")