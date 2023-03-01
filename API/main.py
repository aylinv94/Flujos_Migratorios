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
    

@app.get('/contar_columnas')
async def startup_event(columna:str):
    app.state.connection = get_database_connection()
    cursor = app.state.connection.cursor()
    query = f"SELECT COUNT({columna}) FROM pip"
    cursor.execute(query)
    result = cursor.fetchone()
    return f"La tabla pip tiene {result[0]} registros"

@app.get('/migracion_neta_anual') 
def predict_net_migration(country:str, future_year:int):
    app.state.connection = get_database_connection()
    cursor = app.state.connection.cursor()

    query = 'SELECT * FROM country_net_migration'
    df = pd.read_sql_query(query,app.state.connection)
    
    df_country = df[df['country_name'] == country].reset_index(drop=True)

    # convirtiendo las fechas a datetime
    df_country['year'] = pd.to_datetime(df_country['year'], format='%Y')

    # creando el dataframe para Prophet
    df_country_prophet = pd.DataFrame({'ds': df_country['year'], 'y': df_country['net_migration']})

    # entrenando el modelo Prophet
    model = Prophet(changepoint_prior_scale=0.5, 
    seasonality_mode='multiplicative', 
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=True,
    growth='linear')
    model.fit(df_country_prophet)

    # generando las fechas futuras y realizando la predicción
    start_year = df_country_prophet['ds'].max().year
    if future_year >= start_year:
        future_dates = pd.date_range(start=f'{start_year}-01-01', end=f'{future_year}-12-31', freq='M')
        future = pd.DataFrame({'ds': future_dates})
    else:
        future = pd.DataFrame({'ds': [f'{future_year}-01-01']})
    forecast = model.predict(future)

    # seleccionando la predicción para el año futuro
    if future_year >= start_year:
        pred = forecast[forecast['ds'].dt.year == future_year]['yhat'].values[0]
    else:
        pred = forecast.iloc[0]['yhat']
    return {f'La migración neta es: {pred} para el año {future_year}'}
