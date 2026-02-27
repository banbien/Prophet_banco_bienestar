from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "insumos" / "df_general.parquet"

# Clusters disponibles:
#   - "event_driven"
#   - "grande_y_estable"
#   - "normal_con_picos"
#   - "normal_estable"


def construir_resumen_estructural(df):
    resumen = (
        df
        .groupby("cajero")
        .agg(
            dias_obs=("retiro", "count"),
            mediana=("retiro", "median"),
            p95=("retiro", lambda x: x.quantile(0.95))
        )
        .reset_index()
    )

    resumen["ratio_p95_mediana"] = resumen["p95"] / resumen["mediana"]
    resumen["ratio_p95_mediana"] = resumen["ratio_p95_mediana"].replace([np.inf, -np.inf], 0)
    resumen["ratio_p95_mediana"] = resumen["ratio_p95_mediana"].fillna(0)

    return resumen


def aplicar_reglas_precluster(
    df_resumen,
    umbral_grande=200000,
    umbral_estable=3,
    umbral_evento=8,
    umbral_picos=5
):
    def clasificar(row):
        mediana = row["mediana"]
        ratio = row["ratio_p95_mediana"]

        if mediana == 0:
            return "event_driven"
        elif (mediana >= umbral_grande) and (ratio <= umbral_estable):
            return "grande_y_estable"
        elif ratio >= umbral_evento:
            return "event_driven"
        elif ratio >= umbral_picos:
            return "normal_con_picos"
        else:
            return "normal_estable"

    df_resumen = df_resumen.copy()
    df_resumen["etiqueta"] = df_resumen.apply(clasificar, axis=1)

    return df_resumen


def seleccionar_cajeros_por_cluster(
    df_clasificados,
    cluster,
    n,
    modo="aleatorio",
    random_state=42
):
    """
    Devuelve un DataFrame con n cajeros del cluster indicado.
    modo: "aleatorio" | "mayor_ratio" | "mayor_mediana"
    """
    clusters_validos = ["event_driven", "grande_y_estable", "normal_con_picos", "normal_estable"]
    if cluster not in clusters_validos:
        raise ValueError(f"Cluster '{cluster}' no válido. Usa uno de: {clusters_validos}")

    df_cluster = df_clasificados[df_clasificados["etiqueta"] == cluster].copy()
    total_disponibles = len(df_cluster)

    if total_disponibles == 0:
        raise ValueError(f"No existen cajeros en el cluster '{cluster}'.")

    if n > total_disponibles:
        print(f"  Solo hay {total_disponibles} cajeros en '{cluster}'. Se devolverán todos.")
        n = total_disponibles

    if modo == "aleatorio":
        seleccion = df_cluster.sample(n=n, random_state=random_state)
    elif modo == "mayor_ratio":
        seleccion = df_cluster.sort_values("ratio_p95_mediana", ascending=False).head(n)
    elif modo == "mayor_mediana":
        seleccion = df_cluster.sort_values("mediana", ascending=False).head(n)
    else:
        raise ValueError(f"Modo '{modo}' no válido. Usa: 'aleatorio', 'mayor_ratio' o 'mayor_mediana'.")

    return seleccion.reset_index(drop=True)


def seleccionar_cajeros_multi_cluster(
    df_clasificados,
    solicitud_dict,
    modo="aleatorio",
    random_state=42
):
    """
    Selecciona cajeros de múltiples clusters.

    solicitud_dict ejemplo:
    {
        "normal_estable": 40,
        "event_driven": 20,
        "normal_con_picos": 15,
        "grande_y_estable": 5
    }

    Retorna: (resultados_dict, resumen_df)
      - resultados_dict: {cluster: [lista_cajeros]}
      - resumen_df: tabla con totales por cluster
    """
    resultados = {}
    resumen_rows = []

    total_solicitado = sum(solicitud_dict.values())

    for cluster, n in solicitud_dict.items():
        df_cluster = df_clasificados[df_clasificados["etiqueta"] == cluster].copy()
        disponibles = len(df_cluster)

        if disponibles == 0:
            print(f"  No existen cajeros en '{cluster}'. Se omite.")
            continue

        if n > disponibles:
            print(f"  '{cluster}': solo hay {disponibles} cajeros. Se ajusta N.")
            n = disponibles

        if modo == "aleatorio":
            seleccion = df_cluster.sample(n=n, random_state=random_state)
        elif modo == "mayor_ratio":
            seleccion = df_cluster.sort_values("ratio_p95_mediana", ascending=False).head(n)
        elif modo == "mayor_mediana":
            seleccion = df_cluster.sort_values("mediana", ascending=False).head(n)
        else:
            raise ValueError(f"Modo '{modo}' no válido.")

        lista_cajeros = seleccion["cajero"].tolist()
        resultados[cluster] = lista_cajeros

        porcentaje = (n / total_solicitado) * 100
        resumen_rows.append({
            "Cluster": cluster,
            "Cajeros seleccionados": n,
            "% del total": round(porcentaje, 1)
        })

    resumen_df = pd.DataFrame(resumen_rows)
    return resultados, resumen_df


if __name__ == "__main__":
    df = pd.read_parquet(DATA_PATH)
    resumen = construir_resumen_estructural(df)
    df_clasificados = aplicar_reglas_precluster(resumen)

    print("Distribución de clusters:")
    print(df_clasificados["etiqueta"].value_counts())

    solicitud = {
        "normal_estable": 40,
        "event_driven": 20,
        "normal_con_picos": 15,
        "grande_y_estable": 5
    }

    listas_atm, tabla_resumen = seleccionar_cajeros_multi_cluster(df_clasificados, solicitud)
    print(tabla_resumen)
