from website import create_app, db, celery
from flask_socketio import SocketIO
from website.database_initializer import initialize_database

# Create Flask app
app = create_app()
socketio = SocketIO(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        initialize_database()
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)