from flask import Blueprint, render_template, request, jsonify, flash, jsonify, redirect, url_for, session, current_app
from flask_login import login_required, current_user
from flask_security import roles_required
import os
from dotenv import load_dotenv
load_dotenv()
from .models import Note, User, Duel, Season, Groupz, Round, Product, Order, user_duel, user_group, user_season, PaymentCard
from . import db
import json
from sqlalchemy import func, or_
from sqlalchemy import insert, update

from . import tabz, duels, dictionary, mysql
from datetime import datetime
from itertools import combinations
from sqlalchemy.inspection import inspect
from flask_sqlalchemy import SQLAlchemy

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
import psycopg2
import email
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, SelectMultipleField, IntegerField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, StopValidation,NumberRange
from wtforms import DateField, DateTimeField, DateTimeLocalField, Form
from psycopg2.errorcodes import UNIQUE_VIOLATION
from psycopg2 import errors
import datetime
from datetime import datetime as dt
from math import ceil, log2, log
from functools import wraps

from sqlalchemy.exc import IntegrityError  # Importujte pre zachytávanie chýb pri vkladaní do databázy

def roles_required(*roles):
    """Dekorátor, ktorý kontroluje, či má používateľ aspoň jednu z požadovaných rolí."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                # Ak používateľ nie je prihlásený, presmeruje ho na prihlasovaciu stránku
                flash("You need to be logged in to access this page.", "warning")
                return redirect(url_for('auth.login'))
            
            # Skontroluje, či má používateľ aspoň jednu z požadovaných rolí
            if not any(role.name in roles for role in current_user.roles):
                flash("You do not have permission to access this page.", "danger")
                return redirect(url_for('views.index'))

            # Ak má používateľ povolenie, vykoná funkciu
            return f(*args, **kwargs)
        return decorated_function
    return decorator
        
views = Blueprint('views', __name__)

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

@views.route('/', methods=['GET', 'POST'])
# @login_required
def index():
    if not current_user.is_authenticated:
        # Ak nie je používateľ prihlásený, presmerujte ho na prihlasovaciu stránku
        return redirect(url_for('auth.login'))

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
    
    if request.method == "POST" and request.form.get('tournament_add'):
        
        print(request.form.get('tournament_add'))
        return redirect(url_for('views.tournament_new'))
       
        
    if request.method == "POST" and request.form.get('season_add'):
        
        # print(request.form.get('season_add'))
        return redirect(url_for('views.season_new'))

    
    

    if request.method == "POST" and request.form.get('season_id_button'):
        season1 = request.form.get('season_id')

        return redirect(url_for('views.home', season=season1))
    
    
    
    return render_template("index.html", seasons=seasons, user=current_user, adminz=adminz)
    

@views.route('/home/<season>/', methods=['GET', 'POST'])
@login_required
def home(season):


    groups = db.session.query(Groupz).join(
        Season).filter(Season.id == season).all()
    round = db.session.query(Groupz.round_id).filter(Groupz.season_id==season).order_by(Groupz.round_id.desc()).first()
    print(round)
    if round is not None:
        user_group = db.session.query(Groupz).join(User.groupy).filter(User.id == current_user.id).filter(Groupz.season_id == Season.id).filter(Season.id == season).filter(Groupz.round_id == round[0]).first()
    
    # myduels_user = db.session.query(Groupz.id).join(User.groupy).filter(Groupz.season_id == Season.id).filter(
    #     Season.id == season).filter(User.id.in_([current_user.id])).filter(Groupz.round_id == round[0]).all()

        players = User.query.all()
        data_show_table = tabz.show_table(season, round, round[0])
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


    return render_template("home.html", round=round, seas = seas, season=season, user_group=user_group, groups=groups, dataAll=data_all, players=players, data_name_tabz=data_name_tabz, data_show_table=data_show_table, user=current_user, adminz=adminz)


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
    print("aaaaaaaaaaaaaaaaaaaaaa")
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
            print(f"POMOOOOC - {duel.groupz_id}")
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








@views.route('/update-duel2', methods=['POST', 'GET'])
@login_required
@roles_required('Admin','Manager','Player')
# @roles_required('Admin','Manager','Player')
def update_duel2():
    try:
        duelResult = json.loads(request.data)
        data = duelResult["duelResult"]
        print(data)
        data = data.split(",")
        duel = Duel.query.get(int(data[1]))
        season = Season.query.filter_by(id=duel.season_id).first()
        # calculating points
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
                    
                
                new_user = User.query.get(winner_user_id)
                if winner_user_id:
                    new_user_id = new_user.id
                else:
                    new_user_id = None
                    
                user_duel_update = db.session.query(user_duel).filter(user_duel.c.notez==str(duell.id))
                update_expr = user_duel.update().\
                    where(user_duel.c.notez == duel.id).\
                    values(user_id=new_user_id)

                # Vykonanie aktualizačného výrazu
                db.session.execute(update_expr)
                existing_record = db.session.query(user_group).filter(user_group.c.duel_id == duel.id).first()

                if existing_record:
                    # Záznam existuje, skontrolujte, či user_id zodpovedá new_user_id
                    print("SSSSSSSSSSSSSSSSSSSSSSSSSSS")
                    print(new_user_id)
                    print("SSSSSSSSSSSSSSSSSSSSSSSSSSS")
                    
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

    return render_template("duel.html", seas = seas, season=season, group=group, roundz=roundz,  duel=duel, players=duelz, user=current_user, adminz=adminz)




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
        return render_template("duels_filter.html", season_type=seas.season_type, manager=manager, seas_no_r=len(seas_no_r), roundz=roundz, seas = seas, season_obj=season_obj, round=round, groups=groups, season=season, duels=new_ret, user=current_user, adminz=adminz)
    if seas.season_type == 2:
        return render_template("duels_filter2.html", season_type=seas.season_type, manager=manager, seas_no_r=len(seas_no_r), roundz=roundz, seas = seas, season_obj=season_obj, round=round, groups=groups, season=season, duels=new_ret, user=current_user, adminz=adminz)


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


####### NEW TOURNAMENT

@views.route('/tournament/new', methods=['GET', 'POST'])
@login_required
@roles_required('Admin','Manager','Player')
def tournament_new():
    
    form = NewTournament()
    
    players = User.query.all()
   
    if form.validate_on_submit():
        season = db.session.query(Season).filter(Season.name.like(form.name.data)).first()
        season_type = int(request.form.get('season_type'))
    
        ## season_from=form.season_from.data, 
        if not season:
                new_season = Season(name=form.name.data, no_group=1, 
                                    winner_points=3, open=form.open.data, user_id=current_user.id, min_players=form.min_players.data,season_type=season_type)
                db.session.add(new_season)
                db.session.commit()
                return redirect(url_for('views.season_manager', season=new_season.id))
        else:
            flash("Tournament name must be unique.", category="error")


        

    return render_template("tournament_create.html", head='new-tournament', title='Create New Tournament', form=form, players=players, user=current_user, adminz=adminz)


####### NEW SEASON

@views.route('/season/new', methods=['GET', 'POST'])
@login_required
@roles_required('Admin','Manager')
# @roles_required('Admin')
def season_new():
    
    form = NewSeason()
    
    players = User.query.all()
   
    if form.validate_on_submit():
        season = db.session.query(Season).filter(Season.name.like(form.name.data)).first()
        season_type = int(request.form.get('season_type'))
    
        ## season_from=form.season_from.data, 
        if not season:
                new_season = Season(name=form.name.data, no_round=form.no_round.data, no_group=form.no_group.data, 
                                    winner_points=form.winner_points.data, open=form.open.data, user_id=current_user.id, min_players=form.min_players.data,season_type=season_type)
                db.session.add(new_season)
                db.session.commit()
                return redirect(url_for('views.season_manager', season=new_season.id))
        else:
            flash("Season name must be unique.", category="error")


        

    return render_template("season_create.html", head='new-season', title='Create Season', form=form, players=players, user=current_user, adminz=adminz)



@views.route('/season/delete/<season>', methods=['GET', 'POST'])
@login_required
@roles_required('Admin','Manager')
def season_delete(season):
  
    season = Season.query.get(season)
    if season:
        db.session.delete(season)
        db.session.commit()
        flash("Season has been deleted.", category="success")
        seasons = db.session.query(Season).all()
        # seasons = db.session.query(Season).filter(Season.open==True).all()
        return redirect(url_for('views.index', seasons=seasons, user=current_user, adminz=adminz))
    else:
        flash("Season does not exist.", category="error")
        seasons = db.session.query(Season).all()
        return redirect(url_for('views.index', seasons=seasons, user=current_user, adminz=adminz))



@views.route('/season/delete-player/<player>/<season>', methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'Manager', 'Player')
def season_player_delete(player, season):
    response_data = {'status': 'error', 'message': 'An error occurred'}  # Predvolená odpoveď
    if player and season:
        season_obj = Season.query.get(season)
        user = User.query.get(player)
        if season_obj and user:
            user.seasony.remove(season_obj)
            db.session.commit()
            response_data = {'status': 'success', 'message': 'Removed from list'}
        else:
            response_data = {'status': 'error', 'message': 'Season or player not found'}

    return jsonify(response_data)
    



@views.route('/pricing', methods=['GET', 'POST'])
def pricing_list():
    
    
    products = Product.query.filter(Product.is_visible==True).order_by(Product.id.asc()).all()
    orders = Order.query.filter(Order.user_id==current_user.id).all()

    return render_template("pricing.html", orders=orders, products=products, user=current_user, adminz=adminz)


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

    return render_template("season_list.html", seasons=seasons, user=current_user, adminz=adminz)




##########################################
##########  SEASON PLAYERS  ##############
##########################################

@views.route('/season/<season>/season-players')
@login_required
@roles_required('Admin','Manager','Player')
# @roles_required('Admin')
def season_players(season):
    seas = Season.query.get(season)
    seasons = Season.query.all()
    users = User.query.all()
    manager = db.session.query(Season.user_id).filter(Season.user_id==current_user.id).filter(Season.id==season).first()

    rounds = db.session.query(Season, Round).filter(Groupz.season_id==Season.id).filter(Groupz.round_id==Round.id).filter(User.id==user_group.c.user_id).filter(user_group.c.groupz_id==Groupz.id).filter(Season.id==season).order_by(Groupz.round_id.desc()).all()
    if manager or current_user.id==21:
        return render_template('users/season_players.html', manager=manager, seas=seas, seasons=rounds, season=season, seasons2=seasons, users=users, user=current_user)
    else:
        flash('You don`t have permission!', 'error')
        return redirect(url_for('auth.login'))


@views.route('/season/<season>/get_user_seasons', methods=['GET'])
@login_required
@roles_required('Admin','Manager')
# @roles_required('Admin')
def get_user_seasons(season):
    # results = db.session.execute(user_season.select().order_by(user_season.c.orderz.asc())).fetchall()
    results = db.session.query(user_season.c.user_id, user_season.c.season_id, User.first_name, user_season.c.orderz).join(Season, Season.id==user_season.c.season_id).join(User, User.id==user_season.c.user_id).filter(user_season.c.season_id==season).order_by(user_season.c.orderz.asc()).all()

    # Convert rows to list of dictionaries before jsonifying
    user_seasons_list = [{"user_id": row[0], "season_id": row[1], "season_first_date": row[2], "orderz": row[3]} for row in results]
    return jsonify(user_seasons_list)

@views.route('/season/update_order', methods=['POST'])
@login_required
@roles_required('Admin','Manager','Player')
# @roles_required('Admin')
def update_order():
    # Update ordering logic here
    data = request.json
    for item in data:
        stmt = (user_season.update().where(user_season.c.user_id == item['user_id'])
                                    .where(user_season.c.season_id == item['season_id'])
                                    .values(orderz=item['orderz']+1))
        db.session.execute(stmt)
    db.session.commit()
    return jsonify({'message': 'Order updated'}), 200

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
# @roles_required('Admin')
def add_user_to_season():
    try:
        data = request.json
        user_id = data['user_id']
        season_id = data['season_id']

        user = User.query.get(user_id)
        season = Season.query.get(season_id)
        
        max_orderz = db.session.query(func.max(user_season.c.orderz)).filter(user_season.c.season_id==season_id).scalar()

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
        return jsonify({"error": "An error occurred"}), 500


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
    
    if form.validate_on_submit():
        season.name = form.name.data
        season.min_players = form.min_players.data
        season.no_round = form.no_round.data
        season.no_group = form.no_group.data
        season.winner_points = form.winner_points.data
        season.season_from = form.season_from.data
        season.open = form.open.data
        season.visible = form.visible.data
        
        db.session.commit()

        
        flash('Your Season has been updated!', 'success')
        return redirect(url_for('views.season_manager', season=season.id))
    
    elif request.method == 'GET':
        form.name.data = season.name
        form.min_players.data = season.min_players
        form.no_round.data = season.no_round
        form.no_group.data = season.no_group
        form.winner_points.data = season.winner_points
        form.season_from.data = season.season_from
        form.open.data = season.open
        form.visible.data = season.visible

        
    return render_template("season_create.html", head='edit-season', title='Update Season', season=season.id, seas=season, form=form, user=current_user, adminz=adminz)


@views.route("/tournament/<int:season>/update", methods=['GET', 'POST'])
@login_required
# @roles_required('Admin')
@roles_required('Admin','Manager')
def update_tournament(season):
    season = Season.query.get(season)
   
    form = NewTournament()
    
    if form.validate_on_submit():
        season.name = form.name.data
        season.min_players = form.min_players.data
        # season.no_round = form.no_round.data
        # season.no_group = form.no_group.data
        # season.winner_points = form.winner_points.data
        season.season_from = form.season_from.data
        season.open = form.open.data
        season.visible = form.visible.data
        
        db.session.commit()

        
        flash('Your Tournament has been updated!', 'success')
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

        
    return render_template("tournament_create.html", head='edit-tournament', title='Update Tournament', season=season, seas=season, form=form, user=current_user, adminz=adminz)






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
        # print(season1)
        if season1 < 1:
            flash('There is a problem!', category='error')
        else:
            # pass
            # create_new_season(season1)
            print("********************")
            print(season_type.season_type)
            print("********************")
            if season_type.season_type==1:
                create_new_season(season1)
            if season_type.season_type==2:
                generate_tournament_structure(season1)
            flash('New round was created!!!', category='success')
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
    end_date = last_day.strftime('%Y-%m-%d %H:%M:%S')
    
    # print(last_day.strftime('%Y-%m-%d %H:%M:%S'))
    # end_date=last_day.strftime('%Y-%m-%d %H:%M:%S')
    return render_template("season.html", season_type=season_type.season_type, season_type_name=season_type_name,products=products, orders=orders, order=order, rounds_open=rounds_open, manager=manager, end_date=end_date, players_wait=players_wait, players=players, seas=seas, groupz=groupz, dic=dic, season=season, seasons=rounds, user=current_user, adminz=adminz)


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
    print('--------***-----')
    print(groups)
    print('--------***----------')


    list_groups_shorts = ['A', 'B1', 'B2', 'C1', 'C2', 'C3', 'C4']
    last_round = db.session.query(Round).filter(Round.season_id==season).order_by(Round.id.desc()).first()
    new_round = Round(season_id=season, open=True)
    
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









class NewSeason(FlaskForm):
    name = StringField('Season name', validators=[DataRequired()])
    min_players = IntegerField('Min. players in Season', validators=[
            DataRequired(), 
            NumberRange(min=2, max=10, message="Please enter a whole number between 2 and 10."), is_integer
        ])    
    no_round = IntegerField('Rounds (min 1 - max 10)', validators=[DataRequired(), NumberRange(min=1, max=10, message="blah")])
    no_group = IntegerField('Players in group (2 - 20)', validators=[DataRequired(), NumberRange(min=2, max=20, message="blah")])
    winner_points = IntegerField('Points for win (1 - 5)', validators=[DataRequired(), NumberRange(min=1, max=5, message="blah")])
    season_from = DateTimeLocalField('Break Point')
    season_end_round = DateTimeLocalField('Break Point')
    # season_to = DateTimeLocalField('Break Point')
    open = BooleanField('Open')
    visible = BooleanField('Visible')

    submit = SubmitField()


class NewTournament(FlaskForm):
    name = StringField('Tournament name', validators=[DataRequired()])
    min_players = IntegerField('Players in Tournament', validators=[
            DataRequired(), 
            is_power_of_two, is_integer
        ])         
    # no_round = IntegerField('Rounds (min 1 - max 10)', validators=[DataRequired(), NumberRange(min=1, max=10, message="blah")])
    # no_group = IntegerField('Players in group (2 - 20)', validators=[DataRequired(), NumberRange(min=2, max=20, message="blah")])
    # winner_points = IntegerField('Points for win (1 - 5)', validators=[DataRequired(), NumberRange(min=1, max=5, message="blah")])
    season_from = DateTimeLocalField('Break Point')
    # season_to = DateTimeLocalField('Break Point')
    open = BooleanField('Open')
    visible = BooleanField('Visible')

    submit = SubmitField()

