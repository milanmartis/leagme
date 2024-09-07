from website import create_app, db
from flask_socketio import SocketIO

# Vytvorenie aplikácie Flask
app = create_app()
socketio = SocketIO(app)

# Používajte existujúci Celery z 'app'
celery = app.celery

if __name__ == '__main__':
    with app.app_context():
        # Vytvorenie databázových tabuliek, ak je to potrebné
        # db.create_all()
        
        # Spustenie aplikácie s podporou Socket.IO
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)