from flask import Flask, render_template

app = Flask(__name__)

whiteboard = {
    "Room 1": {"provider": "Dr. Smith", "surgeon": "Dr. Jones"},
    "Room 2": {"provider": "Dr. Lee", "surgeon": "Dr. Patel"}
}

@app.route('/')
def home():
    return render_template('index.html', whiteboard=whiteboard)

if __name__ == '__main__':
    app.run(debug=True)