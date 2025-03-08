import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import pathlib
import json
from datetime import datetime
import os
from jinja2 import Environment, FileSystemLoader

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class HttpHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.file_handler = FileHandler("storage/data.json")
        self.env = Environment(loader=FileSystemLoader("templates"))
        super().__init__(*args, **kwargs)

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        logging.info(f"Handling GET request for {url.path}")
        if url.path == "/":
            self.render_template("index.html")
        elif url.path == "/message":
            self.render_template("message.html")
        elif url.path == "/read":
            data = self.file_handler.read_json_file()
            self.render_template("read.html", messages=data)
        else:
            if pathlib.Path().joinpath(url.path[1:]).exists():
                self.send_static()
            else:
                self.render_template("error.html", 404)

    def do_POST(self):
        if self.path == "/message":
            post_data = self.parse_post_data()
            timestamp = datetime.now().isoformat()

            data = self.file_handler.read_json_file()
            data[timestamp] = post_data
            self.file_handler.write_json_file(data)

            logging.info(f"Message received and stored at {timestamp}")
            self.send_response_headers(302, "text/html", "/read")

    def parse_post_data(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        data = urllib.parse.unquote_plus(post_data.decode())
        logging.info(f"Parsed POST data: {data}")
        return {key: value for key, value in [el.split("=") for el in data.split("&")]}

    def render_template(self, template_name, status=200, **context):
        try:
            self.send_response_headers(status, "text/html")
            template = self.env.get_template(template_name)
            rendered_html = template.render(**context)
            self.wfile.write(rendered_html.encode())
            logging.info(f"Rendered template {template_name} with status {status}")
        except FileNotFoundError:
            self.send_response_headers(404, "text/html")
            self.wfile.write(b"File not found")
            logging.error(f"Template {template_name} not found")
        except Exception as e:
            self.send_response_headers(500, "text/html")
            self.wfile.write(f"Internal server error: {e}".encode())
            logging.error(f"Error rendering template {template_name}: {e}")

    def send_response_headers(self, status, content_type, location=None):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        if status == 302 and location:
            self.send_header("Location", location)
        self.end_headers()
        logging.info(
            f"Sent response headers with status {status} and content type {content_type}"
        )

    def send_static(self):
        self.send_response(200)
        mimetype = mimetypes.guess_type(self.path)
        if mimetype:
            self.send_header("Content-type", mimetype[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())
        logging.info(f"Served static file {self.path}")


class FileHandler:
    def __init__(self, filename):
        self.filename = filename

    def read_json_file(self):
        try:
            if os.path.exists(self.filename):
                with open(self.filename, "r", encoding="utf-8") as file:
                    logging.info(f"Reading JSON file {self.filename}")
                    return json.load(file)
        except (json.JSONDecodeError, OSError) as e:
            logging.error(f"Error reading JSON file {self.filename}: {e}")
        return {}

    def write_json_file(self, data):
        temp_filepath = self.filename + ".tmp"
        try:
            with open(temp_filepath, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)
            os.replace(temp_filepath, self.filename)
            logging.info(f"Written JSON data to {self.filename}")
        except OSError as e:
            logging.error(f"Error writing JSON file {self.filename}: {e}")


def run(server=HTTPServer, request_handler=HttpHandler):
    server_address = ("", 3000)
    server_instance = server(server_address, request_handler)
    logging.info("Starting server at localhost:3000")
    try:
        server_instance.serve_forever()
    except KeyboardInterrupt:
        server_instance.server_close()
        logging.info("Server stopped")


if __name__ == "__main__":
    run()
