from fastapi import FastAPI
import mysql.connector as myconn
from mysql.connector import Error
import pandas as pd
from prophet import Prophet


app = FastAPI(title="Projecto grupal Migration AId")


# app.include_router(user)


# user= APIRouter()


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


    
@app.get("country: str}{year: int}") 
async def predict_net_migration(country: str, year: str):
                
    co = myconn.connect(host="migrationaid.csjeonbxjstv.us-east-1.rds.amazonaws.com",
                            database="FlujoMigratorio",
                            user="admin",
                            password="Aylinv94.")
    
    try:

        if co.is_connected():                                    
            cursor = co.cursor()

            def predict_net_migration(country, future_year):
                # cargar el archivo csv y convertir las comas en puntos en la columna "net_migration"
                df = pd.read_csv('countries_net_migration.csv')
                df.loc[:, 'net_migration_1990':'net_migration_2020'] = df.loc[:, 'net_migration_1990':'net_migration_2020'].astype(str).apply(lambda x: x.str.replace(',', '.')).astype(float)

                # pivoteando el dataframe
                df = pd.melt(df, id_vars=['country_name', 'country_code'], var_name='year', value_name='net_migration')
                df_country = df[df['country_name'] == country].reset_index(drop=True)
                df_country['year'] = df_country['year'].str.split('_').str[-1]

                # convirtiendo las fechas a datetime
                df_country['year'] = pd.to_datetime(df_country['year'], format='%Y')

                # creando el dataframe para Prophet
                df_country_prophet = pd.DataFrame({'ds': df_country['year'], 'y': df_country['net_migration']})

                # entrenando el modelo Prophet
                model = Prophet()
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
    except Error as ex:
        return "Error durante la conección:", ex
    finally:
        if co.is_connected():
           co.close()

