# Metodlogía Siz Sigma para calidad de datos

La metodología **Six Sigma** es ampliamente conocida por su enfoque en la mejora de procesos y la reducción de variabilidad, pero su aplicación a la **calidad de datos** (especialmente al comparar dos bases de datos) requiere adaptaciones específicas:

---

## **1. Definir (Define)**
**Objetivo:** Establecer claramente el alcance y los objetivos del proyecto.

- **Identificar las bases de datos a comparar:** Define cuáles son las dos bases de datos (ej: Base A vs. Base B).
- **Establecer métricas clave de calidad de datos:**
  - **Exactitud:** ¿Los datos coinciden con la realidad?
  - **Completitud:** ¿Hay valores faltantes?
  - **Consistencia:** ¿Los datos son uniformes en formato y valores?
  - **Unicidad:** ¿Hay duplicados?
  - **Validez:** ¿Los datos cumplen con reglas de negocio o formatos esperados?
- **Definir el equipo y roles:** Asigna responsables para la recolección, análisis y validación.

---

## **2. Medir (Measure)**
**Objetivo:** Cuantificar la calidad actual de los datos en ambas bases.

- **Seleccionar muestras representativas:** Extrae muestras aleatorias de ambas bases para el análisis.
- **Herramientas comunes:**
  - **SQL:** Para consultar y comparar registros.
  - **Python/R:** Para análisis estadísticos (ej: pandas, dplyr).
  - **Herramientas ETL:** Para limpieza y transformación (ej: Talend, Informatica).
- **Métricas a medir:**
  - Porcentaje de registros con errores (ej: valores nulos, inconsistencias).
  - Tasa de duplicados.
  - Desviaciones en formatos (ej: fechas, códigos postales).
- **Ejemplo de métrica:**
  - *"El 15% de los registros en la Base A tienen valores nulos en el campo 'teléfono', vs. 5% en la Base B."*

---

## **3. Analizar (Analyze)**
**Objetivo:** Identificar las causas raíz de las diferencias en calidad.

- **Comparar métricas entre bases:**
  - Usa tablas comparativas o gráficos (ej: barras para % de completitud).
  - Ejemplo:

    | Métrica          | Base A (%) | Base B (%) |
    |------------------|-----------|-----------|
    | Completitud      | 85        | 95        |
    | Exactitud        | 90        | 88        |
    | Duplicados       | 10        | 2         |

- **Análisis de causas:**
  - ¿Los errores son sistemáticos (ej: falla en un proceso de carga) o aleatorios?
  - ¿Hay diferencias en los procesos de origen de los datos?

---

## **4. Mejorar (Improve)**
**Objetivo:** Proponer soluciones para reducir las brechas de calidad.

- **Acciones correctivas:**
  - **Limpieza de datos:** Eliminar duplicados, corregir formatos.
  - **Validación automática:** Implementar reglas de negocio (ej: validar correos electrónicos).
  - **Capacitación:** Si los errores son humanos, entrenar al equipo.
- **Pilotear soluciones:** Aplicar mejoras a una muestra y medir el impacto.

---

## **5. Controlar (Control)**
**Objetivo:** Asegurar que las mejoras se mantengan en el tiempo.

- **Monitoreo continuo:**
  - Dashboards con métricas de calidad (ej: Power BI, Tableau).
  - Alertas automáticas para desviaciones (ej: si los nulos superan el 5%).
- **Documentación:**
  - Crear un manual de calidad de datos con reglas y responsables.
  - Establecer auditorías periódicas.

---

## **Comparación Directa entre Bases**
Para comparar **Base A vs. Base B** de manera práctica:
1. **Unir las bases** por un campo clave (ej: ID de cliente).
2. **Identificar discrepancias:**
   - Registros que existen en una base pero no en la otra.
   - Diferencias en valores para el mismo registro.
3. **Priorizar:**
   - Enfocarse en los campos críticos para el negocio (ej: datos de contacto, transacciones).
