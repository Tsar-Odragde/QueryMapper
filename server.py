from http.server import BaseHTTPRequestHandler, HTTPServer  # Handles HTTP requests
import urllib.parse as urlparse  # Parses URLs and query parameters
import requests  # Handles HTTP requests for external APIs
import os  # Handles environment variables

# OAuth credentials and server configurations obtained from environment variables
CLIENT_ID = os.environ['YOUR_CLIENT_ID']
CLIENT_SECRET = os.environ['YOUR_CLIENT_SECRET']
REDIRECT_URI = os.environ['REDIRECT_URI']
PORT = os.environ['PORT']

# Define a custom request handler class to handle GET requests
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the incoming request path and query parameters
        parsed_path = urlparse.urlparse(self.path)
        
        # Check if the request is for the "/callback" path
        if parsed_path.path == "/callback":
            # Extract the authorization code from the query parameters
            query = urlparse.parse_qs(parsed_path.query)
            code = query.get("code", [None])[0]  # Extract the 'code' parameter
            
            # If the authorization code is found, exchange it for an access token
            if code:
                token_response = self.exchange_code_for_token(code)
                if token_response:
                    # Respond with the access token as JSON if successful
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(token_response.encode())  # Send the token
                else:
                    # Respond with an error if the token exchange fails
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(b"Error exchanging code for token.")
            else:
                # Respond with an error if the authorization code is not found
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Authorization code not found.")
        else:
            # Respond with a 404 error if the path is not "/callback"
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Path not found.")
    
    # Method to exchange the authorization code for an access token
    def exchange_code_for_token(self, code):
        token_url = "https://api.mercadolibre.com/oauth/token"  # MercadoLibre token URL
        
        # Prepare the payload for the POST request to obtain the token
        payload = {
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'redirect_uri': REDIRECT_URI
        }
        
        # Send a POST request to the token endpoint with the payload
        response = requests.post(token_url, data=payload)
        if response.status_code == 200:
            return response.text  # Return the access token JSON response if successful
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None  # Return None if there's an error

# Function to start the server and listen for incoming requests on the specified port
def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    server_address = ('', int(PORT))  # Bind the server to the specified port
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()  # Start the server and keep it running

# Entry point to run the server
if __name__ == "__main__":
    run()
