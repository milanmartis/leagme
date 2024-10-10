import json
from datetime import datetime, timedelta

# AWS Lambda handler function
def lambda_handler(event, context):
    task = event.get("task")

    if task == "close_rounds":
        close_rounds()

    return {
        "statusCode": 200,
        "body": json.dumps("Úloha uzatvárania kôl bola úspešne dokončená.")
    }

# Funkcia na uzavretie kôl
def close_rounds():
    from website import create_app, db  # Importuješ až vnútri funkcie, aby sa predišlo kruhovému importu
    from website.models import Round  # Importuješ až vnútri funkcie

    app = create_app()  # Vytvoríš aplikáciu

    with app.app_context():  # Získaš prístup ku kontextu aplikácie
        current_time = datetime.now()

        # Predpokladáme, že máte definovaný SQLAlchemy model pre "Round"
        open_rounds = db.session.query(Round).filter_by(open=True).all()

        for round_instance in open_rounds:
            round_end_time = round_instance.round_start + timedelta(seconds=round_instance.duration)
            if current_time >= round_end_time:
                round_instance.open = False
                db.session.add(round_instance)

        db.session.commit()
        db.session.close()
