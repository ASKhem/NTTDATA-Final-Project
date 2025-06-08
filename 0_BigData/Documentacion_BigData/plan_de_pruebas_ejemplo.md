# Plan de Pruebas de Calidad de Datos (ejemplo)

Este documento define las pruebas de calidad que se aplicarán a los datos durante el proceso ETL para asegurar su fiabilidad, consistencia e integridad antes de ser cargados en el Data Warehouse.

## 1. Pruebas a Nivel de Fichero

| ID | Regla de Calidad | Medida | Umbral | Acción en caso de fallo |
| :--- | :--- | :--- | :--- | :--- |
| FILE-01 | Existencia de Fichero | Verificar que los ficheros `energy_dataset.csv` y `weather_features.csv` existen en la fuente. | **Aceptable:** Ambos existen. <br> **Inaceptable:** Falta uno o ambos. | Abortar proceso y notificar. |
| FILE-02 | Formato Correcto | Comprobar que los ficheros son CSV válidos y usan la codificación esperada (UTF-8). | **Aceptable:** Formato correcto. <br> **Inaceptable:** Formato incorrecto. | Abortar proceso y notificar. |

## 2. Pruebas a Nivel de Columna

Estas pruebas se aplicarán a la tabla procesada antes de cargarla en BigQuery.

| ID | Regla de Calidad | Medida | Umbral | Acción en caso de fallo |
| :--- | :--- | :--- | :--- | :--- |
| COL-01 | Nulidad en columnas críticas | Asegurar que `timestamp`, `total_load_actual`, `price_actual` no contienen valores nulos. | **Aceptable:** 100% de no nulos. <br> **Inaceptable:** < 100%. | Descartar la fila y registrarla en logs. |
| COL-02 | Unicidad de registros | Verificar que no existen registros duplicados para la misma combinación de `timestamp` y `city`. | **Aceptable:** 100% de unicidad. <br> **Inaceptable:** < 100%. | Descartar filas duplicadas y registrar en logs. |
| COL-03 | Rango de Valores para `temp_celsius` | La temperatura debe estar en un rango lógico (ej. -50 a 50 °C). | **Aceptable:** >= 99.5% de los registros. <br> **Inaceptable:** < 99.5%. | Marcar la fila como inválida o registrarla. |
| COL-04 | Rango de Valores para `humidity` y `clouds` | Los valores deben estar entre 0 y 100. | **Aceptable:** >= 99% de los registros. <br> **Inaceptable:** < 99%. | Corregir si es posible (ej. `valor % 100`) o marcar como inválida. |
| COL-05 | Validez de `weather_condition` | El valor debe pertenecer a una lista predefinida de condiciones climáticas. | **Aceptable:** >= 98% de los registros. <br> **Inaceptable:** < 98%. | Marcar como "Desconocido" y registrar. |
| COL-06 | Consistencia de valores numéricos | Los valores `total_load_actual` y `price_actual` deben ser mayores o iguales a cero. | **Aceptable:** 100% de los registros. <br> **Inaceptable:** < 100%. | Marcar la fila como inválida y registrar. |

## 3. Pruebas de Integridad Referencial

| ID | Regla de Calidad | Medida | Umbral | Acción en caso de fallo |
| :--- | :--- | :--- | :--- | :--- |
| REF-01 | Consistencia en la unión de datos | Verificar que el número de filas en la tabla final es consistente después de unir los datasets de energía y clima. | **Aceptable:** >= 99.9% de filas conservadas. <br> **Inaceptable:** < 99.9%. | Investigar la causa de la pérdida de datos. |

## 4. Evidencias de Ejecución

Para cada ejecución del pipeline ETL, se generará un reporte que contendrá:
- Resumen de la ejecución (fecha, hora, duración).
- Número de filas procesadas, aceptadas y rechazadas.
- Detalle de las pruebas fallidas y el número de filas afectadas por cada una, siguiendo el formato de la tabla de ejemplo del plan teórico.
- Muestras de filas que no pasaron las pruebas de calidad.
