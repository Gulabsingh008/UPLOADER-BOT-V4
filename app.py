from flask import Flask
#import os

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

#port = int(os.environ.get("PORT", 8080))

if __name__ == '__main__':
    # Run the Flask app on port 80
    app.run(host='0.0.0.0', port=80)
