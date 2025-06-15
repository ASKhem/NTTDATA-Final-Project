# Plan de Pruebas

## Definición de objetivos

Queremos comprobar la calidad de los datos que tenemos relacionados con la producción de energía y la meteorología. Nos centramos en aspectos como que los datos tengan sentido, estén bien relacionados, sean coherentes entre sí y estén completos. Lo que buscamos es detectar posibles errores que puedan afectar al análisis del proyecto.

## Identificación de criterios

Algunas de las reglas establecidas para comprobar la calidad de los datos son:

*   No puede haber valores nulos en los campos clave como producción, carga o temperatura
*   No puede haber valores negativos si no tienen lógica en ese contexto
*   Los valores deben estar en las unidades requeridas
*   No debe de haber valores duplicados ni mal escritos
*   Se cumplen los requisitos de integridad, es decir las relaciones entre datos las dos tablas son consistentes y correctas.

## Preparación de pruebas

En esta fase se preparan pruebas para garantizar la calidad de los datos, evaluando si son adecuados para el análisis.
El diseño de las pruebas se basará siguiendo los siguientes requisitos de calidad:

*   Unicidad: No debe haber registros duplicados.
*   Exactitud: Los valores deben estar dentro de rangos lógicos.
*   Validez: Los formatos deben ser correctos, como fechas uniformes.
*   Razonabilidad: Los datos deben tener sentido según el contexto.
*   Integridad: Se identifican valores faltantes o vacíos.
*   Consistencia: No debe haber contradicciones entre conjuntos de datos.
*   Precisión: Las mediciones no deben repetirse sin motivo.
*   Completitud: Los datos deben estar completos.

## Diseño de casos de prueba

En esta parte definimos los diferentes escenarios en los que los datos podrían fallar.
Los tipos de casos que vamos a diseñar son los siguientes:

*   Fechas mal formateadas o vacías.
*   Valores nulos o vacíos en campos obligatorios.
*   Temperaturas fuera de los rangos físicos posibles.
*   Producciones o precios negativos no tienen lógica.
*   Campos con texto donde debería haber números.
*   Duplicados en fechas u otros campos clave.
*   Incoherencias entre los datasets, como datos meteorológicos que no se reflejan en la producción energética.
*   Formatos inconsistentes entre los dos ficheros.
*   Datos que no cumplen con las unidades esperadas

Estos casos están diseñados para comprobar cómo responden los datos ante errores típicos y asegurar que cualquier anomalía sea detectada antes del análisis final.

## Ejecución de pruebas

Para llevar a cabo las pruebas, desarrollamos un script que aplica todas las reglas definidas en el diseño de los casos.
Este script recorre ambos conjuntos de datos y comprueba si se cumplen las condiciones de calidad establecidas. En general, la mayoría de los campos cumplen con los requisitos preestablecidos. No obstante se detectaron errores relacionados con:

*   Presencia de valores nulos en columnas clave como la producción solar
*   Presiones fuera de los rangos físicos posibles
*   Duplicados en registros con la misma fecha y hora, afectando a la unicidad

## Acciones correctivas

Una vez identificados los errores, se aplicaron diferentes acciones para mejorar la calidad de los datos y dejar los conjuntos listos para su análisis. Estas son las medidas que se tomaron:

*   Eliminación de registros duplicados según las columnas que han de ser únicas .
*   Sustitución de valores nulos en campos clave usando métodos como la imputación por mediana
*   Eliminación de valores fuera de rango.
*   Eliminación de filas incompletas o inconsistentes, cuando no era posible completar la información de forma fiable.
*   Homogeneización de unidades, para adaptarlos al sistema de unidades que se utiliza en España.

Estas acciones permitieron que los datos finales cumplieran con los requisitos de calidad establecidos.