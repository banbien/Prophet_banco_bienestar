import pandas as pd
import numpy as np
import pickle
#from neuralprophet import NeuralProphet  [Si el modelo ya está entrenado y guardado con pickle, no necesitas importar NeuralProphet directamente]

# CARGA DE MODELO
def cargar_modelo(ruta_modelo: str):
    """
    Carga modelo previamente entrenado y guardado.
    """
    with open(ruta_modelo, "rb") as f:
        modelo = pickle.load(f)
    return modelo


# PREPARAR DATA PARA NEURALPROPHET
def preparar_datos_para_modelo(df, cajero_id):
    """
    Filtra y formatea datos para NeuralProphet.
    """
    df_cajero = df[df["cajero"] == cajero_id].copy()

    if df_cajero.empty:
        return None

    df_cajero = df_cajero.rename(
        columns={
            "fecha": "ds",
            "retiro": "y"
        }
    )

    df_cajero = df_cajero[["ds", "y"]].sort_values("ds")

    return df_cajero


# INFERENCIA POR LISTA DE CAJEROS

def inferencia_por_lista(
    lista_cajeros,
    df_historico,
    ruta_modelo,
    horizonte=30
):
    """
    Realiza inferencia automática para cada ATM de la lista.
    """

    modelo = cargar_modelo(ruta_modelo)

    resultados = {}

    for cajero in lista_cajeros:

        df_modelo = preparar_datos_para_modelo(df_historico, cajero)

        if df_modelo is None or len(df_modelo) < 30:
            print(f"Cajero {cajero} sin datos suficientes. Se omite.")
            continue

        future = modelo.make_future_dataframe(
            df_modelo,
            periods=horizonte
        )

        forecast = modelo.predict(future)

        resultados[cajero] = forecast

        print(f"Inferencia completada para {cajero}")

    return resultados