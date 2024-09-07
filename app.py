from website import create_app, db, celery
from flask_socketio import SocketIO

# Create Flask app
app = create_app()
socketio = SocketIO(app)

if __name__ == '__main__':
    with app.app_context():
        # db.create_all()
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)