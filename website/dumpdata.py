from sqlalchemy import create_engine, select
from models import User

engine_lite = create_engine('sqlite:///mydb.sqlite')
engine_cloud = create_engine('postgresql+psycopg2://USER:PW@/DBNAME?host=/cloudsql/INSTANCE')

with engine_lite.connect() as conn_lite:
    with engine_cloud.connect() as conn_cloud:
        for table in User.metadata.sorted_tables:
            data = [dict(row) for row in conn_lite.execute(select(table.c))]
            conn_cloud.execute(table.insert().values(data))



# heroku pg:backups restore `heroku pg:backups postgresql://sfljcgpqzpdtgy:e7cf417bcda516a158e6573deeef539aa5a8c641024736ae0dcad733e4116a82@ec2-54-173-77-184.compute-1.amazonaws.com:5432/d7lne9amqh2iri -a darts` database.sql --app website --confirm website