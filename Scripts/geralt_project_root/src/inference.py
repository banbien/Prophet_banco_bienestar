import pandas as pd
import numpy as np
from neuralprophet import load


def cargar_modelo(ruta_modelo: str):
    """Carga modelo NeuralProphet previamente entrenado y guardado con neuralprophet.save()."""
    modelo = load(str(ruta_modelo))
    return modelo


def preparar_datos_para_modelo(df, cajero_id):
    """Filtra y formatea datos de un cajero para NeuralProphet (columnas ds, y)."""
    df_cajero = df[df["cajero"] == cajero_id].copy()

    if df_cajero.empty:
        return None

    df_cajero = df_cajero.rename(columns={"fecha": "ds", "retiro": "y"})
    df_cajero = df_cajero[["ds", "y"]].sort_values("ds").reset_index(drop=True)
    df_cajero["ds"] = pd.to_datetime(df_cajero["ds"])

    return df_cajero


def inferencia_por_lista(lista_cajeros, df_historico, ruta_modelo, horizonte=30):
    """
    Realiza inferencia para cada cajero de la lista.
    Retorna dict {cajero_id: DataFrame con predicciones futuras (ds, yhat1)}.
    El modelo requiere mínimo 150 días de historial (n_lags=150).
    """
    modelo = cargar_modelo(ruta_modelo)
    resultados = {}

    for cajero in lista_cajeros:
        df_cajero = preparar_datos_para_modelo(df_historico, cajero)

        n_dias = len(df_cajero) if df_cajero is not None else 0

        if df_cajero is None or n_dias < 150:
            print(f"  [OMITIDO] Cajero {cajero}: {n_dias} días históricos (mínimo 150).")
            continue

        try:
            future = modelo.make_future_dataframe(df_cajero, periods=horizonte)
            forecast = modelo.predict(future)

            ultima_fecha = df_cajero["ds"].max()
            pred_cols = ["ds"] + [c for c in forecast.columns if c.startswith("yhat")]
            predicciones_futuras = forecast[forecast["ds"] > ultima_fecha][pred_cols].copy()

            resultados[cajero] = {
                "forecast_completo": forecast,
                "predicciones_futuras": predicciones_futuras,
                "n_dias_historicos": n_dias,
                "media_historica": round(df_cajero["y"].mean(), 2),
            }

            print(f"  [OK] Cajero {cajero}: {n_dias} días históricos, {len(predicciones_futuras)} días predichos.")

        except Exception as e:
            print(f"  [ERROR] Cajero {cajero}: {e}")

    return resultados
