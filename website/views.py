from flask import Blueprint, render_template, request, jsonify, flash, jsonify, redirect, url_for, session, current_app, send_file
from flask_login import login_required, current_user
from flask_security import roles_required
from sqlalchemy import text

import os
from dotenv import load_dotenv
load_dotenv()
from .models import Note, User, Duel, Place, OpeningHours, Season, Groupz, Round, Product, Order, user_duel, user_group, user_season, PaymentCard, BillingInfo
from .models import PushSubscription, Reservation, Field
from pywebpush import webpush, WebPushException
from . import db, current_app
import json
from sqlalchemy import func, or_, and_
from sqlalchemy import insert, update
import stripe
from slugify import slugify

from . import tabz, duels, dictionary, mysql
from datetime import datetime, timedelta
from itertools import combinations
from sqlalchemy.inspection import inspect
from flask_sqlalchemy import SQLAlchemy
import requests

import sqlite3
from flask import jsonify
import numbers
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import joinedload
from sqlalchemy import select, update
from sqlalchemy.orm import lazyload, joinedload, subqueryload
from collections import defaultdict
from itertools import groupby
import random
from random import sample
from random import shuffle
# import mysql.connector
from . import conn
from .utils import send_new_round_email
import psycopg2
import email
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, SelectMultipleField, IntegerField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, StopValidation, NumberRange, Optional
from wtforms import DateField, DateTimeField, DateTimeLocalField, Form
from psycopg2.errorcodes import UNIQUE_VIOLATION
from psycopg2 import errors
import datetime
from datetime import datetime as datetime2
from datetime import datetime as dt
from math import ceil, log2, log
from functools import wraps
from py_vapid import Vapid
from sqlalchemy.exc import IntegrityError  # Importujte pre zachytávanie chýb pri vkladaní do databázy
from website import mail



# Stripe konfigurácia
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
vapid_public_key=os.environ.get("VAPID_PUBLIC_KEY")
def roles_required(*roles):
    """Dekorátor, ktorý kontroluje, či má používateľ aspoň jednu z požadovaných rolí."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                # Ak používateľ nie je prihlásený, presmeruje ho na prihlasovaciu stránku
                flash("Please log in", "warning")
                return redirect(url_for('auth.login'))
            
            # Skontroluje, či má používateľ aspoň jednu z požadovaných rolí
            if not any(role.name in roles for role in current_user.roles):
                flash("You don't have permission, make a subscription", "error")
                return redirect(url_for('views.index'))

            # Ak má používateľ povolenie, vykoná funkciu
            return f(*args, **kwargs)
        return decorated_function
    return decorator
        
views = Blueprint('views', __name__)



from firebase_admin import messaging

def send_push_notification(token, title, body):
    """Odoslanie push notifikácie na dané zariadenie pomocou FCM."""
    
    # Vytvorenie správy
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,  # Toto je token zariadenia, kam notifikáciu posielate
    )

    # Odoslanie správy
    try:
        response = messaging.send(message)
        print('Úspešne odoslané:', response)
    except Exception as e:
        print('Chyba pri odosielaní notifikácie:', e)
        
        

adminz = [2]
# season = 58
def is_integer(form, field):
    try:
        int(field.data)
    except (ValueError, TypeError):
        raise ValidationError('Field must be an integer.')
    
    
def is_power_of_two(form, field):
    try:
        value = int(field.data)
        if value == 0 or (value & (value - 1)) != 0:
            raise ValidationError('Number must be a power of two.')
    except ValueError:
        raise ValidationError('Invalid input. Please enter an integer.')

# print(current_user)




@views.route('/welcome', methods=['GET', 'POST'])
# @login_required
def welcome():
    seasons = db.session.query(Season).filter(
    or_(
        Season.visible == True    )
    ).all()
    
    return render_template("welcome.html", vapid_public_key=vapid_public_key, user=None, seasons=seasons)
    
    




@views.route('/', methods=['GET', 'POST'])
# @login_required
def index():
    # from py_vapid import Vapid

    # vapid = Vapid()
    # vapid.generate_keys()
    # print(f"Public Key: {vapid.public_key}")
    # print(f"Private Key: {vapid.private_key}")
    
    if not current_user.is_authenticated:
        # Ak nie je používateľ prihlásený, presmerujte ho na prihlasovaciu stránku
        return redirect(url_for('views.welcome'))

    # print('-----------------')
    # print(current_user.has_roles)
    # print('-----------------')
    # user_email = session.get('user_email')
    # user_id = session.get('user_id')
    # user_name = session.get('user_name')

    # dict_log = {
    #     'id': user_id, 
    #     'first_name': user_name, 
    #     'email': user_email,
    # }
    # print(roles_required('Admin'))
    # season_ids = [1,58]
    # seasons = db.session.query(Season).filter(Season.id.in_(season_ids)).all()
    # seasons = db.session.query(Season).filter(Season.open==True).all()
    # seasons = db.session.query(Season).filter(Season.visible==True)
    
    seasons = db.session.query(Season).filter(
    or_(
        Season.visible == True,
        Season.user_id == current_user.id
    )
    ).all()
    groupz = db.session.query(Groupz.round_id).all()
    # season_places = Season.query.filter_by(place_id=place.id)
    placeable = Place.query.filter_by(user_id=current_user.id).first()
    
    if request.method == "POST" and request.form.get('tournament_add'):
        
        print(request.form.get('tournament_add'))
        return redirect(url_for('views.tournament_new'))
       
        
    if request.method == "POST" and request.form.get('season_add'):
        
        # print(request.form.get('season_add'))
        return redirect(url_for('views.index'))

    
    

    if request.method == "POST" and request.form.get('season_id_button'):
        season1 = request.form.get('season_id')

        return redirect(url_for('views.home', season=season1))
    
    
    
    return render_template("index.html", vapid_public_key=vapid_public_key , seasons=seasons, user=current_user, adminz=adminz, placeable=placeable)
    

@views.route('/home/<season>/', methods=['GET', 'POST'])
@login_required
def home(season):


    groups = db.session.query(Groupz).join(
        Season).filter(Season.id == season).all()
    round = db.session.query(Groupz.round_id).filter(Groupz.season_id==season).order_by(Groupz.round_id.desc()).first()
    round_all_info = db.session.query(Round).filter(Round.season_id==season, Round.open==True).first()
    print(round)
    if round is not None:
        user_group = db.session.query(Groupz).join(User.groupy).filter(User.id == current_user.id).filter(Groupz.season_id == Season.id).filter(Season.id == season).filter(Groupz.round_id == round[0]).first()
    
    # myduels_user = db.session.query(Groupz.id).join(User.groupy).filter(Groupz.season_id == Season.id).filter(
    #     Season.id == season).filter(User.id.in_([current_user.id])).filter(Groupz.round_id == round[0]).all()

        players = User.query.all()
        data_show_table = tabz.show_table(season, round[0])
        data_all = tabz.show_table_all(season)
        round = (db.session.query(Round.id)
            .join(Season, Round.season_id == Season.id)
            .filter(Season.id == season)
            .order_by(Round.id.desc())
            .first())
        data_name_tabz = tabz.show_name_table(season, round[0])
    else:
        return redirect(url_for('views.season_manager', season=season))

    if request.method == "POST" and request.form.get("duelz"):

        duelz_players = []

        duelz = request.form.get("duelz")
        duelz_players = request.form.get("duelz_players")
        return redirect(url_for('views.duel_id', season=season, duelz=duelz, duelz_players=duelz_players))
    
    seas = Season.query.get(season)


    return render_template("home.html", round_all_info=round_all_info, vapid_public_key=vapid_public_key, round=round, seas = seas, season=season, user_group=user_group, groups=groups, dataAll=data_all, players=players, data_name_tabz=data_name_tabz, data_show_table=data_show_table, user=current_user, adminz=adminz)


# def make_tab_list():
#     length_tab_list = len(tabz.show_name_table(season, 2))
#     return list(range(0, int(length_tab_list)))


@views.route('/business-conditions', methods=['GET'])
# @login_required
def business_conditions():
    return render_template("business_conditions.html", user=current_user, adminz=adminz)






@views.route('/delete-note', methods=['POST'])
@login_required
# @roles_required('Admin','Manager','Player')
@roles_required('Admin')
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})


@views.route('/delete-duel', methods=['POST'])
@login_required
@roles_required('Admin')
# @roles_required('Admin','Manager','Player')
def delete_duel():
    duel = json.loads(request.data)
    duelId = duel['duelId']
    duel = Duel.query.get(duelId)
    if duel:
        db.session.delete(duel)
        db.session.commit()

    return jsonify({})


@views.route('/update-duel', methods=['POST', 'GET'])
@login_required
@roles_required('Admin', 'Manager', 'Player')
def update_duel():
    duelCheck = json.loads(request.data)
    data = duelCheck["duelCheck"]
    data = data.split(",")
    duel_id, user_id, checked = int(data[1]), int(data[2]), data[0]

    # Aktualizácia stavu duelu
    u = update(user_duel).values({"checked": checked})
    u = u.where(user_duel.c.duel_id == duel_id)
    u = u.where(user_duel.c.user_id == user_id)
    db.session.execute(u)
    db.session.commit()

    # Získanie informácií o sezóne a kole pre duel
    duel = Duel.query.get(duel_id)
    season_id = duel.season_id
    current_round_id = duel.round_id

    # Kontrola, či sú všetky duely v aktuálnom kole kompletné
    # if check_all_duels_completed(current_round_id):
    #     # Ak áno, spracuj duely a nastav ďalšie kolo
    #     process_duels_and_setup_next_round(season_id, current_round_id)

    return jsonify({})

def check_all_duels_completed(round_id):
    incomplete_duels = Duel.query.filter_by(round_id=round_id, checked='false').first()
    return incomplete_duels is None



# def assign_players_to_duel_and_group(group_id, player1_id, player2_id, season_id, round_id):
#     # Vytvorenie nového duelu
#     new_duel = Duel(season_id=season_id, round_id=round_id)
#     db.session.add(new_duel)
#     db.session.flush()  # Flush pre získanie ID novovytvoreného duelu pred commitom

#     # Priradenie hráčov k novovytvorenému duelu
#     entries = [
#         {'duel_id': new_duel.id, 'user_id': player1_id},
#         {'duel_id': new_duel.id, 'user_id': player2_id}
#     ]
#     for entry in entries:
#         db.session.execute(user_duel.insert(), entry)
    
#     db.session.commit()


def calculate_rounds(num_players):
    """Vráti celkový počet kôl potrebných na dokončenie turnaja."""
    return int(ceil(log2(num_players)))


def create_new_round(season_id):
    new_round = Round(season_id=season_id, open=True)
    db.session.add(new_round)
    db.session.commit()
    return new_round

# @celery.task
def generate_tournament_structure(season_id):
    players = db.session.query(User)\
        .join(user_season)\
        .filter(User.id == user_season.c.user_id)\
        .filter(user_season.c.season_id == season_id)\
        .order_by(func.random())\
        .all()
    num_players = len(players)
    num_rounds = calculate_rounds(num_players)

    # Vytvorenie hlavnej Round pre celý turnaj
    # print("************************************OOO************************************")
    # print(season_id)
    # print("************************************OOO************************************")
    tournament_round = create_new_round(season_id)

    # Vytvorenie skupín pre každé kolo
    for round_number in range(1, num_rounds + 1):
        group = Groupz(name=f"Kolo {round_number}", shorts=str(round_number), season_id=season_id, round_id=tournament_round.id)
        db.session.add(group)
        
        if round_number==1:
            for player in players:
                player = User.query.get(player.id)
                group_new = Groupz.query.get(group.id)
                player.groupy.append(group_new)

    db.session.commit()

    # Vytvorenie duelov len pre prvé kolo
    if num_rounds >= 1:
        # Náhodné premiešanie hráčov
        shuffle(players)

        # Vytvorenie duelov pre prvé kolo z premiešaného zoznamu
        first_group = Groupz.query.filter_by(name="Kolo 1", season_id=season_id, round_id=tournament_round.id).first()
        
        for i, player in enumerate(players[::2]):  # Iteruje cez každého druhého hráča
            if i*2 + 1 < len(players):  # Zabezpečenie, že existuje ďalší hráč pre duel
                # i je tu index každého druhého hráča, takže poradové číslo duelu je i + 1
                poradove_cislo = i + 1
                create_duel(first_group.id, players[i*2].id, players[i*2+1].id, season_id, tournament_round.id, poradove_cislo)


    # Vytvorenie "prázdnych" duelov pre ďalšie kola
    for round_number in range(2, num_rounds + 1):
        num_duels = 2 ** (num_rounds - round_number)  # Počet duelov v danom kole
        for _ in range(num_duels):
            
                    create_duel_for_future_rounds(season_id, tournament_round.id, round_number)

    db.session.commit()

def create_duel(group_id, player1_id, player2_id, season_id, round_id, poradove_cislo):
    # print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
    season_user = db.session.query(user_season).filter(user_season.c.season_id==season_id).all()
    groupz_short = db.session.query(Groupz).filter(Groupz.id==group_id)
    pocet_user_season = len(season_user)
    fin = pocet_user_season / 2
    sign_list = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','R','S','T','U','V','X','Y','Z']

    new_duel = Duel(season_id=season_id, round_id=round_id, notice=sign_list[poradove_cislo - 1],groupz_id=group_id)
    db.session.add(new_duel)
    db.session.flush()  # Získanie ID pre duel

    # Priradenie hráčov k duelu (len pre prvé kolo)
    assign_players_to_duel(season_id, new_duel.id, player1_id, player2_id, poradove_cislo)

def create_duel_for_future_rounds(season_id, round_id, round_number):
    # Predpokladajme, že máte funkciu na vytvorenie alebo získanie groupz pre dané kolo
    group = get_or_create_group_for_round(season_id, round_id)
    if group:
        
        # new_duel = Duel(season_id=season_id, round_id=round_id, groupz_id=group.id + (round_number - 1), notice="player ?")
        # db.session.add(new_duel)
        # db.session.commit()
        next_gr = group.id + (round_number - 1)
        # print(next_gr)
        create_duel(next_gr, '', '', season_id, round_id, round_number)
    else:
        print("No group found or created for the specified round.")


def get_or_create_group_for_round(season_id, round_id):
    # Tu môžete implementovať logiku na získanie existujúcej skupiny alebo vytvorenie novej skupiny pre dané kolo
    # Tento príklad len ilustruje koncept a bude potrebné ho prispôsobiť vašim potrebám
    group = Groupz.query.filter_by(season_id=season_id, round_id=round_id).first()
    if not group:
        group = Groupz(name=f"Round {round_id} Group", season_id=season_id, round_id=round_id)
        db.session.add(group)
        db.session.flush()  # Použite flush na získanie ID novej skupiny pred commitom, ak plánujete ihneď použiť jej ID
        
        
    return group

# dom = 0

def assign_players_to_duel(season_id,duel_id, player1_id, player2_id, poradove_cislo):

    duel = Duel.query.get(duel_id)
    if not duel:
        print("Duel does not exist.")
        return

    # Pre každého hráča vytvoríme alebo aktualizujeme záznam v user_duel
    
    # player1_id = int(player1_id) if player1_id is not None else ''
    # player2_id = int(player2_id) if player2_id is not None else ''
    season_user = db.session.query(user_season).filter(user_season.c.season_id==season_id).all()
    duel_list_first_groupz = db.session.query(Groupz).filter(Groupz.round_id==duel.round_id).first()
    
    # user_duel_last_record = db.session.query(user_duel).filter(user_duel.c.notez==duel.id).all()

    # print(user_duel_last_record)
    # print("aaaaaaaaaaaaaaaaaaaaaa")
    duel_first_groupz = db.session.query(Duel.id).filter(Duel.round_id==duel.round_id).all()
    print(len(duel_first_groupz))
    
    
    # duel_ids = [str(duel[0]) for duel in duel_first_groupz]

    # Inicializácia zoznamu pre uloženie výsledkov dotazov
    user_duel_records_with_notez = []

    # for duel_id in duel_ids:
            
    player_idss = [1, 2]  # Predpokladajme, že toto sú ID hráčov, ktoré chcete pridať
    
    all_players = len(season_user) + 1   

    if not player1_id or not player2_id:
        for index, player_id in enumerate(player_idss, start=(len(duel_first_groupz)-1)):
            # print(f"POMOOOOC - {duel.groupz_id}")
            # index = index + dom
            duel_no = db.session.query(Duel).filter(Duel.round_id == duel.round_id).order_by(Duel.id.asc()).offset((len(duel_first_groupz) + index)- all_players).first()
            new_record = user_duel.insert().values(
                            addons=duel.groupz_id,
                            duel_id=duel_id,
                            notez=duel_no.id
                        )
            db.session.execute(new_record)

            
        
    else:
        for player_id in [player1_id, player2_id]:
            if player_id:
                # Skontrolujeme, či už existuje záznam pre daného hráča a duel
                existing_record = db.session.query(user_duel).filter_by(user_id=player_id, duel_id=duel_id).first()
                if existing_record:
                    # Ak existuje, aktualizujeme len notez
                    existing_record.notez = poradove_cislo
                else:
                    # Inak vytvoríme nový záznam
                    new_record = user_duel.insert().values(
                        addons=duel.groupz_id,
                        user_id=player_id,
                        duel_id=duel_id
                    )
                    db.session.execute(new_record)

    # Nezabudneme na commit zmeny
    db.session.commit()

# def process_duels_and_setup_next_round(season_id, current_round_id):
#     # Získanie duelov a ich výsledkov pre aktuálne kolo
#     duels = Duel.query.filter_by(season_id=season_id, round_id=current_round_id).all()
    
#     winners = []
#     for duel in duels:
#         # Predpokladáme, že máme funkciu na získanie víťaza duelu
#         winner = get_duel_winner(duel.id)
#         if winner:
#             winners.append(winner)
    
#     # Vytvorenie nového kola, ak existujú víťazi na postup
#     if winners and len(winners) > 1:
#         new_round = Round(season_id=season_id)
#         db.session.add(new_round)
#         db.session.flush()  # Získame ID pre nové kolo pred vytvorením duelov

#         # Vytvorenie nových duelov pre nasledujúce kolo s víťazmi
#         for i in range(0, len(winners), 2):
#             new_duel = Duel(season_id=season_id, round_id=new_round.id)
#             db.session.add(new_duel)
#             db.session.flush()  # Získame ID nového duelu

#             # Priradenie víťazov k novému duelu
#             for winner_id in winners[i:i+2]:
#                 user_duel_record = {'user_id': winner_id, 'duel_id': new_duel.id}
#                 db.session.execute(user_duel.insert(), user_duel_record)

#         db.session.commit()

# def get_duel_winner(duel_id):
#     # Táto funkcia by mala vrátiť ID víťaza duelu na základe výsledkov uložených v tabuľke user_duel
#     duel_results = db.session.execute(
#         user_duel.select().where(user_duel.c.duel_id == duel_id)
#     ).fetchall()
    
#     # Logika na určenie víťaza z duel_results, napríklad na základe skóre alebo iných kritérií
#     # Vrátiť ID víťaza

#     # Tu je len príkladná logika, skutočná implementácia bude závisieť od schémy výsledkov
#     # Predpokladajme, že víťaz má vyššie 'points' alebo iné kritérium
#     winner = max(duel_results, key=lambda x: x['points'])
#     return winner['user_id'] if winner else None

# Dynamicky nastavíme audience podľa subscription endpointu
def get_audience_from_subscription(endpoint):
    if "fcm.googleapis.com" in endpoint:
        return "https://fcm.googleapis.com"
    elif "push.services.mozilla.com" in endpoint:
        return "https://updates.push.services.mozilla.com"
    elif "notify.windows.com" in endpoint:
        return "https://wns.windows.com"
    elif "web.push.apple.com" in endpoint:
        return "https://web.push.apple.com"
    elif "push.opera.com" in endpoint:
        return "https://push.opera.com"
    else:
        raise ValueError(f"Neznámy push server pre endpoint: {endpoint}")

@views.route('/send_game_change_notification', methods=['POST'])
@login_required
@roles_required('Admin','Manager','Player')
def send_game_change_notification():
    # Definovanie notifikácie, ktorú chceme poslať
    notification_payload = {
        "title": "Your Game Changed",
        "body": "Toto je test push notifikácie",
        "icon": "/static/img/icon.png"
    }

    # Načítanie všetkých subscription z databázy
    subscriptions = PushSubscription.query.all()

    if not subscriptions:
        return jsonify({"message": "Nie sú uložené žiadne predplatné (subscriptions)"}), 400

    # Posielanie Web Push notifikácií pre všetky uložené subscriptions
    for subscription in subscriptions:
        try:
            # Získaj endpoint z databázy
            endpoint = subscription.endpoint

            # Dynamické získanie audience (na základe endpointu)
            audience = get_audience_from_subscription(endpoint)

            # Nastavenie VAPID claimov s dynamickým audience
            vapid_claims = {
                "sub": "mailto:tvoj-email@example.com",
                "aud": audience
            }

            # Posielanie push notifikácie pomocou webpush
            webpush(
                subscription_info={
                    "endpoint": subscription.endpoint,
                    "keys": {
                        "p256dh": subscription.p256dh,
                        "auth": subscription.auth
                    }
                },
                data=json.dumps(notification_payload),
                vapid_private_key=os.environ.get("VAPID_PRIVATE_KEY"),
                vapid_claims=vapid_claims
            )

        except WebPushException as ex:
            print(f"Chyba pri posielaní Web Push notifikácie: {ex}")
            if ex.response:
                print(f"Detailná odpoveď zo servera: Status kód: {ex.response.status_code}, Text: {ex.response.text}")
            return jsonify({"message": "Chyba pri odoslaní Web Push notifikácie2"}), 500
        except ValueError as ve:
            print(f"Chyba: {ve}")
            return jsonify({"message": f"Chyba: {ve}"}), 400

    return jsonify({"message": "Notifikácia bola úspešne odoslaná všetkým používateľom"}), 200



##### CRON  #####
# @celery.task
# def check_and_close_rounds_task():
#     # Získaj aktuálny čas
#     current_time = datetime.now()

#     # Načítaj všetky otvorené kolá, kde duration nie je prázdne
#     open_rounds = Round.query.filter(Round.open == True, Round.duration.isnot(None)).all()

#     for round_instance in open_rounds:
#         # Vypočíta čas ukončenia kola (round_start + duration v sekundách)
#         round_end_time = round_instance.round_start + timedelta(seconds=round_instance.duration)

#         # Ak je aktuálny čas väčší ako čas ukončenia, nastav `open` na False a uzavri kolo
#         if current_time >= round_end_time:
#             round_instance.open = False
#             db.session.add(round_instance)

#             # Získaj všetky duely v tomto kole (round) a aktualizuj ich status
#             duels_in_round = Duel.query.filter_by(round_id=round_instance.id).all()
#             for duel in duels_in_round:
#                 # Aktualizuj user_duel pre oboch hráčov
#                 user_duels = db.session.query(user_duel).filter(user_duel.c.duel_id == duel.id).all()
#                 for user_duel_instance in user_duels:
#                     # Nastav `checked` na True
#                     user_duel_update = update(user_duel).where(user_duel.c.duel_id == duel.id).values(checked="true")
#                     db.session.execute(user_duel_update)

#                     # Aktualizácia bodov podľa výsledku duelu (na základe tvojej logiky)
#                     result, against = user_duel_instance.result, user_duel_instance.against
#                     season = Season.query.get(duel.season_id)

#                     # Určenie bodov pre hráča
#                     if result == 6 and against <= 4:
#                         points = season.winner_points
#                     elif result == 6 and against == 5:
#                         points = season.winner_points
#                     elif result == 5 and against == 6:
#                         points = 1
#                     elif result <= 4 and against == 6:
#                         points = 0
#                     elif result == 4 and against == 0:
#                         points = season.winner_points
#                     elif result == 0 and against == 0:
#                         points = 0
#                     else:
#                         points = 0

#                     # Aktualizácia bodov pre user_duel
#                     update_points = update(user_duel).where(user_duel.c.duel_id == duel.id, user_duel.c.user_id == user_duel_instance.user_id).values(points=points)
#                     db.session.execute(update_points)

#     # Ulož všetky zmeny do databázy
#     db.session.commit()

#     return f"Closed all opened rounds after limit and updated duels."


@views.route('/update-duel2', methods=['POST', 'GET'])
@login_required
@roles_required('Admin','Manager','Player')
# @roles_required('Admin','Manager','Player')
def update_duel2():
    try:
        duelResult = json.loads(request.data)
        data = duelResult["duelResult"]
        # print(data)
        data = data.split(",")
        duel = Duel.query.get(int(data[1]))
        season = Season.query.filter_by(id=duel.season_id).first()
        # calculating points
        
        # if int(data[0]) > int(data[3]):
        #     points = int(season.winner_points)
        #     points2 = 0
        # if int(data[0]) < int(data[3]):
        #     points2 = int(season.winner_points)
        #     points = 0
        # if int(data[0]) == int(data[3]):
        #     points = 1
        #     points2 = 1
        
        if int(data[0]) == 6 and int(data[3]) <= 4:
            points = int(season.winner_points)
        elif int(data[0]) == 6 and int(data[3]) == 5:
            points = int(season.winner_points)
        elif int(data[0]) == 5 and int(data[3]) == 6:
            points = 1
        elif int(data[0]) <= 4 and int(data[3]) == 6:
            points = 0
        elif int(data[0]) == 4 and int(data[3]) == 0:
            points = int(season.winner_points)
        elif int(data[0]) == 0 and int(data[3]) == 0:
            points = 0
        else:
            points = 0

        if int(data[3]) == 6 and int(data[0]) <= 4:
            points2 = int(season.winner_points)
        elif int(data[3]) == 6 and int(data[0]) == 5:
            points2 = int(season.winner_points)
        elif int(data[3]) == 5 and int(data[0]) == 6:
            points2 = 1
        elif int(data[3]) <= 4 and int(data[0]) == 6:
            points2 = 0
        elif int(data[3]) == 4 and int(data[0]) == 0:
            points2 = int(season.winner_points)
        elif int(data[3]) == 0 and int(data[0]) == 0:
            points2 = 0
        else:
            points2 = 0
            
  
        if data:
            u = update(user_duel)
            u = u.values({"result": int(data[0]), "against": int(data[3]), "points": int(points)})
            u = u.where(user_duel.c.duel_id == int(data[1]))
            u = u.where(user_duel.c.user_id == int(data[2]))
            u2 = update(user_duel)
            u2 = u2.values({"result": int(data[3]), "against": int(data[0]), "points": int(points2)})
            u2 = u2.where(user_duel.c.duel_id == int(data[4]))
            u2 = u2.where(user_duel.c.user_id == int(data[5]))

            db.session.execute(u)
            db.session.execute(u2)
            db.session.commit()
            
            # duel = Duel.query.get(int(data[1]))

            if duel:
                # Dotaz na získanie objektu Season podľa season_id z duel
                season = Season.query.filter_by(id=duel.season_id).first()

                if season:
                    # Tlačíme typ sezóny
                    # print(season.season_type)
                    # update_duel_and_assign_winner(data)
                    pass
                else:
                    print("Season not found for the given duel.")
            else:
                print("Duel not found.")
                
            
            
            # update_duel_and_assign_winner(data)
            if season.season_type == 2:   
                duell = Duel.query.get(int(data[1]))  
                winner_user_id = None
                if points == season.winner_points:  # Ak hráč 1 vyhral
                    winner_user_id = int(data[2])
                elif points2 == season.winner_points:  # Ak hráč 2 vyhral
                    winner_user_id = int(data[5])
                    
                
                if winner_user_id:
                    new_user = User.query.get(winner_user_id)
                    if new_user:
                        new_user_id = new_user.id
                    else:
                        new_user_id = None
                else:
                    new_user_id = None
                
                # new_user = User.query.get(winner_user_id)
                # if winner_user_id:
                #     new_user_id = new_user.id
                # else:
                #     new_user_id = None
                    
                user_duel_update = db.session.query(user_duel).filter(user_duel.c.notez==str(duell.id))
                update_expr = user_duel.update().\
                    where(user_duel.c.notez == duel.id).\
                    values(user_id=new_user_id)

                # Vykonanie aktualizačného výrazu
                db.session.execute(update_expr)
                existing_record = db.session.query(user_group).filter(user_group.c.duel_id == duel.id).first()

                if existing_record:
                    # Záznam existuje, skontrolujte, či user_id zodpovedá new_user_id
                    
                    if existing_record.user_id != new_user_id:
                        # Ak user_id sa líši, aktualizujte záznam
                        update_statement = user_group.update().\
                            where(user_group.c.duel_id == duel.id).\
                            values(user_id=new_user_id, groupz_id=((duell.groupz_id) + 1), season_id=duell.season_id, round_id=duell.round_id)
                        db.session.execute(update_statement)
                else:
                    # Záznam neexistuje, vložte nový záznam
                    insert_statement = user_group.insert().values(
                        user_id=new_user_id, 
                        duel_id=duell.id,
                        groupz_id=((duell.groupz_id) + 1), 
                        season_id=duell.season_id, 
                        round_id=duell.round_id
                    )
                    db.session.execute(insert_statement)

                # Uložte zmeny
                db.session.commit()
                

        # Načítanie všetkých subscription z databázy
        # subscriptions = PushSubscription.query.filter(PushSubscription.user_id == int(data[2]) or int(data[5]) a nerovna sa current_user.id).first()
        subscriptions = PushSubscription.query.filter(
            and_(
                or_(PushSubscription.user_id == int(data[2]), PushSubscription.user_id == int(data[5])),
                PushSubscription.user_id != current_user.id  # Exclude current user
            )
        ).all()
        print(int(data[5]))

        notification_payload = {
            "title": "Your Game Changed",
            "body": "Toto je test push notifikácie",
            "icon": "/static/img/icon.png"
        }
        if not subscriptions:
            return jsonify({"message": "Nie sú uložené žiadne predplatné (subscriptions)"}), 400

        # Posielanie Web Push notifikácií pre všetky uložené subscriptions
        for subscription in subscriptions:
            try:
                # Získaj endpoint z databázy
                endpoint = subscription.endpoint

                # Dynamické získanie audience (na základe endpointu)
                audience = get_audience_from_subscription(endpoint)

                # Nastavenie VAPID claimov s dynamickým audience
                vapid_claims = {
                    "sub": "mailto:tvoj-email@example.com",
                    "aud": audience
                }

                # Posielanie push notifikácie pomocou webpush
                webpush(
                    subscription_info={
                        "endpoint": subscription.endpoint,
                        "keys": {
                            "p256dh": subscription.p256dh,
                            "auth": subscription.auth
                        }
                    },
                    data=json.dumps(notification_payload),
                    vapid_private_key=os.environ.get("VAPID_PRIVATE_KEY"),
                    vapid_claims=vapid_claims
                )

            except WebPushException as ex:
                print(f"Chyba pri posielaní Web Push notifikácie: {ex}")
                if ex.response:
                    print(f"Detailná odpoveď zo servera: Status kód: {ex.response.status_code}, Text: {ex.response.text}")
                return jsonify({"message": "Chyba pri odoslaní Web Push notifikácie2"}), 500
            except ValueError as ve:
                print(f"Chyba: {ve}")
                return jsonify({"message": f"Chyba: {ve}"}), 400

        # return jsonify({"message": "Notifikácia bola úspešne odoslaná všetkým používateľom"}), 200
                


        return jsonify(success=True)
    

    except Exception as e:
        print('error:', e)
        # V prípade chyby vráťte chybovú správu
        return jsonify(error="An error occurred"), 500
        
       
       
 
       
       
        
        
        
def update_duel_and_assign_winner(data):
    try:
        # Rozloženie dát
        duel_id, winner_user_id = data[1], data[2] if data[0] > data[3] else data[5]
        
        # Načítanie existujúceho duelu
        duel = Duel.query.get(duel_id)
        if not duel:
            print("Duel neexistuje.")
            return
        
        # Určenie nasledujúceho duelu pre víťaza
        next_duel = Duel.query.filter(Duel.round_id == duel.round_id + 1).first()
        if not next_duel:
            # Ak neexistuje, vytvoríme nový duel v nasledujúcom kole
            next_duel = Duel(notice=f'{duel.round_id + 1} kolo', date_duel=dt.now(), season_id=duel.season_id, round_id=duel.round_id + 1)
            db.session.add(next_duel)
        
        # Priradenie víťaza do duelu a skupiny
        player = User.query.get(winner_user_id)
        if player:
            # Priradenie hráča do nasledujúceho duelu
            if not next_duel.player1:
                next_duel.player1 = player
            elif not next_duel.player2:
                next_duel.player2 = player
            
            # Priradenie hráča do skupiny pre nasledujúce kolo
            next_group = Groupz.query.get(duel.groupz_id + 1)
            if next_group and player not in next_group.users:
                next_group.users.append(player)
            
            db.session.commit()
        else:
            print("Hráč neexistuje.")
        
    except Exception as e:
        print(f'Vyskytla sa chyba: {e}')
        db.session.rollback()



def update_or_create_user_duel(duel_id, winner_user_id, next_group_id):
    print(duel_id)
    print(winner_user_id)
    print(next_group_id)
    # Skontrolovanie existencie záznamu v user_duel pre daného hráča a duel
    user_duel_record = db.session.execute(
        db.select(user_duel).where(user_duel.c.duel_id == duel_id, user_duel.c.user_id == winner_user_id)
    ).fetchone()

    if user_duel_record:
        # Aktualizujeme existujúci záznam
        stmt = (
            update(user_duel).
            where(user_duel.c.duel_id == duel_id, user_duel.c.user_id == winner_user_id).
            values(result=...,  # aktualizujte podľa potreby
                # aktualizujte ďalšie polia podľa potreby
                )
        )
    else:
        # Vytvárame nový záznam
        stmt = (
            insert(user_duel).
            values(duel_id=duel_id,
                user_id=winner_user_id,
                result=...,  # nastavte podľa potreby
                # nastavte ďalšie polia podľa potreby
                )
        )

    # Vykonáme príkaz
    db.session.execute(stmt)
    db.session.commit()
    
    # Aktualizácia alebo priradenie hráča k novej skupine
    player = User.query.get(winner_user_id)
    if player:
        next_group = Groupz.query.get(next_group_id)
        if next_group:
            # Ak hráč už je priradený k nejakej skupine, môžete tu pridať logiku na jeho odstránenie z predchádzajúcej skupiny
            # a priradiť ho k novej, ak je to potrebné podľa vašej aplikácie
            if next_group not in player.groupy:
                player.groupy.append(next_group)
        else:
            print(f"Group with ID {next_group_id} not found.")
    else:
        print(f"Player with ID {winner_user_id} not found.")
    
    # Uloženie zmien do databázy
    db.session.commit()


def find_next_duel_id_for_winner(current_duel_id, total_players):
    current_duel = Duel.query.get(current_duel_id)
    total_rounds = log2(total_players)
    current_round = ceil(log2(current_duel_id + 1))
    duel_index_in_round = current_duel_id - 2**(current_round - 1) + 1
    next_round_first_duel_id = 2**current_round

    next_duel_index = ceil(duel_index_in_round / 2)
    next_duel_id = next_round_first_duel_id + next_duel_index - 1

    if current_round >= total_rounds:
        return None  # Neexistuje ďalší duel, súčasný duel je finále

    # Vráťte Duel objekt alebo ID pre nasledujúci duel
    return Duel.query.filter_by(id=next_duel_id, round_id=current_round+1).first()


@views.route('/season/<season>/duel/<duelz>', methods=['GET', 'POST'])
@login_required
@roles_required('Admin','Manager','Player')
# @roles_required('Admin')
def duel_id(season, duelz):
    
    # user_email = session.get('user_email')
    # user_id = session.get('user_id')
    # user_name = session.get('user_name')

    # dict_log = {
    #     'id': user_id, 
    #     'first_name': user_name, 
    #     'email': user_email,
    # }


    # season = 1

    duel = db.session.query(User.first_name, user_duel, Duel.round_id).filter(
        user_duel.c.user_id == User.id).filter(user_duel.c.duel_id == Duel.id).filter(Duel.id == duelz).order_by(User.id.desc()).all()

    roundz = db.session.query(Round).filter(Round.season_id==season).filter(Round.open==True).order_by(Round.id.desc()).first()
    group = db.session.query(User)\
        .join(user_group, User.id == user_group.c.user_id)\
        .join(Groupz, Groupz.id == user_group.c.groupz_id)\
        .join(user_duel, User.id == user_duel.c.user_id)\
        .filter(user_duel.c.duel_id == duelz)\
        .first() 
        
    
    # group = db.session.query(User).filter(user_group.c.groupz_id==Groupz.id).filter(user_duel.c.duel_id==duelz).filter(user_duel.c.user_id==User.id).filter(Groupz.round_id==5).first()

#     group = (
#     db.session.query(User)
#     .join(user_group, user_group.c.user_id == User.id)  # Spája User s Groupz cez asociáciu user_group
#     .join(Groupz, Groupz.id == user_group.c.groupz_id)  # Explicitný JOIN medzi User a Groupz
#     .join(Duel, Duel.user_id == User.id)  # Explicitný JOIN medzi User a UserDuel
#     .filter(Duel.duel_id == duelz)  # Filtruje UserDuel podľa ID duelu
#     .filter(Groupz.round_id == 5)  # Filtruje Groupz podľa round_id
#     .options(joinedload(User.groupz), joinedload(User.user_duel))
#     .first()
# )
    # print('---------------------')
    # print(duel)
    # print('------------------')
    seas = Season.query.get(season)

    return render_template("duel.html", vapid_public_key=vapid_public_key, seas = seas, season=season, group=group, roundz=roundz,  duel=duel, players=duelz, user=current_user, adminz=adminz)




@views.route('/season/<season>/round/<round>', methods=['GET', 'POST'])
@login_required
@roles_required('Admin','Manager','Player')
# @roles_required('Player')
def duel_view(season, round):
    
    # user_email = session.get('user_email')
    # user_id = session.get('user_id')
    # user_name = session.get('user_name')

    # dict_log = {
    #     'id': user_id, 
    #     'first_name': user_name, 
    #     'email': user_email,
    # }
    season_obj = Season.query.filter(Season.id==season).first()
    new_ret = duels.create_duels_list(season, round)
    # print(len(new_ret))

    # group = db.session.query(Groupz).join(Season).filter(Season.id == season).filter(Groupz.round_id == round).first()
    groups = db.session.query(Groupz).join(Season).filter(Season.id == season).filter(Groupz.round_id == round).all()

    seas = Season.query.get(season)
    roundz = Round.query.get(int(round))
    seas_no_r = db.session.query(Round).filter(Round.season_id==seas.id).all()
    # print(seas_no_r.round_id)
    # print("xxcxcxcxcxcxxcxxxx")
    
    
    if request.method == 'POST':
        grno2 = request.form.get('grno')
        grname = request.form.get('grname')
        seasons2 = request.form.get('season')
        round2 = request.form.get('round')
        # print('------------------------')
        # print(grname)
        # print(seasons2)
        # print(round2)
        # print(grno2)
        # print('------------------------')
        
        # duel_view(seasons, grno)

        return redirect(url_for('views.duel_view', seas=seas, round=round2, group=grno2, season=seasons2))

    if request.method == "POST" and request.form.get("duelz"):

        duelz_players = []
        # flash('Lets play!!!', category='success')

        duelz = request.form.get("duelz")
        duelz_players = request.form.get("duelz_players")

        # duel_players = db.session.query(User)\
        #          .join(User.seasony)\
        #          .filter(Duel.id.like(duelz))\
        #          .first()

        return redirect(url_for('views.duel_id', season=season, duelz=duelz, duelz_players=duelz_players))
    
    #seas = Season.query.get(season)
    manager = db.session.query(Season.user_id).filter(Season.user_id==current_user.id).filter(Season.id==season).first()

    if seas.season_type == 1:
        return render_template("duels_filter.html", vapid_public_key=vapid_public_key, season_type=seas.season_type, manager=manager, seas_no_r=len(seas_no_r), roundz=roundz, seas = seas, season_obj=season_obj, round=round, groups=groups, season=season, duels=new_ret, user=current_user, adminz=adminz)
    if seas.season_type == 2:
        return render_template("duels_filter2.html", vapid_public_key=vapid_public_key, season_type=seas.season_type, manager=manager, seas_no_r=len(seas_no_r), roundz=roundz, seas = seas, season_obj=season_obj, round=round, groups=groups, season=season, duels=new_ret, user=current_user, adminz=adminz)


@views.route('/tournament/season/<int:season_id>/round/<int:round_id>', methods=['GET', 'POST'])
@login_required
def tournament(season_id, round_id):
    
    original_data = duels.create_tournament_list(season_id, round_id)
    total_rounds = db.session.query(Groupz).filter(Groupz.season_id==season_id).filter(Groupz.round_id==round_id).count()
    
    all_duels = db.session.query(user_duel)\
        .outerjoin(Duel, Duel.id == user_duel.c.duel_id)\
        .outerjoin(User, User.id == user_duel.c.user_id)\
        .outerjoin(Groupz, Groupz.id == user_duel.c.addons)\
        .filter(Groupz.season_id == season_id, Duel.round_id == round_id)\
        .order_by(user_duel.c.duel_id, user_duel.c.notez.asc())\
        .all()
      
    # for i, al in enumerate(original_data):
        # print(f"{i} - {al}")
        
    
    new_ret = transform_to_js_structure(original_data, season_id)
    # print(original_data)
    # Konverzia new_ret na JSON string
    return json.dumps(new_ret)
    # return render_template("tournament.html", new_ret_json=new_ret_json, user=current_user, adminz=adminz)


def transform_to_js_structure(input_data, season_id):
    # Initialize the structure for rounds
    rounds_structure = []

    for round_index, matches in enumerate(input_data):
        round_matches = []  # Initialize the list for the current round's matches
        for match_data in matches:
            # Initialize default match structure
            match_structure = {"player1": {}, "player2": {}}

            # Fill in details for player 1 if available
            if len(match_data['player']) > 0:
                if match_data['useride'][0]['user_id'] is not None:
                    player1_result = f"{match_data['player'][0]['first_name']}" if match_data['result_'][0]['result'] is not None else "?"
                else:
                    player1_result = 'waiting'

                match_structure["player1"] = {
                    "name": player1_result,
                    "ID": match_data['useride'][0]['user_id'],
                    "winner": False,  # Initialize winner as False
                    "url": "",  # Initialize URL as empty
                    "result": match_data['result_'][0]['result']
                }
                # Determine if player 1 is the winner
                if len(match_data['result_']) > 1 and match_data['result_'][0]['result'] > match_data['result_'][1]['result']:
                    match_structure["player1"]["winner"] = True
                # Set URL if available
                if 'duel_id' in match_data:
                    match_structure["player1"]["url"] = f"/season/{season_id}/duel/{match_data['duel_id']}"

            # Repeat for player 2
            if len(match_data['player']) > 1:
                if match_data['useride'][1]['user_id'] is not None:
                    player2_result = f"{match_data['player'][1]['first_name']} " if match_data['result_'][1]['result'] is not None else "Waiting"
                else:
                    player2_result = 'waiting'
                    
                match_structure["player2"] = {
                    "name": player2_result,
                    "ID": match_data['useride'][1]['user_id'],
                    "winner": False,  # Initialize winner as False
                    "url": "",
                    "result": match_data['result_'][1]['result']
                }
                # Determine if player 2 is the winner
                if len(match_data['result_']) > 1 and match_data['result_'][1]['result'] > match_data['result_'][0]['result']:
                    match_structure["player2"]["winner"] = True
                # Set URL if available
                if 'duel_id' in match_data:
                    match_structure["player2"]["url"] = f"/season/{season_id}/duel/{match_data['duel_id']}"

            round_matches.append(match_structure)  # Add the match to the round

        rounds_structure.append(round_matches)

    # Pridanie finálneho víťaza ako posledného "kola"
    if rounds_structure:  # Pridaj len ak existujú nejaké kola
        final_winner_match = determine_final_winner(rounds_structure[-1])
        if final_winner_match:
            rounds_structure.append([final_winner_match])

    return rounds_structure


def determine_final_winner(last_round):
    # Zistite víťaza posledného kola, ak existuje
    if not last_round:  # Ak je posledné kolo prázdne, vráť None
        return None

    last_match = last_round[-1]  # Získaj posledný duel v poslednom kole
    if last_match['player1']['winner']:
        return {"player1": last_match['player1'], "player2": None}
    elif last_match['player2']['winner']:
        return {"player1": last_match['player2'], "player2": None}
    return 'None'



####### NEW PLACE
def generate_unique_slug(session, name):
    # Vygeneruje základný slug z názvu
    slug = slugify(name)
    return slug


@views.route('/place/new', methods=['GET', 'POST'])
@views.route('/place/<int:place_id>/edit', methods=['GET', 'POST'])
@login_required
def new_or_edit_place(place_id=None):
    place = Place.query.get(place_id) if place_id else None
    form = NewPlace(obj=place)

    # Get existing opening hours for the place
    opening_hours = OpeningHours.query.filter_by(place_id=place.id).all() if place else []

    opening_hours_data = [
        {
            'day_of_week': oh.day_of_week,
            'open_time': oh.open_time.strftime('%H:%M'),
            'close_time': oh.close_time.strftime('%H:%M')
        }
        for oh in opening_hours
    ]

    if request.method == 'POST':
        if form.validate_on_submit():
            # Create or update place
            if place:
                form.populate_obj(place)
            else:
                slug = generate_unique_slug(db.session, form.name.data)
                places = Place.query.filter_by(slug=slug).first()
                if places is None:
                    place = Place(
                        name=form.name.data,
                        slug=slug,
                        address_street=form.address_street.data,
                        phone_number=form.phone_number.data,
                        coordinates=form.coordinates.data,
                        user_id=current_user.id
                    )
                    db.session.add(place)
                else:
                    flash("Choose another place name", category="error")
                    return render_template('place_create.html', form=form)

            db.session.commit()

            # Delete existing opening hours for the place once
            OpeningHours.query.filter_by(place_id=place.id).delete()

            # Retrieve form data, including opening hours
            form_data = request.form.to_dict(flat=False)
            print(form_data)  # Check the received form data in logs

            # Set to track unique days
            unique_days = set()

            # Process opening hours
            for key, values in form_data.items():
                if key.startswith('opening_hours'):
                    day = key.split('[')[1].split(']')[0]  # Get the day (e.g., 'Monday')
                    open_time = form_data[f'opening_hours[{day}][open_time]'][0]
                    close_time = form_data[f'opening_hours[{day}][close_time]'][0]

                    # Ensure unique days
                    if day not in unique_days and open_time and close_time:
                        unique_days.add(day)  # Add day to the set to avoid duplicates
                        opening_hour = OpeningHours(
                            day_of_week=day,
                            open_time=open_time,
                            close_time=close_time,
                            place_id=place.id
                        )
                        db.session.add(opening_hour)

            db.session.commit()

            flash('Place saved successfully.', 'success')
            return redirect(url_for('views.place_manager', place_slug=place.slug))

    return render_template(
        'place_create.html',
        form=form,
        place=place,
        opening_hours=opening_hours_data,  # Pass serialized opening hours data
        head='edit-place' if place else 'new-place',
        title='Edit Place' if place else 'Create New Place',
        user=current_user
    )


@views.route('/place/<int:place_id>/delete', methods=['POST'])
@roles_required('Admin', 'Player', 'Manager')
def delete_place(place_id):
    # Získať miesto podľa ID
    place = Place.query.get_or_404(place_id)

    # Skontrolovať, či používateľ je vlastníkom miesta alebo má príslušné práva
    if place.user_id != current_user.id:
        flash("You do not have permission to delete this place.", "error")
        return redirect(url_for('views.places'))

    try:
        # Vymazať miesto
        db.session.delete(place)
        db.session.commit()
        flash("Place has been deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while trying to delete the place: {str(e)}", "error")
    
    return redirect(url_for('views.places'))

    
@views.route('/places', methods=['GET'])
def places():
    places = Place.query.filter_by(user_id=current_user.id).all()
    
    return render_template("myplaces.html", vapid_public_key=vapid_public_key, places=places, user=current_user)

    

@views.route('/place/<place_slug>', methods=['GET', 'POST'])
@roles_required('Admin', 'Player', 'Manager')
def place_manager(place_slug):
    # Query the Place object based on the slug
    place = Place.query.filter_by(slug=place_slug).first()

    if not place:
        flash("Place not found.", category="error")
        return redirect(url_for('views.index'))

    # Query all seasons related to this place
    season_places = Season.query.filter_by(place_id=place.id).all()

    # Query fields related to this place
    fields = Field.query.filter_by(place_id=place.id).all()

    return render_template(
        "place.html", 
        vapid_public_key=vapid_public_key, 
        season_places=season_places, 
        fields=fields,  # Pass the fields to the template
        place=place, 
        user=current_user
    )




# Zobraziť dostupné ihriská v rámci miesta
@views.route('/place/<int:place_id>/fields', methods=['GET'])
def get_fields(place_id):
    place = Place.query.get_or_404(place_id)
    fields = Field.query.filter_by(place_id=place.id).all()
    opening_hours = OpeningHours.query.filter_by(place_id=place.id).all()
    
    return render_template("fields.html", place=place, fields=fields, opening_hours=opening_hours)

# Rezervácia ihriska
# @views.route('/place/<int:place_id>/fields/<int:field_id>/reserve', methods=['POST'])
# @login_required
# def reserve_field(place_id, field_id):
#     place = Place.query.get_or_404(place_id)
#     field = Field.query.get_or_404(field_id)
    
#     start_time_str = request.form['start_time']
#     end_time_str = request.form['end_time']
    
#     # Prevod z reťazca na datetime objekt
#     start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M')
#     end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M')
    
#     # Overiť, či rezervácia spadá do otváracích hodín
#     opening_hours = OpeningHours.query.filter_by(place_id=place.id, day_of_week=start_time.strftime('%A')).first()
    
#     if not (opening_hours and opening_hours.open_time <= start_time.time() <= opening_hours.close_time):
#         return jsonify({'error': 'Rezervácia mimo otváracích hodín'}), 400

#     # Skontroluj, či už nie je ihrisko rezervované v tom čase
#     existing_reservation = Reservation.query.filter_by(field_id=field.id).filter(
#         (Reservation.start_time <= start_time) & (Reservation.end_time >= end_time)
#     ).first()
    
#     if existing_reservation:
#         return jsonify({'error': 'Ihrisko je už rezervované na tento čas'}), 400

#     # Ak je všetko v poriadku, vytvor rezerváciu
#     reservation = Reservation(
#         user_id=current_user.id,
#         field_id=field.id,
#         start_time=start_time,
#         end_time=end_time,
#         place_id=place.id
#     )
    
#     db.session.add(reservation)
#     db.session.commit()
    
#     return jsonify({'success': 'Rezervácia bola úspešná'}), 200




# Endpoint na vytvorenie ihriska
@views.route('/place/<int:place_id>/field/new', methods=['GET', 'POST'])
@login_required
def create_field(place_id):
    place = Place.query.get_or_404(place_id)  # Získa miesto z databázy podľa ID

    if request.method == 'POST':
        # Získaj dáta z formulára
        field_name = request.form['name']
        field_description = request.form.get('description')
        field_capacity = request.form['capacity']

        # Vytvor nové ihrisko (Field) a priraď ho k miestu (Place)
        new_field = Field(
            name=field_name,
            description=field_description,
            capacity=int(field_capacity),
            place_id=place.id
        )
        db.session.add(new_field)
        db.session.commit()

        # Zobrazenie flash správy a presmerovanie na zoznam ihrísk
        place = Place.query.get_or_404(place_id)
        flash('Ihrisko bolo úspešne vytvorené.', 'success')
        return redirect(url_for('views.place_manager', place_slug=place.slug))

    return render_template('create_field.html', place=place, user=current_user)






def get_available_slots(open_time, close_time, reservations, slot_duration=1):
    """
    Funkcia na získanie dostupných časových slotov pre daný deň
    :param open_time: Čas otvárania (datetime.time)
    :param close_time: Čas zatvárania (datetime.time)
    :param reservations: Zoznam existujúcich rezervácií pre tento deň
    :param slot_duration: Trvanie slotu v hodinách (napr. 1 hodina)
    :return: Zoznam dostupných časov
    """
    available_slots = []
    current_time = dt.combine(dt.today(), open_time)
    closing_time = dt.combine(dt.today(), close_time)

    # Prejdi všetky časové intervaly medzi otváracím a zatváracím časom
    while current_time + timedelta(hours=slot_duration) <= closing_time:
        slot_start = current_time
        slot_end = current_time + timedelta(hours=slot_duration)

        # Skontroluj, či je tento slot už rezervovaný
        is_reserved = any(
            reservation.start_time <= slot_start.time() < reservation.end_time
            for reservation in reservations
        )

        if not is_reserved:
            available_slots.append({
                'start': slot_start.strftime('%H:%M'),
                'end': slot_end.strftime('%H:%M')
            })

        current_time += timedelta(hours=slot_duration)

    return available_slots






@views.route('/place/<int:place_id>/field/<int:field_id>/available_slots', methods=['GET'])
def available_slots(place_id, field_id):
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'error': 'No date provided'}), 400

    date = dt.strptime(date_str, '%Y-%m-%d')

    # Získaj objekt Field
    field = Field.query.get_or_404(field_id)

    # Zavolaj metódu get_opening_hours_for_day na priradený objekt Place
    opening_hours = field.place.get_opening_hours_for_day(date.weekday())

    if not opening_hours:
        return jsonify({'error': 'No opening hours for this day'}), 400

    # Pripoj čas k dátumu, aby sme mohli používať datetime objekty
    start_time = dt.combine(date, opening_hours.open_time)
    end_time = dt.combine(date, opening_hours.close_time)

    # Predpokladáme, že máme model Reservation na uchovávanie rezervácií
    reservations = Reservation.query.filter_by(field_id=field_id, reservation_date=date).all()

    # Definuj dostupné časové sloty (napr. od 9:00 do 18:00 každých 60 minút)
    slots = []
    current_time = start_time
    while current_time + timedelta(minutes=60) <= end_time:
        slot_start = current_time
        slot_end = current_time + timedelta(minutes=60)
        booked = False
        booked_by_current_user = False

        # Skontroluj, či je slot rezervovaný
        for reservation in reservations:
            if reservation.start_time == slot_start.time() and reservation.end_time == slot_end.time():
                booked = True
                if reservation.user_id == current_user.id:  # Rezervácia aktuálneho používateľa
                    booked_by_current_user = True
                break

        slots.append({
            'start': slot_start.strftime('%H:%M'),
            'end': slot_end.strftime('%H:%M'),
            'booked': booked,
            'booked_by_current_user': booked_by_current_user
        })
        current_time += timedelta(minutes=60)

    return jsonify(slots)





@views.route('/reserve_field', methods=['POST'])
@login_required
def reserve_field():
    place_id = request.form.get('place_id')
    # print(place_id)
    field_id = request.form.get('field_id')
    date = request.form.get('reservation_date')
    time_slot = request.form.get('time_slot')
    print(date)
    # Rozdelenie časového slotu na začiatok a koniec
    start_time, end_time = time_slot.split('-')

    # Overenie existencie miesta a ihriska
    place = Place.query.get(place_id)
    field = Field.query.get(field_id)

    if not place or not field:
        return jsonify({'success': False, 'error': 'Miesto alebo ihrisko neexistuje'}), 404

    # Overenie, či ihrisko patrí k miestu
    if field.place_id != place.id:
        return jsonify({'success': False, 'error': 'Ihrisko nepatrí k tomuto miestu'}), 400
    
    start_time = dt.strptime(start_time, '%H:%M').time()  # Prevod na typ time
    end_time = dt.strptime(end_time, '%H:%M').time()

    # Overenie, či je slot už rezervovaný
    existing_reservation = Reservation.query.filter_by(
        field_id=field_id, place_id=place_id, reservation_date=date,
        start_time=start_time, end_time=end_time
    ).first()

    if existing_reservation:
        return jsonify({'success': False, 'error': 'Slot je už rezervovaný'}), 400

    # Uloženie novej rezervácie
    new_reservation = Reservation(
        user_id=current_user.id,
        field_id=field_id,
        place_id=place_id,
        reservation_date=date,
        start_time=start_time,
        end_time=end_time
    )
    db.session.add(new_reservation)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Rezervácia bola úspešná!'})

        
        
@views.route('/place/<int:place_id>/field/<int:field_id>/cancel_booking', methods=['POST'])
def cancel_booking(place_id, field_id):
    data = request.get_json()
    time_slot = data.get('slot')
    date_str = data.get('reservation_date')

    if not time_slot or not date_str:
        return jsonify({'error': 'Missing data'}), 400

    slot_start_str, slot_end_str = time_slot.split('-')
    slot_start = dt.strptime(slot_start_str, '%H:%M').time()
    slot_end = dt.strptime(slot_end_str, '%H:%M').time()
    date = dt.strptime(date_str, '%Y-%m-%d')

    # Skontroluj, či existuje rezervácia pre aktuálneho používateľa
    reservation = Reservation.query.filter_by(
        field_id=field_id,
        place_id=place_id,
        user_id=current_user.id,
        reservation_date=date,
        start_time=slot_start,
        end_time=slot_end
    ).first()

    if not reservation:
        return jsonify({'error': 'Reservation not found'}), 404

    # Zruš rezerváciu
    db.session.delete(reservation)
    db.session.commit()

    return jsonify({'success': True})



@views.route('/tournament/new', methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'Manager')
def tournament_new():
    form = NewTournament()

    # Načítanie miest aktuálneho používateľa
    user_places = Place.query.filter_by(user_id=current_user.id).all()
    form.place_id.choices = [(place.id, place.name) for place in user_places]

    # Ak POST request neprejde validáciou
    if request.method == "POST" and not form.validate_on_submit():
        flash("You must fill in all required fields", 'error')

    # Ak formulár prešiel validáciou
    if form.validate_on_submit():
        season = db.session.query(Season).filter(Season.name.like(form.name.data)).first()
        season_type = int(request.form.get('season_type'))
        place_id = request.form.get('place_id')

        if not season:
            new_season = Season(
                name=form.name.data,
                no_group=1,
                winner_points=3,
                open=form.open.data,
                visible=form.visible.data,
                user_id=current_user.id,
                min_players=form.min_players.data,
                season_type=season_type,
                place_id=place_id
            )
            db.session.add(new_season)
            db.session.commit()
            return redirect(url_for('views.season_manager', season=new_season.id))
        else:
            flash("Tournament name must be unique.", category="error")

    return render_template("tournament_create.html", vapid_public_key=vapid_public_key, head='new-tournament', title='Create New Tournament', form=form, user=current_user, user_places=user_places)


    # return render_template("tournament_create.html", vapid_public_key=vapid_public_key, head='new-tournament', title='Create New Tournament', form=form, players=players, user=current_user, adminz=adminz)


####### NEW SEASON

@views.route('/season/new', methods=['GET', 'POST'])
@login_required
@roles_required('Admin','Manager')
# @roles_required('Admin')
def season_new():
    
    form = NewSeason()
    
    players = User.query.all()
    
    user_places = Place.query.filter_by(user_id=current_user.id).all()
    form.place_id.choices = [(place.id, place.name) for place in Place.query.filter_by(user_id=current_user.id).all()]
    if request.method == "POST" and not form.validate_on_submit():
        flash(f"you must fill in required fields", 'error')  # Toto vám ukáže chyby v konzole, ak nejaké existujú
    if form.validate_on_submit():
        season = db.session.query(Season).filter(Season.name.like(form.name.data)).first()
        season_type = int(request.form.get('season_type'))
        place_id = request.form.get('place_id')  # Získanie vybraného miesta z formulára
    
        ## season_from=form.season_from.data, 
        if not season:
                new_season = Season(name=form.name.data, no_group=form.no_group.data, 
                                    winner_points=form.winner_points.data, open=form.open.data, visible=form.visible.data ,user_id=current_user.id, min_players=form.min_players.data,season_type=season_type,place_id=form.place_id.data,duration=form.duration.data)
                db.session.add(new_season)
                db.session.commit()
                return redirect(url_for('views.season_manager', season=new_season.id))
        else:
            flash("Season name must be unique.", category="error")


        

    return render_template("season_create.html", vapid_public_key=vapid_public_key, head='new-season', title='Create Season', form=form, players=players, user=current_user, adminz=adminz, user_places=user_places)



@views.route('/season/delete/<season>', methods=['GET', 'POST'])
@login_required
@roles_required('Admin','Manager')
def season_delete(season):
  
    season = Season.query.get(season)
    if season:
        db.session.delete(season)
        db.session.commit()
        flash("Selected season have been deleted.", category="success")
        seasons = db.session.query(Season).all()
        # seasons = db.session.query(Season).filter(Season.open==True).all()
        return redirect(url_for('views.index', seasons=seasons, user=current_user, adminz=adminz))
    else:
        flash("Season does not exist.", category="error")
        seasons = db.session.query(Season).all()
        return redirect(url_for('views.index', seasons=seasons, user=current_user, adminz=adminz))



@views.route('/season/delete-player/<player>/<season>', methods=['POST'])
@login_required
@roles_required('Admin', 'Manager', 'Player')
def season_player_delete(player, season):
    action = request.form.get('action')

    if player and season and action == 'remove':
        season_obj = Season.query.get(season)
        user = User.query.get(player)
        if season_obj and user:
            user.seasony.remove(season_obj)
            db.session.commit()

            # Skontrolujte, či je hráč, ktorý má byť odstránený, aktuálny používateľ
            if int(player) == current_user.id:
                flash('You have been removed from the season.', 'success')
                message = 'You have been removed from the season'
            else:
                flash('Player has been removed from the season.', 'success')
                message = 'Player has been removed from the season'

            # Odošlite JSON odpoveď so správou a URL na presmerovanie
            response = {
                'status': 'success',
                'message': message,
                'redirect_url': url_for('views.season_manager', season=season)
            }
            return jsonify(response), 200
        else:
            response = {
                'status': 'error',
                'message': 'Season or player not found'
            }
            return jsonify(response), 404

    response = {
        'status': 'error',
        'message': 'Invalid request'
    }
    return jsonify(response), 400



@views.route('/pricing', methods=['GET', 'POST'])
def pricing_list():
    
    # customer_id = current_user.stripe_subscription_id  # Predpokladám, že máte stripe_customer_id uložené v používateľskom objekte
    # subscriptions = stripe.Subscription.list(customer=customer_id)
    # if not subscriptions:
       
        # products = Product.query.filter(Product.is_visible==True).order_by(Product.id.asc()).all()
    orders3 = Order.query.filter(Order.user_id==current_user.id).all()
    print(orders3)
    cards = PaymentCard.query.filter(PaymentCard.user_id==current_user.id).all()
    products = Product.query.filter(Product.is_visible==True).order_by(Product.id.asc()).all()
    orders = Order.query.filter(Order.user_id==current_user.id).all()

    return render_template("pricing.html",  vapid_public_key=vapid_public_key, orders3=orders3, products=products, adminz=adminz, checkout_public_key=os.environ.get("STRIPE_PUBLIC_KEY"), user=current_user, cards=cards, orders=orders)
    # else:
        # return render_template("pricing.html",  vapid_public_key=vapid_public_key, orders3=orders3, products=products, adminz=adminz, checkout_public_key=os.environ.get("STRIPE_PUBLIC_KEY"), user=current_user, cards=cards, orders=orders)
        # return redirect(url_for('auth.user_details'))



@views.route('/season', methods=['GET', 'POST'])
def season_list():

    # user_email = session.get('user_email')
    # user_id = session.get('user_id')
    # user_name = session.get('user_name')

    # dict_log = {
    #     'id': user_id, 
    #     'first_name': user_name, 
    #     'email': user_email,
    # }
    # print(roles_required('Admin'))
    season_ids = [1,58]
    seasons = db.session.query(Season).filter(Season.id.in_(season_ids)).all()
    # seasons = db.session.query(Season).filter(Season.open==True).all()
    groupz = db.session.query(Groupz.round_id).all()
    
        
    if request.method == "POST" and request.form.get('season_add'):
        
        # print(request.form.get('season_add'))
        return redirect(url_for('views.season_new'))

    if request.method == "POST" and request.form.get('tournament_add'):
        
        # print(request.form.get('season_add'))
        return redirect(url_for('views.tournament_new'))
       
    
    

    if request.method == "POST" and request.form.get('season_id_button'):
        season1 = request.form.get('season_id')

        return redirect(url_for('views.season_manager', season=season1))

    return render_template("season_list.html", vapid_public_key=vapid_public_key, seasons=seasons, user=current_user, adminz=adminz)




##########################################
##########  SEASON PLAYERS  ##############
##########################################

@views.route('/season/<season>/season-players')
@login_required
@roles_required('Admin','Manager','Player')
# @roles_required('Admin')
def season_players(season):
    seas = Season.query.get(season)
    # seasons = Season.query.all()
    users = User.query.all()
    manager = db.session.query(Season.user_id).filter(Season.user_id==current_user.id).filter(Season.id==season).first()

    rounds = db.session.query(Season, Round).filter(Groupz.season_id==Season.id).filter(Groupz.round_id==Round.id).filter(User.id==user_group.c.user_id).filter(user_group.c.groupz_id==Groupz.id).filter(Season.id==season).order_by(Groupz.round_id.desc()).all()
    if manager or current_user.id==21:
        return render_template('users/season_players.html', vapid_public_key=vapid_public_key, manager=manager, seas=seas, seasons=rounds, season=season, users=users, user=current_user)
    else:
        flash('You don`t have permission!', 'error')
        return redirect(url_for('auth.login'))


@views.route('/season/<season>/get_user_seasons', methods=['GET'])
@login_required
@roles_required('Admin', 'Manager')
def get_user_seasons(season):
    # Dotaz na získanie potrebných údajov, vrátane stĺpca move
    results = db.session.query(
        user_season.c.user_id,
        user_season.c.season_id,
        User.first_name,
        user_season.c.orderz,
        Season.no_group,
        user_season.c.move  # Pridanie stĺpca move do dotazu
    ).join(
        Season, Season.id == user_season.c.season_id
    ).join(
        User, User.id == user_season.c.user_id
    ).filter(
        user_season.c.season_id == season
    ).order_by(
        user_season.c.orderz.asc()
    ).all()

    # Konvertovanie výsledkov na zoznam slovníkov vrátane move
    user_seasons_list = [
        {
            "user_id": row[0],
            "season_id": row[1],
            "first_name": row[2],  # Opravené meno stĺpca
            "orderz": row[3],
            "no_group": row[4],
            "move": row[5]  # Pridanie stĺpca move do výstupu
        } 
        for row in results
    ]
    
    return jsonify(user_seasons_list)


@views.route('/season/update_move', methods=['POST'])
@login_required
@roles_required('Admin', 'Manager', 'Player')
def update_move():
    # Retrieve data from the request
    data = request.json
    user_id = data.get('user_id')
    season_id = data.get('season_id')
    move_value = data.get('move')

    # Ensure all required fields are provided
    if user_id is None or season_id is None or move_value is None:
        return jsonify({'error': 'Invalid data provided'}), 400

    # Update the 'move' column in the 'user_season' table
    stmt = (user_season.update()
            .where(user_season.c.user_id == user_id)
            .where(user_season.c.season_id == season_id)
            .values(move=move_value))

    try:
        db.session.execute(stmt)
        db.session.commit()
        return jsonify({'message': 'Move updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
    
    
@views.route('/season/update_order', methods=['POST'])
@login_required
@roles_required('Admin', 'Manager', 'Player')
def update_order():
    data = request.json

    # Najprv načítame všetky záznamy pre túto sezónu, zoradené podľa `orderz`
    season_id = data[0]['season_id'] if data else None
    if not season_id:
        return jsonify({'error': 'Season ID missing'}), 400

    # Načítanie všetkých hráčov v danej sezóne podľa `orderz`
    results = db.session.execute(
        user_season.select().where(user_season.c.season_id == season_id).order_by(user_season.c.orderz)
    ).fetchall()

    # Vytvoríme mapu pre {orderz: move}
    order_to_move_map = {row[3]: row[4] for row in results}  # Index 3 pre `orderz`, index 4 pre `move`

    # Prechádzame každú položku a aktualizujeme poradie (orderz)
    for item in data:
        new_orderz = item['orderz'] + 1  # Pridáme 1, ak je potrebné, inak ponecháme pôvodnú hodnotu
        old_orderz = item['orderz']

        # Tu presúvame hráča, ale hodnota `move` zostane na pôvodnom mieste (orderz)
        # Ak je nová pozícia, nech sa zmení len `orderz`, ale `move` zostane pôvodné pre dané poradie
        new_move_value = order_to_move_map.get(new_orderz, 0)  # Získame move hodnotu pre novú pozíciu
        old_move_value = order_to_move_map.get(old_orderz, 0)  # Získame move hodnotu pre starú pozíciu

        # Priraď pôvodnú hodnotu `move` tam, kde má byť
        # Staré poradie dostane nového hráča, ale staré `move` musí zostať na pozícii
        stmt_new = (user_season.update()
                    .where(user_season.c.user_id == item['user_id'])
                    .where(user_season.c.season_id == season_id)
                    .values(orderz=new_orderz, move=new_move_value))  # Update new orderz and preserve move
        db.session.execute(stmt_new)

        # Zachovaj pôvodnú hodnotu `move` pre túto pozíciu
        stmt_old = (user_season.update()
                    .where(user_season.c.orderz == old_orderz)
                    .where(user_season.c.season_id == season_id)
                    .values(move=old_move_value))  # Preserve move on the old orderz
        db.session.execute(stmt_old)

    db.session.commit()
    return jsonify({'message': 'Order and move updated successfully'}), 200




    
@views.route('/season/add_row', methods=['POST'])
@login_required
@roles_required('Admin','Manager','Player')
# @roles_required('Admin')
def add_row():
    # Logic to add a new row
    data = request.json
    stmt = user_season.insert().values(
        user_id=data['user_id'],
        season_id=data['season_id'],
        season_first_date=data.get('season_first_date', None),  # This will use default if not provided
        orderz=data.get('orderz', None)
    )
    db.session.execute(stmt)
    db.session.commit()
    return jsonify({'message': 'Row added'}), 200


@views.route('/season/<int:season>/search_users', methods=['POST'])
@login_required
@roles_required('Admin','Manager')
# @roles_required('Admin')
def search_users(season):
    try:
        query = request.json.get('query', '')
   
        allready_added = db.session.query(user_season.c.user_id).filter(user_season.c.season_id==season).all()
        flat_list = [item[0] for item in allready_added]
        users = User.query.filter(User.first_name.ilike(f'%{query}%')).filter(User.id.notin_(flat_list)).filter(User.stripe_subscription_id!="").all()
        # print(users)
        users_data = [{'id': user.id, 'first_name': user.first_name} for user in users]
        return jsonify(users_data)
    except Exception as e:
        return jsonify({"error": "An error occurred"}), 500


@views.route('/season/add_user_to_season', methods=['POST'])
@login_required
@roles_required('Admin','Manager')
def add_user_to_season():
    try:
        data = request.json
        user_id = data['user_id']
        season_id = data['season_id']

        user = User.query.get(user_id)
        season = Season.query.get(season_id)
        
        max_orderz = db.session.query(func.max(user_season.c.orderz)).filter(user_season.c.season_id == season_id).scalar()

        # Ak je max_orderz None (žiadne záznamy), nastavte ho na 1, inak inkrementujte o 1
        if max_orderz is None:
            max_orderz = 1
        else:
            max_orderz += 1

        if user and season:
            # Vložte nový záznam do tabuľky 'user_season' s nastavenou hodnotou 'orderz'
            db.session.execute(user_season.insert().values(
                user_id=user_id,
                season_id=season_id,
                orderz=max_orderz
            ))
            db.session.commit()
            return jsonify({"message": "User added to season successfully"})
        else:
            return jsonify({"error": "User or season not found"}), 404

    except Exception as e:
        # Vrátte detailnú správu o chybe pre účely diagnostiky
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



@views.route('/season/delete_row', methods=['POST'])
@login_required
@roles_required('Admin','Manager','Player')
# @roles_required('Admin')
def delete_row():
    # Logic to delete a row
    data = request.json
    stmt = user_season.delete().where(user_season.c.user_id == data['user_id'])\
                               .where(user_season.c.season_id == data['season_id'])
    db.session.execute(stmt)
    db.session.commit()
    return jsonify({'message': 'Row deleted'}), 200




@views.route('/season/<int:season>/update-round/<int:round>', methods=['POST', 'GET'])
@login_required
@roles_required('Admin','Manager')
# @roles_required('Admin')
def update_round(season,round):
    duelCheck = json.loads(request.data)
    data = duelCheck["duelCheck"]
    data = data.split(",")
    data = (data[0], data[1], data[2])
    # print(data)

    round = Round.query.get(round)
    boolean_value = False if data[0].lower() == 'false' else True
    round.open = boolean_value
    db.session.commit()
    return jsonify({})




@views.route("/season/<int:season>/update", methods=['GET', 'POST'])
@login_required
# @roles_required('Admin')
@roles_required('Admin','Manager')
def update_season(season):
    season = Season.query.get(season)
   
    form = NewSeason()
    user_places = Place.query.filter_by(user_id=current_user.id).all()
    form.place_id.choices = [(place.id, place.name) for place in Place.query.filter_by(user_id=current_user.id).all()]
    # form.place_id.choices = [(place.id, place.name) for place in user_places]
    if request.method == "POST" and not form.validate_on_submit():
        flash(f"you must fill in required fields", 'error')  # Toto vám ukáže chyby v konzole, ak nejaké existujú
    if form.validate_on_submit():
        season.name = form.name.data
        season.min_players = form.min_players.data
        # season.no_round = form.no_round.data
        season.no_group = form.no_group.data
        season.winner_points = form.winner_points.data
        season.season_from = form.season_from.data
        season.open = form.open.data
        season.visible = form.visible.data
        season.place_id = form.place_id.data
        season.duration = form.duration.data

        
        db.session.commit()

        
        flash('Your Season have been updated!', 'success')
        return redirect(url_for('views.season_manager', season=season.id))
    
    elif request.method == 'GET':
        form.name.data = season.name
        form.min_players.data = season.min_players
        # form.no_round.data = season.no_round
        form.no_group.data = season.no_group
        form.winner_points.data = season.winner_points
        form.season_from.data = season.season_from
        form.open.data = season.open
        form.visible.data = season.visible
        form.place_id.data = season.place_id
        form.duration.data = season.duration

        
    return render_template("season_create.html", vapid_public_key=vapid_public_key, head='edit-season', title='Update Season', season=season.id, seas=season, form=form, user=current_user, adminz=adminz, user_places=user_places)


@views.route("/tournament/<int:season>/update", methods=['GET', 'POST'])
@login_required
# @roles_required('Admin')
@roles_required('Admin','Manager')
def update_tournament(season):
    season = Season.query.get(season)
   
    form = NewTournament()
    user_places = Place.query.filter_by(user_id=current_user.id).all()

    # form.place_id.choices = [(place.id, place.name) for place in Place.query.all()]
    form.place_id.choices = [(place.id, place.name) for place in user_places]
    if request.method == "POST" and not form.validate_on_submit():
        flash(f"you must fill in required fields", 'error')  # Toto vám ukáže chyby v konzole, ak nejaké existujú
    if form.validate_on_submit():
        season.name = form.name.data
        season.min_players = form.min_players.data
        # season.no_round = form.no_round.data
        # season.no_group = form.no_group.data
        # season.winner_points = form.winner_points.data
        season.season_from = form.season_from.data
        season.open = form.open.data
        season.visible = form.visible.data
        season.place_id = form.place_id.data
        
        db.session.commit()

        
        flash('Your Tournament have been updated!', 'success')
        return redirect(url_for('views.season_manager', season=season.id))
    
    elif request.method == 'GET':
        form.name.data = season.name
        form.min_players.data = season.min_players
        # form.no_round.data = season.no_round
        # form.no_group.data = season.no_group
        # form.winner_points.data = season.winner_points
        form.season_from.data = season.season_from
        form.open.data = season.open
        form.visible.data = season.visible
        form.place_id.data = season.place_id
        
    return render_template("tournament_create.html", vapid_public_key=vapid_public_key, head='edit-tournament', title='Update Tournament', season=season, seas=season, form=form, user=current_user, adminz=adminz,user_places=user_places)



# @views.route("/place/<int:place>/update", methods=['GET', 'POST'])
# @login_required
# @roles_required('Admin','Manager')
# def update_place(place):
#     # season = Season.query.get(season)
   
#     form = NewPlace()
    
#     if form.validate_on_submit():
#         season.name = form.name.data
#         season.min_players = form.min_players.data
#         # season.no_round = form.no_round.data
#         # season.no_group = form.no_group.data
#         # season.winner_points = form.winner_points.data
#         season.season_from = form.season_from.data
#         season.open = form.open.data
#         season.visible = form.visible.data
        
#         db.session.commit()

        
#         flash('Your Tournament have been updated!', 'success')
#         return redirect(url_for('views.season_manager', season=season.id))
    
#     elif request.method == 'GET':
#         form.name.data = season.name
#         form.min_players.data = season.min_players
#         # form.no_round.data = season.no_round
#         # form.no_group.data = season.no_group
#         # form.winner_points.data = season.winner_points
#         form.season_from.data = season.season_from
#         form.open.data = season.open
#         form.visible.data = season.visible

        
#     return render_template("place_create.html", head='edit-tournament', title='Update Tournament', season=season, seas=season, form=form, user=current_user, adminz=adminz)




@views.route('/season/<season>', methods=['GET', 'POST'])
@login_required
@roles_required('Admin','Player','Manager')
def season_manager(season):
    

    season_type = db.session.query(Season).filter(Season.id==season).first()
    if season_type:
        if season_type.season_type==1:
            season_type_name='Season'
        if season_type.season_type==2:
            season_type_name='Tournament'
    else:
        return redirect(url_for('views.index'))

    # user_email = session.get('user_email')
    # user_id = session.get('user_id')
    # user_name = session.get('user_name')

    # dict_log = {
    #     'id': user_id, 
    #     'first_name': user_name, 
    #     'email': user_email,
    # }
    # rounds = db.session.query(Season, Round).filter(Groupz.season_id==Season.id).filter(Groupz.round_id==Round.id).filter(User.id==user_group.c.user_id).filter(user_group.c.groupz_id==Groupz.id).filter(Season.id==season).order_by(Groupz.round_id.desc()).all()

    rounds = db.session.query(Season, Round).filter(Groupz.season_id==Season.id).filter(Groupz.round_id==Round.id).filter(Season.id==season).order_by(Groupz.round_id.desc()).all()
    rounds_open = db.session.query(Round).join(Season, Season.id==Round.season_id).filter(Season.id==season).filter(Round.open==True).all()
    groupz = db.session.query(Groupz.round_id).all()

    
    
    dic = dictionary.dic
    
    

    
    if request.method == "POST" and request.form.get('add_player_to_season'):
        
        player_join_season = User.query.get(current_user.id)
        season = Season.query.get(season)
        max_orderz = db.session.query(func.max(user_season.c.orderz)).filter(user_season.c.season_id==season.id).scalar()

        # Ak je max_orderz None (žiadne záznamy), nastavte ho na 1, inak inkrementujte o 1
        if max_orderz is None:
            max_orderz = 1
        else:
            max_orderz += 1
        if player_join_season and season:
            # Vložte nový záznam do tabuľky 'user_season' s nastavenou hodnotou 'orderz'
            db.session.execute(user_season.insert().values(
                user_id=player_join_season.id,
                season_id=season.id,
                orderz=max_orderz
            ))
            db.session.commit()
            flash('You have entered the tournament', category='success')
            
        # player_join_season.seasony.append(season)
        # db.session.commit()
        
        return redirect(url_for('views.season_manager', season=season.id))



    if request.method == "POST" and request.form.get('season_delete'):
        
        return redirect(url_for('views.season_delete', season=request.form.get('season_delete')))


    if request.method == "POST" and request.form.get('ide_season'):
        season1 = int(request.form.get('ide_season'))
        
        if season1 < 1:
            flash('There is a problem!', category='error')
        else:
            # Načítanie emailov pre sezónu
            emailz = db.session.query(User.email).join(user_season, user_season.c.user_id == User.id).filter(user_season.c.season_id == season1).all()
            
            # Konverzia výsledku dotazu na zoznam e-mailov
            email_list = [email[0] for email in emailz]
            
            # Určenie typu sezóny (pridajte logiku na načítanie správneho 'season_type')
            season_type = db.session.query(Season).filter_by(id=season1).first()

            if season_type is None:
                flash('Invalid season type!', category='error')
                return redirect(url_for('views.season_manager', season=season1))
            
            # Vytvorenie sezóny alebo generovanie turnajovej štruktúry
            if season_type.season_type == 1:
                print("Creating new season...")
                create_new_season(season1)
            elif season_type.season_type == 2:
                print("Generating tournament structure...")
                generate_tournament_structure(season1)

            flash('New round was created!!!', category='success')

            # Odoslanie e-mailu pre všetkých používateľov naraz
            if email_list:
                send_new_round_email(email_list, "New Round Notification", season1)
            else:
                flash('No users found for this season!', category='warning')

            return redirect(url_for('views.season_manager', season=season1))


    if request.method == "POST" and request.form.get('round'):
        season1 = int(request.form.get('season'))
        round = int(request.form.get('round'))
        # print(round)
        # print('---------------')

        if not season:
            flash('There is a problem!', category='error')
        else:
            grno=db.session.query(Groupz.id).filter(Groupz.season_id==season1).filter(Groupz.round_id==round).first()
            return redirect(url_for('views.duel_view', round=round, group=grno[0], season=season1))
    seas = Season.query.get(season)
    players = db.session.query(user_season).filter(user_season.c.season_id==season).all()
    sesd = len(players)
    # print(sesd)
    players_wait = db.session.query(User).filter(User.seasony).filter(Season.id==season).all()
    now = datetime.datetime.now()
    if now.month == 12:
        next_month = datetime.datetime(now.year + 1, 1, 1)
    else:
        next_month = datetime.datetime(now.year, now.month + 1, 1)

    last_day = next_month - datetime.timedelta(days=1)
    # last_day = datetime.datetime(now.year, now.month + 1, 1) - datetime.timedelta(days=1)
    manager = db.session.query(Season.user_id).filter(Season.user_id==current_user.id).filter(Season.id==season).first()
    order = db.session.query(Order.produc_id, Order.stripe_subscription_id == current_user.stripe_subscription_id).first()
    products = Product.query.filter(Product.is_visible==True).order_by(Product.id.asc()).all()
    orders = Order.query.filter(Order.user_id==current_user.id).filter(Order.stripe_subscription_id==current_user.stripe_subscription_id).all()
    # print(order)
    round_end_data = db.session.query(Round).filter(Round.open == True, Round.season_id == season).first()

    if round_end_data and round_end_data.duration:
        # Povedzme, že máš 'round_start' ako počiatočný dátum kola
        round_start = round_end_data.round_start  # Použitie správneho importu
        duration_seconds = round_end_data.duration  # Predpokladajme, že duration je v sekundách
        round_end = round_start + timedelta(seconds=duration_seconds)

        # Formátovanie do podoby '%Y-%m-%d %H:%M:%S'
        # start_date = round_end_data.round_start
        end_date = round_end.strftime('%Y-%m-%d %H:%M:%S')
        print("Round ends on:", end_date)
    else:
        print("No round data found.")
        end_date = False
        round_start = False

    # print(round_end[0])
    
    # print(last_day.strftime('%Y-%m-%d %H:%M:%S'))
    # end_date=last_day.strftime('%Y-%m-%d %H:%M:%S')
    season_author = db.session.query(User.first_name).join(Season).filter(Season.user_id == User.id).filter(Season.id==season).first()
    return render_template("season.html", start_date=round_start, vapid_public_key=vapid_public_key, season_author=season_author,season_type=season_type.season_type, season_type_name=season_type_name,products=products, orders=orders, order=order, rounds_open=rounds_open, manager=manager, end_date=end_date, players_wait=players_wait, players=players, seas=seas, groupz=groupz, dic=dic, season=season, seasons=rounds, user=current_user, adminz=adminz)





def create_new_season(season):

    # my_list_of_ids = [16, 17, 18, 19, 20]
    # players = User.query.filter(User.id.in_(my_list_of_ids)).all()

    # players = db.session.query(User)\
    #     .join(User.seasony)\
    #     .filter(Season.id.like(season))\
    #     .order_by(User.groupy.order.asc())\
    #     .all()

    # connection = sqlite3.connect('instance/database.db')
    # cursor = connection.cursor()
    # cursor.execute('''
    # SELECT user.id FROM user
    # JOIN user_season ON user.id = user_season.user_id
    # WHERE user_season.season_id = '1' ORDER BY user_season.orderz ASC
    # ''')
    # players = cursor.fetchall()
    # connection.commit()
    # connection.close()

    settings = db.session.query(Season).filter(Season.id==season).first()
    players = db.session.query(User)\
        .join(user_season)\
        .filter(User.id==user_season.c.user_id)\
        .filter(user_season.c.season_id==season)\
        .order_by(user_season.c.orderz.asc())\
        .group_by(User.id, user_season.c.user_id, user_season.c.orderz)\
        .all()

    # print(len(players))
    # print(settings.id)
    # players = tabz.show_table_all()

    def divide_to_groups(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    # n = int(len(players) / settings.no_group)
    groups = list(divide_to_groups(players, settings.no_group))
    # print('--------***-----')
    # print(groups)
    # print('--------***----------')
    user_seasons2 = db.session.execute(
        user_season.select().where(user_season.c.season_id == season).order_by(user_season.c.orderz.asc())
    ).fetchall()

    # 2. Generovanie pravidiel pre postup a vypadnutie
    rules = []
    for user_season2 in user_seasons2:
        if user_season2.move == 1:  # Postup
            rules.append(f"{user_season2.orderz}:1")  # orderz je miesto v sezóne, 1 znamená postup
        elif user_season2.move == 2:  # Vypadnutie
            rules.append(f"{user_season2.orderz}:2")  # orderz je miesto v sezóne, 2 znamená vypadnutie
        else:
            rules.append(f"{user_season2.orderz}:0")  # 0 znamená žiadna zmena

    # 3. Zlúčenie pravidiel do jedného reťazca v tvare '1:0,2:0,3:2,...'
    rules_str = ','.join(rules)



    list_groups_shorts = ['A', 'B1', 'B2', 'C1', 'C2', 'C3', 'C4']
    last_round = db.session.query(Round).filter(Round.season_id==season).order_by(Round.id.desc()).first()
    new_round = Round(season_id=season, open=True, duration=settings.duration, rules=rules_str)
    
    db.session.add(new_round)
    db.session.commit()

    for i, group in enumerate(groups):
        gr = Groupz(
            name=f'Group {i+1}', shorts=list_groups_shorts[i], season_id=season, round_id=new_round.id)
        db.session.add(gr)
        db.session.commit()

        for player in group:
            player = User.query.get(player.id)
            group_new = Groupz.query.get(gr.id)
            player.groupy.append(group_new)

        group = random.sample(group, len(group))

        to_duels = list(combinations(group, 2))
        couples2 = []
        for lists in to_duels:

            # new_duel = Duel(notice=f'{new_round.id}. kolo', date_duel=datetime.now(), season_id=season, round_id=new_round.id)
            new_duel = Duel(notice=f'{new_round.id}. kolo', date_duel=dt.now(), season_id=season, round_id=new_round.id,groupz_id=gr.id)

            db.session.add(new_duel)
            db.session.commit()

            couples = []
            for combo in lists:
                couples.append(new_duel.id)
                couples.append(combo.id)

            couples2.append(couples)

            for co_player in lists:
                duel = Duel.query.get(new_duel.id)
                player = User.query.get(co_player.id)
                player.play.append(duel)
                db.session.commit()
    
    open_season = Season.query.get(season)
    open_season.open = True

    db.session.commit()
    

    
    
#################### FIRE BASE ###########################
user_tokens = {}
@views.route('/register_token', methods=['POST'])
def register_token():
    print("ssssssssssssssssssssssssssssssssssssssssssssssssssss")
    print("ssssssssssssssssssssssssssssssssssssssssssssssssssss")
    print("ssssssssssssssssssssssssssssssssssssssssssssssssssss")
    """API na registráciu FCM tokenu pre používateľa."""
    data = request.json
    user_id = data.get('user_id')
    token = data.get('token')

    # Uložte token pre používateľa
    user_tokens[user_id] = token
    return jsonify({"message": "Token uložený"}), 200

@views.route('/send_notification', methods=['POST'])
def send_notification():
    """API na odoslanie push notifikácie."""
    data = request.json
    user_id = data.get('user_id')
    title = data.get('title')
    body = data.get('body')

    # Získanie tokenu používateľa
    token = user_tokens.get(user_id)
    
    if token:
        # Odoslanie notifikácie
        send_push_notification(token, title, body)
        return jsonify({"message": "Notifikácia odoslaná"}), 200
    else:
        return jsonify({"error": "Používateľ nemá registrovaný token"}), 404








class NewSeason(FlaskForm):
    name = StringField('Season name', validators=[DataRequired()])
    min_players = IntegerField('Min Players in Season', validators=[
            DataRequired(), 
            NumberRange(min=2, max=40, message="Please enter a whole number between 2 and 40."), is_integer
        ])    
    # no_round = IntegerField('Rounds (min 1 - max 10)', validators=[DataRequired(), NumberRange(min=1, max=10, message="blah")])
    no_group = IntegerField('Players in group (2 - 20)', validators=[DataRequired(), NumberRange(min=2, max=20, message="blah")])
    winner_points = IntegerField('Points for win (1 - 5)', validators=[DataRequired(), NumberRange(min=1, max=5, message="blah")])
    season_from = DateTimeLocalField('Break Point')
    season_end_round = DateTimeLocalField('Break Point')
    # season_to = DateTimeLocalField('Break Point')
    open = BooleanField('Open')
    visible = BooleanField('Visible')
    place_id = SelectField('Select Place', choices=[], coerce=int, validators=[DataRequired()])  # Definujte pole place_id s výberom
    duration = IntegerField('Duration (in days)', validators=[DataRequired(), NumberRange(min=1, max=365)])
    submit = SubmitField()


# class NewTournament(FlaskForm):
#     name = StringField('Tournament name', validators=[DataRequired()])
#     min_players = IntegerField('Players in Tournament', validators=[
#             DataRequired(), 
#             is_power_of_two, is_integer
#         ])         
#     # no_round = IntegerField('Rounds (min 1 - max 10)', validators=[DataRequired(), NumberRange(min=1, max=10, message="blah")])
#     # no_group = IntegerField('Players in group (2 - 20)', validators=[DataRequired(), NumberRange(min=2, max=20, message="blah")])
#     # winner_points = IntegerField('Points for win (1 - 5)', validators=[DataRequired(), NumberRange(min=1, max=5, message="blah")])
#     season_from = DateTimeLocalField('Break Point')
#     # season_to = DateTimeLocalField('Break Point')
#     open = BooleanField('Open')
#     visible = BooleanField('Visible')
#     place_id = SelectField('Select Place', choices=[], coerce=int, validators=[DataRequired()])  # Definujte pole place_id s výberom
#     submit = SubmitField()


class NewTournament(FlaskForm):
    name = StringField('Tournament name', validators=[DataRequired()])
    # Zmena min_players z IntegerField na SelectField pre dynamický výber
    min_players = SelectField('Players in Tournament', choices=[(2, '2'), (4, '4'), (8, '8'), (16, '16'), (32, '32'), (64, '64')], coerce=int, validators=[DataRequired()])
    season_from = DateTimeLocalField('Break Point', format='%Y-%m-%dT%H:%M')
    open = BooleanField('Open')
    visible = BooleanField('Visible')
    place_id = SelectField('Select Place', choices=[], coerce=int, validators=[DataRequired()])
    submit = SubmitField('Create Tournament')


class NewPlace(FlaskForm):
    # Basic Place Information
    name = StringField('Place Name', validators=[DataRequired(), Length(max=300)])
    address_street = StringField('Street Address', validators=[DataRequired(), Length(max=300)])
    # address_street_no = StringField('Street Number', validators=[Optional(), Length(max=50)])
    # address_street_zip = StringField('ZIP Code', validators=[Optional(), Length(max=20)])
    # address_street_city = StringField('City', validators=[Optional(), Length(max=100)])
    # address_street_state = StringField('State', validators=[Optional(), Length(max=100)])

    # Contact Information
    phone_number = StringField('Phone Number', validators=[Optional(), Length(max=20)])

    # Coordinates (could be latitude/longitude or a specific format)
    coordinates = StringField('Coordinates', validators=[Optional(), Length(max=100)])

    submit = SubmitField('Submit')
    
    
