from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse as urlparse
import requests


CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
REDIRECT_URI = 'REDIRECT_URI'

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        if parsed_path.path == "/callback":
            query = urlparse.parse_qs(parsed_path.query)
            code = query.get("code", [None])[0]
            
            if code:
                token_response = self.exchange_code_for_token(code)
                if token_response:
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(token_response.encode())
                else:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(b"Error exchanging code for token.")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Authorization code not found.")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Path not found.")
    
    def exchange_code_for_token(self, code):
        token_url = "https://api.mercadolibre.com/oauth/token"
        
        payload = {
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'redirect_uri': REDIRECT_URI
        }
        
        response = requests.post(token_url, data=payload)
        if response.status_code == 200:
            return response.text  # Return the access token JSON response
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    server_address = ('', 3000)  
    httpd = server_class(server_address, handler_class)
    print("Starting server on http://localhost:3000...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()