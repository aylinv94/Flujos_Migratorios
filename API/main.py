from fastapi import FastAPI
from fastapi import Depends
import mysql.connector as myconn
from mysql.connector import Error
import pandas as pd
from prophet import Prophet


app = FastAPI(title="Projecto grupal Migration AId")


# app.include_router(user)


# user= APIRouter()
@app.get('/')
async def init():
    return {'Hello:World'}

@app.post("/Bienvenid@ a la API Migration AId")
async def Saludo():
    return {f"Saludos": "Gracias por curiosear aquí"}

'''
 CONSULTAS
-- 1.Migración neta
-- predict_net_migration('país', 2025)
-- país- año
-- argentina- 2025
'''

config = {'host':"migrationaid.csjeonbxjstv.us-east-1.rds.amazonaws.com",
                            'database':"FlujoMigratorio",
                            'user':"admin",
                            'password':"Aylinv94."}

def get_database_connection():
    conn = myconn.connect(**config)
    return conn
    

@app.get('/count_coulumas_{columna}')
async def startup_event(columna:str):
    app.state.connection = get_database_connection()
    cursor = app.state.connection.cursor()
    query = f"SELECT COUNT({columna}) FROM pip"
    cursor.execute(query)
    result = cursor.fetchone()
    return f"La tabla pip tiene {result[0]} registros"
