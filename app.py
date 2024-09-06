
from website import create_app, db
from flask_socketio import SocketIO

app = create_app()
socketio = SocketIO(app)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        socketio.run(app, debug=False)
        # app.run(host='0.0.0.0', port=5000, debug=False)