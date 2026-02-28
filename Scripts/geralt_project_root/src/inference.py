import pandas as pd
import numpy as np
from neuralprophet import load
from sklearn.metrics import r2_score, mean_absolute_error

from src.events_calendar import agregar_columnas_eventos


def cargar_modelo(ruta_modelo: str):
    """Carga modelo NeuralProphet previamente entrenado y guardado con neuralprophet.save()."""
    modelo = load(str(ruta_modelo))
    return modelo


def preparar_datos_para_modelo(df, cajero_id):
    """
    Filtra y formatea datos de un cajero para NeuralProphet.
    Añade las columnas binarias de eventos que el modelo requiere.
    """
    df_cajero = df[df["cajero"] == cajero_id].copy()

    if df_cajero.empty:
        return None

    df_cajero = df_cajero.rename(columns={"fecha": "ds", "retiro": "y"})
    df_cajero = df_cajero[["ds", "y"]].sort_values("ds").reset_index(drop=True)
    df_cajero["ds"] = pd.to_datetime(df_cajero["ds"])

    df_cajero = agregar_columnas_eventos(df_cajero)

    return df_cajero


def inferencia_por_lista(lista_cajeros, df_historico, ruta_modelo, horizonte=30):
    """
    Para cada cajero:
      1. Predice sobre todo el histórico (in-sample) → calcula R², MAE, RMSE.
      2. Genera predicciones futuras (horizonte días).
    Retorna dict {cajero_id: dict con resultados}.
    Requiere mínimo 150 días de historial por cajero (n_lags=150).
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
            # ── IN-SAMPLE: predecir sobre todo el histórico ──────────────────
            forecast_hist = modelo.predict(df_cajero)

            df_base = df_cajero[["ds", "y"]].copy()
            merged = df_base.merge(
                forecast_hist[["ds", "yhat1"]], on="ds"
            ).dropna(subset=["yhat1"])

            n_neg = int((merged["yhat1"] < 0).sum())
            merged["yhat1"] = merged["yhat1"].clip(lower=0)

            r2   = round(float(r2_score(merged["y"], merged["yhat1"])), 4)
            mae  = round(float(mean_absolute_error(merged["y"], merged["yhat1"])), 0)
            rmse = round(float(np.sqrt(((merged["yhat1"] - merged["y"]) ** 2).mean())), 0)

            metricas = {
                "r2": r2,
                "mae": mae,
                "rmse": rmse,
                "n_negativos_corregidos": n_neg,
            }

            # ── FUTURO: predicciones más allá del último día histórico ────────
            future = modelo.make_future_dataframe(df_cajero, periods=horizonte)
            forecast_fut = modelo.predict(future)

            ultima_fecha = df_cajero["ds"].max()
            pred_cols = ["ds"] + [c for c in forecast_fut.columns if c.startswith("yhat")]
            pred_fut = forecast_fut[forecast_fut["ds"] > ultima_fecha][pred_cols].copy()
            pred_fut["yhat1"] = pred_fut["yhat1"].clip(lower=0)

            resultados[cajero] = {
                "merged_historico":   merged,        # ds, y, yhat1 para el plot
                "predicciones_futuras": pred_fut,    # días futuros
                "metricas":           metricas,
                "n_dias_historicos":  n_dias,
                "media_historica":    round(float(df_cajero["y"].mean()), 2),
            }

            print(
                f"  [OK] Cajero {cajero}: "
                f"R²={r2:.4f} | MAE=${mae:,.0f} | RMSE=${rmse:,.0f}"
            )

        except Exception as e:
            print(f"  [ERROR] Cajero {cajero}: {e}")

    return resultados
