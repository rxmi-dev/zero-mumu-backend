from flask import Flask, send_file
import os

app = Flask(__name__)

@app.route('/')
def serve_test():
    return send_file('test.html')

@app.route('/health')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    app.run(port=5000, debug=True)