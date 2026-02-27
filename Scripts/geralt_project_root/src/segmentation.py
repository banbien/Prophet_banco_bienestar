# construir_resumen_estructural
# aplicar_reglas_precluster
# seleccionar_cajeros_multi_cluster

from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "insumos" / "df_general.parquet"


df = pd.read_parquet(DATA_PATH)

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
    
    resumen["ratio_p95_mediana"] = (
        resumen["p95"] / resumen["mediana"]
    )
    
    resumen["ratio_p95_mediana"] = resumen["ratio_p95_mediana"].replace([np.inf, -np.inf], 0)
    resumen["ratio_p95_mediana"] = resumen["ratio_p95_mediana"].fillna(0)
    
    return resumen


def aplicar_reglas_precluster(
    df_resumen,
    umbral_grande,
    umbral_estable,
    umbral_evento,
    umbral_picos
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
    
    df_resumen["etiqueta"] = df_resumen.apply(clasificar, axis=1)
    
    return df_resumen

resumen = construir_resumen_estructural(df)

df_clasificados = aplicar_reglas_precluster(
    resumen,
    umbral_grande=200000,
    umbral_estable=3,
    umbral_evento=8,
    umbral_picos=5
)


def seleccionar_cajeros_por_cluster(
    df_clasificados,
    cluster,
    n,
    modo="aleatorio",
    random_state=42
):
    
    df_cluster = df_clasificados[
        df_clasificados["etiqueta"] == cluster
    ].copy()
    
    total_disponibles = len(df_cluster)
    
    if total_disponibles == 0:
        raise ValueError(f"No existen cajeros en el cluster '{cluster}'")
    
    if n > total_disponibles:
        print(f"Solo hay {total_disponibles} cajeros en '{cluster}'. Se devolverán todos.")
        n = total_disponibles
    
    if modo == "aleatorio":
        seleccion = df_cluster.sample(n=n, random_state=random_state)
        
    elif modo == "mayor_ratio":
        seleccion = df_cluster.sort_values(
            "ratio_p95_mediana",
            ascending=False
        ).head(n)
        
    elif modo == "mayor_mediana":
        seleccion = df_cluster.sort_values(
            "mediana",
            ascending=False
        ).head(n)
        
    else:
        raise ValueError("Modo no válido.")
    
    return seleccion.reset_index(drop=True)

'''Las 4 categorías que existen son:

    - event_driven
    - grande_y_estable
    - normal_con_picos
    - normal_estable
'''
seleccionar_cajeros_por_cluster(
    df_clasificados,
    cluster="event_driven",
    n=5,
    modo="mayor_ratio"
)

#NOTA: Sería mejor si la columna etiqueta estuviera junto a cajero. 


# Core del extractor:
def seleccionar_cajeros_multi_cluster(
    df_clasificados,
    solicitud_dict,
    modo="aleatorio",
    random_state=42
):
    """
    solicitud_dict ejemplo:
    {
        "normal_estable": 50,
        "event_driven": 30,
        "normal_con_picos": 10
    }
    """
    
    resultados = {}
    resumen_rows = []
    
    total_solicitado = sum(solicitud_dict.values())
    
    for cluster, n in solicitud_dict.items():
        
        df_cluster = df_clasificados[
            df_clasificados["etiqueta"] == cluster
        ].copy()
        
        disponibles = len(df_cluster)
        
        if disponibles == 0:
            print(f"No existen cajeros en {cluster}. Se omite.")
            continue
        
        if n > disponibles:
            print(f"{cluster}: solo hay {disponibles}. Se ajusta N.")
            n = disponibles
        
        # Selección
        if modo == "aleatorio":
            seleccion = df_cluster.sample(n=n, random_state=random_state)
        elif modo == "mayor_ratio":
            seleccion = df_cluster.sort_values(
                "ratio_p95_mediana",
                ascending=False
            ).head(n)
        elif modo == "mayor_mediana":
            seleccion = df_cluster.sort_values(
                "mediana",
                ascending=False
            ).head(n)
        else:
            raise ValueError("Modo no válido.")
        
        lista_cajeros = seleccion["cajero"].tolist()
        
        resultados[cluster] = lista_cajeros
        
        porcentaje = (n / total_solicitado) * 100
        
        resumen_rows.append({
            "Pre-cluster": cluster.upper(),
            "Porcentaje (%)": round(porcentaje, 2), #establecer si el parámetro es verdaderamente funcional.
            "Número (n)": n
        })
    
    resumen_df = pd.DataFrame(resumen_rows)
    
    return resultados, resumen_df

solicitud = {
    "normal_estable": 40,
    "event_driven": 20,
    "normal_con_picos": 15,
    "grande_y_estable": 5
    
}

listas_atm, tabla_resumen = seleccionar_cajeros_multi_cluster(
    df_clasificados,
    solicitud,
    modo="aleatorio"
)


#diccionario que contiene todos los elementos solicitados
#listas_atm


# print(listas_atm.get('normal_estable'))
# print(listas_atm.get('event_driven'))
# print(listas_atm.get('normal_con_picos'))
# print(listas_atm.get('grande_y_estable'))