# import xlwings
import pandas as pd
import numpy as np
# from openpyxl import Workbook, load_workbook
import itertools
import psycopg2
from itertools import groupby
from .models import Groupz, Season, User, Duel, Round, user_duel, user_group
from . import db
from . import conn
import sqlite3
from sqlalchemy import func, case, and_, or_

virtualplayers = ('h1', 'h2', 'h3', 'h4')

def show_name_table(season, round):
    
    groups = db.session.query(Groupz).filter(Groupz.season_id == Season.id).filter(Season.id == season).filter(Groupz.round_id == round).all()

    # groups = ['A', 'B1', 'B2', 'C1', 'C2']
    # print(groups)
    return groups


########################## SHOW TABLE IN GROUPS
def show_table(season, round):

    valz = []

    # Definovanie agregovaných funkcií s podmienkami
    c_duel = func.sum(case((user_duel.c.checked == 'true', 1), else_=0)).label("c_duel")
    s_points = func.sum(case((user_duel.c.checked == 'true', user_duel.c.points), else_=0)).label("s_points")
    s_result = func.sum(case((user_duel.c.checked == 'true', user_duel.c.result), else_=0)).label("s_result")
    s_against = func.sum(case((user_duel.c.checked == 'true', user_duel.c.against), else_=0)).label("s_against")

    c_wins = func.sum(
        case(
            (
                and_(
                    (user_duel.c.checked == 'true'),
                    (user_duel.c.points == 2)
                ), 1
            ),
            else_=0
        )
    ).label("c_wins")

    c_loses = func.sum(
        case(
            (
                and_(
                    (user_duel.c.checked == 'true'),
                    or_(
                        (user_duel.c.points == 0),
                        (user_duel.c.points == 1)
                    )
                ), 1
            ),
            else_=0
        )
    ).label("c_loses")

    # Dotaz do databázy
    groups = db.session.query(
            user_group.c.groupz_id,
            User.first_name,
            user_duel.c.user_id,
            Duel.id.label('duel_id'),  # Pridáme duel_id pre lepšiu kontrolu
            c_duel,
            s_points,
            s_result,
            s_against,
            c_wins,
            c_loses
        )\
        .select_from(user_duel)\
        .join(User, user_duel.c.user_id == User.id)\
        .join(Duel, user_duel.c.duel_id == Duel.id)\
        .join(user_group, user_group.c.user_id == User.id)\
        .join(Groupz, user_group.c.groupz_id == Groupz.id)\
        .join(Season, Season.id == Duel.season_id)\
        .join(Round, Groupz.round_id == Round.id)\
        .filter(Season.id == season)\
        .filter(Round.id == round)\
        .filter(Duel.round_id == round)\
        .group_by(user_duel.c.user_id, user_group.c.groupz_id, User.first_name, Duel.id)\
        .all()

    # Zoskupenie výsledkov podľa 'groupz_id'
    result = {k: [*map(lambda v: v, values)]
              for k, values in groupby(sorted(groups, key=lambda x: x[0]), lambda x: x[0])
              }

    # Spracovanie každej skupiny do DataFrame
    for group in result.values():

        # Upravíme počet stĺpcov podľa počtu stĺpcov v 'group'
        df = pd.DataFrame(group, columns=['groupz_id', 'player', 'user_id', 'duel_id', 'c_duel', 's_points', 's_result', 's_against', 'c_wins', 'c_loses'])

        # Výpočet a agregácia údajov
        df['plusminus'] = df['s_result'] - df['s_against']
        df = df.groupby(by="player", as_index=False)[["c_duel", "c_wins", "c_loses", "s_points", "s_result", "s_against", "plusminus"]].sum()

        # Zoradenie výsledkov
        df = df.sort_values(['s_points', 's_result', 'plusminus'], ascending=False)

        # Vytvorenie nového stĺpca 'plusminus2'
        df['plusminus2'] = df['s_result'].astype(str) + "/" + df["s_against"].astype(str)

        # Výber konečných stĺpcov pre výstup
        df = df[['player', 'c_duel', 'c_wins', 'c_loses', 'plusminus2', 'plusminus', 's_points']]

        # Konverzia DataFrame na zoznam a pridanie do výstupu
        der = df.values.tolist()
        valz.append([der])

    return valz





########################## SHOW TABLE ALL

def show_table_all(season):
    valz2 = []
    # season = 1
    # group = 1
    c_duel = func.sum(case((user_duel.c.checked == 'true', 1), else_= 0)).label("c_duel")
    s_points = func.sum(case((user_duel.c.checked == 'true', user_duel.c.points), else_= 0)).label("s_points")
    s_result = func.sum(case((user_duel.c.checked == 'true', user_duel.c.result), else_= 0)).label("s_result")
    s_against = func.sum(case((user_duel.c.checked == 'true', user_duel.c.against), else_= 0)).label("s_against")
    # c_wins = func.sum(case((user_duel.c.points == 2, 1), else_= 0)).label("c_wins")
    # c_loses = func.sum(case((user_duel.c.points == 0, 1),(user_duel.c.points == 1, 1), else_=0)).label("c_loses")
    
    c_wins = func.sum(case(
        
            (and_(
                (user_duel.c.checked == 'true'),
                or_(
                    (user_duel.c.points == 2),
                )
            ), 1)
        ,
        else_ = 0
    ))

    c_loses = func.sum(case(
        
            (and_(
                (user_duel.c.checked == 'true'),
                or_(
                    (user_duel.c.points == 0),
                    (user_duel.c.points == 1)
                )
            ), 1)
        ,
        else_ = 0
    ))
    
    
    groups = db.session.query(
        User.first_name,
        user_duel.c.user_id,
        c_duel,
        s_points,
        s_result,
        s_against,
        c_wins,
        c_loses
        )\
        .join(Duel)\
        .join(Round)\
        .filter(user_duel.c.user_id == User.id)\
        .filter(user_duel.c.duel_id == Duel.id)\
        .filter(User.first_name.not_in(virtualplayers))\
        .filter(Season.id == Duel.season_id)\
        .filter(Season.id == season)\
        .group_by(user_duel.c.user_id, User.first_name)\
        .all()

    df2 = pd.DataFrame(groups, columns=['player', 'user_id','c_duel','s_points','s_result','s_against','c_wins','c_loses'])
    # print(df2['shorts'])
    df2 = df2.replace('?', np.NaN)
    df2['plusminus'] = df2['s_result'] - df2['s_against']

    df2 = df2.groupby(["player"], as_index=False)[["c_duel", "c_wins", "c_loses", "s_points", "s_result","s_against","plusminus"]].sum()
    df2 = df2.sort_values(['s_points','s_result','plusminus'], ascending=False)
    # df2.reset_index(drop=True)
    df2['plusminus2'] = df2['s_result'].astype(str) +"/"+ df2["s_against"].astype(str)

    # df2['dfindex'] = df2.index
    # df2.iloc['shorts']
    # df2['shorts0'] = df2['shorts'].iloc[0]
    # df2['shorts'] = df2.set_index('shorts', inplace=False)
    # df2['player_group'] = df2['player'].astype(str) + '(' +  df2['shorts'] + ')'
    df2 = df2[['player', 'c_duel', 'c_wins', 'c_loses', 'plusminus2', 'plusminus', 's_points']]


    # print(df)
    # der = df.to_string(index=False)
    der2 = df2.values.tolist()
    valz2.append([der2])

    # print(valz2)

    return valz2
########################## SHOW TABLE ALL // END



    # SELECT user_group.groupz_id, user.first_name, user_duel.result, user_duel.against, 
    # user_duel.points, user_duel.checked, user.id, checkings.checking AS sss,

    # SUM(CASE WHEN user_duel.checked = "true" AND checkings.checking = 2 THEN user_duel.addons ELSE 0 END) AS c_duel,
    # SUM(CASE WHEN user_duel.checked = "true" THEN user_duel.points ELSE 0 END) AS s_points,
    # SUM(CASE WHEN user_duel.checked = "true" THEN user_duel.result ELSE 0 END) AS s_result,
    # SUM(CASE WHEN user_duel.checked = "true" THEN user_duel.against ELSE 0 END) AS s_against

    # FROM user_duel, (SELECT SUM(CASE WHEN user_duel.duel_id = duel.id THEN 1 ELSE 0 END) AS checking FROM user_duel JOIN duel ON duel.id=user_duel.duel_id WHERE user_duel.checked = "true") AS checkings
    # JOIN duel ON duel.id = user_duel.duel_id 
    # JOIN user ON user_duel.user_id = user.id 
    # JOIN user_group ON user_group.user_id = user.id 
    # JOIN season ON season.id = duel.season_id 
    # WHERE season.id = ?
    # GROUP BY user_group.user_id, user_duel.user_id


    #     SELECT user_group.groupz_id, user.first_name, user_duel.result, user_duel.against, 
    # user_duel.points, user_duel.checked, user.id, checkings.checking AS sss,

    # SUM(CASE WHEN checkings.checking = 2 THEN user_duel.addons ELSE 0 END) AS c_duel,
    # SUM(CASE WHEN user_duel.checked = "true" THEN user_duel.points ELSE 0 END) AS s_points,
    # SUM(CASE WHEN user_duel.checked = "true" THEN user_duel.result ELSE 0 END) AS s_result,
    # SUM(CASE WHEN user_duel.checked = "true" THEN user_duel.against ELSE 0 END) AS s_against

    # FROM user_duel, (SELECT COUNT(CASE WHEN user_duel.checked = "true" THEN 1 ELSE 0 END) AS checking FROM user_duel JOIN duel ON duel.id=user_duel.duel_id WHERE user_duel.duel_id = duel.id) AS checkings
    # JOIN duel ON duel.id = user_duel.duel_id 
    # JOIN user ON user_duel.user_id = user.id 
    # JOIN user_group ON user_group.user_id = user.id 
    # JOIN season ON season.id = duel.season_id 
    # WHERE season.id = ?
    # GROUP BY user_group.user_id, user_duel.user_id