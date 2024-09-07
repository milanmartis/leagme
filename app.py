from website import create_app, db, make_celery
from flask_socketio import SocketIO

# Vytvorenie aplikácie Flask
app = create_app()
socketio = SocketIO(app)

# Inicializácia Celery
celery = make_celery(app)

if __name__ == '__main__':
    with app.app_context():
        # Vytvorenie databázových tabuliek, ak je to potrebné
        # db.create_all()
        
        # Spustenie aplikácie s podporou Socket.IO
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)