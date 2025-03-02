from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import pathlib
import json
from datetime import datetime
import os

class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def do_POST(self):
        if self.path == '/message':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data_parse = urllib.parse.unquote_plus(post_data.decode())
            data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
            timestamp = datetime.now().isoformat()

            storage_dir = 'storage'
            data_file = os.path.join(storage_dir, 'data.json')
            os.makedirs(storage_dir, exist_ok=True)

            data = read_json_file(data_file)
            data[timestamp] = data_dict
            write_json_file(data_file, data)

            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mimetype = mimetypes.guess_type(self.path)
        if mimetype:
            self.send_header("Content-type", mimetype[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

def read_json_file(filepath):
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as file:
                return json.load(file)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading JSON file {filepath}: {e}")
    return {}


def write_json_file(filepath, data):
    temp_filepath = filepath + '.tmp'
    try:
        with open(temp_filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
        os.replace(temp_filepath, filepath)
    except OSError as e:
        print(f"Error writing JSON file {filepath}: {e}")

def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()

if __name__ == '__main__':
    run()