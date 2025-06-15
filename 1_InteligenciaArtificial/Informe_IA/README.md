# Informe IA
# Informe de Inteligencia Artificial Aplicada al Modelado Predictivo Energético para Naturgy

## Introducción y contexto del proyecto

Este informe presenta los resultados del desarrollo de modelos predictivos de Inteligencia Artificial para Naturgy, una de las empresas españolas líder en el sector energético. El proyecto responde a las necesidades de mejorar sus capacidades predictivas utilizando datos históricos proporcionados por la compañía.

Naturgy facilitó dos conjuntos de datos claves para este análisis:

*   Datos del Mix Energético Español: Series temporales horarias sobre generación y demanda energética nacional.
*   Datos climáticos: Variables meteorológicas por horas de múltiples localizaciones de España.

El objetivo principal fue desarrollar modelos para predecir horizontes de 1 a 6 horas de tres variables: la demanda total de energía, el precio del mercado eléctrico y la generación total de energía renovable.

Estas predicciones son cruciales para Naturgy, permitiendo:

*   Optimización operativa, lo que le permitiría mejorar la gestión de la generación y estabilidad de la red
*   Estrategias de mercado para afinar la participación en el mercado mayorista y la gestión de riesgos
*   Integración de Renovables para facilitar una gestión eficiente de las fuentes intermitentes.

## Feature Engineering

Para poder crear modelos fiables, se aplicó un extenso proceso de feature engineering para optimizar los datos de energía y clima para el modelado:

*   Análisis inicial y unión: Se evaluaron las variables clave de los datasets de energí y clima. Los datos climáticos se promediaron a nivel nacional, tratando el viento como un componente vectorial y finalmente se unieron al dataset de energía por fecha y hora.
*   Limpieza y procesamiento básico: Se eliminaron columnas constantes y predicciones del TSO. Después se creó una variable agregada (total\_renewable\_generation) y finalmente se analizaron las distribuciones  y correlaciones.
*   Transformación y tratamiento de outliers: Se aplicó capping a valores extremos y transformaciones logarítmicas (log, log1p) a variables sesgadas para normalizar distribuciones.
*   Creación de características avanzadas:
    *   Reducción de multicolinealidad: Se utilizó VIF para eliminar variables redundantes.
    *   Temporales cíclicas: Se generaron variables de seno/coseno para hora, día de la semana mes, etc., para capturar patrones periódicos.
    *   Lags: Se incorporaron valores pasados de características relevantes.

No se pudo aplicar técnicas de balanceo dado que el problema es de regresión. Todo el proceso está configurado en la función preprocess\_data\_pipeline() para asegurar la reproducibilidad.

## Entrenamiento y evaluación de modelos

Tras la ingeniería de características, se procedió a entrenar y evaluar dos tipos de modelos predictivos para las variables objetivo (total load actual, price actual, total\_renewable\_generation) en horizontes de H+1 a H+6. Los datos se dividieron en conjuntos de entrenamiento, validación y una prueba final con datos aislados. Las características numéricas se escalaron usando StandardScaler().

Los modelos escogidos fueron los siguientes:

*   XGBoost: Se utilizó xgb.XGBRegressor() dentro de un MultiOutputRegressor() para manejar las múltiples salidas. La principal razón de elegir este modelo fue debido a su eficiencia, robustez con datos tabulares y por su capacidad de manejar múltiples salidas  así como su regularización L1/L2 incorporadas.
    *   Hiperparámetros: n\_estimators=1700, max\_depth=8, subsample=0.8, learning\_rate=0.005.
*   Red Neuronal (MLP - Perceptrón Multicapa): Consta de una arquitectura secuencial con PyTorch, incluyendo cpas nn.Lenear(), normalización (nn.BatchNorm1d, … ), funciones de activación nn.ReLU() en capas ocultas y regularización con nn.Droptout(0.2). La capa de salida es lineal para nuestro problema de regresión. Se decidió por la capacidad de las redes neuronales de captar relaciones no lineales complejas que se alineaban con el proyecto. A parte daba resultados muy similares a otras redes más complejas como pueden ser las de series temporales (TSLM).
    *   Hiperparámetros:para la función de pérdida se usó L1Loss(); como optimizador optim.Adam() con lr=0.00001; como planificador de tasa de aprendizaje se usó ReduceOnPlateau(). Finalmente se aplicó un early stopping con una paciencia de 40 épocas para prevenir sobreajuste o que el modelo se siguiera entrenando con mejoras ínfimas.

## Comparativa de rendimiento y tiempos de entrenamiento

Los modelos se evaluaron utilizando R² (coeficiente de determinación), RMSE (Raíz del Error Cuadrático Medio), MAE (Error Absoluto Medio) y sMAPE (Error Porcentual Absoluto Medio Simétrico).

Aquí se encuentra el informe detallado sobre los modelos de Inteligencia Artificial desarrollados, sus resultados, conclusiones y próximos pasos.

# Informe de Inteligencia Artificial Aplicada al Modelado Predictivo Energético para Naturgy

## Introducción y contexto del proyecto

Este informe presenta los resultados del desarrollo de modelos predictivos de Inteligencia Artificial para Naturgy, una de las empresas españolas líder en el sector energético. El proyecto responde a las necesidades de mejorar sus capacidades predictivas utilizando datos históricos proporcionados por la compañía.

Naturgy facilitó dos conjuntos de datos claves para este análisis:

*   Datos del Mix Energético Español: Series temporales horarias sobre generación y demanda energética nacional.
*   Datos climáticos: Variables meteorológicas por horas de múltiples localizaciones de España.

El objetivo principal fue desarrollar modelos para predecir horizontes de 1 a 6 horas de tres variables: la demanda total de energía, el precio del mercado eléctrico y la generación total de energía renovable.

Estas predicciones son cruciales para Naturgy, permitiendo:

*   Optimización operativa, lo que le permitiría mejorar la gestión de la generación y estabilidad de la red
|                       | XGBoost     |             |             |          | MLP         |             |             |          |
| :-------------------- | :---------- | :---------- | :---------- | :------- | :---------- | :---------- | :---------- | :------- |
|                       | R2          | RMSE        | MAE         | sMAPE    | R2          | RMSE        | MAE         | sMAPE    |
| renewable\_H\_plus\_6 | 0.823469    | 1484.932725 | 1186.277652 | 11.958129| 0.847161    | 1381.698408 | 1089.494666 | 11.027053|
| load\_H\_plus\_6      | 0.905611    | 1511.633135 | 1121.651317 | 4.124332 | 0.846812    | 1925.743498 | 1428.098706 | 5.109202 |
| renewable\_H\_plus\_1 | 0.974325    | 565.720860  | 402.244674  | 4.114768 | 0.964282    | 667.256410  | 499.152064  | 5.006259 |
| load\_H\_plus\_1      | 0.988410    | 533.791674  | 336.940117  | 1.280638 | 0.974265    | 795.417798  | 610.786716  | 2.239124 |
| price\_H\_plus\_1     | 0.933953    | 1.836295    | 1.400207    | 2.104182 | 0.897759    | 2.284692    | 1.781431    | 2.662419 |

Ambos modelos mostraron un rendimiento prometedor, con condiciones para el horizonte H+1 generalmente más precisas que para H+6. No obstante XGBoost tuvo el mejor rendimiento en la mayoría de las métricas especialmente en R². La predicción más difícil de calcular es total\_renewable\_energy H+6 por la volatilidad de las características de las que depende (metereológicas).

Tiempos de entrenamiento: XGBoost : 190.3s VS MLP : 161.7s.

## Elección del modelo final y conclusiones

Tras comparar el rendimiento del conjunto de prueba. XGBoost se selecciona como el modelo principal debido a su robustez y superioridad general en las métricas para la mayoría de las preidcciones.

La red neuronal MLP mostró un buen resultado, destacando en la predicción de renovables a  H+6. Para este caso se podría pensar en algún sistema híbrofo como ensambling.

## Conclusión final

El proyecto deja claro que la IA puede predecir variables energéticas clave para Naturgy con precisión. La ingeniería de características fue fundamental, sin ellas los modelos no pordían captar patrones temporales. Las mejores predicciones son las que son a corto plazo debido a que hay menos incertidumbre.

En el futuro se buscará refinar hiperparámetros de los modelos, incorporar variables nuevas, considerar modelos más avanzados como TSLM pero bien configurados y obtener datasets más grandes.

Los modelos actuales, con XGBoost en el podium, proporcionan una herramienta valiosa para naturgy, con potencial de mejora continua y base para modelos más avanzados.
*   Estrategias de mercado para afinar la participación en el mercado mayorista y la gestión de riesgos
*   Integración de Renovables para facilitar una gestión eficiente de las fuentes intermitentes.

## Feature Engineering

Para poder crear modelos fiables, se aplicó un extenso proceso de feature engineering para optimizar los datos de energía y clima para el modelado:

*   Análisis inicial y unión: Se evaluaron las variables clave de los datasets de energí y clima. Los datos climáticos se promediaron a nivel nacional, tratando el viento como un componente vectorial y finalmente se unieron al dataset de energía por fecha y hora.
*   Limpieza y procesamiento básico: Se eliminaron columnas constantes y predicciones del TSO. Después se creó una variable agregada (total\_renewable\_generation) y finalmente se analizaron las distribuciones  y correlaciones.
*   Transformación y tratamiento de outliers: Se aplicó capping a valores extremos y transformaciones logarítmicas (log, log1p) a variables sesgadas para normalizar distribuciones.
*   Creación de características avanzadas:
    *   Reducción de multicolinealidad: Se utilizó VIF para eliminar variables redundantes.
    *   Temporales cíclicas: Se generaron variables de seno/coseno para hora, día de la semana mes, etc., para capturar patrones periódicos.
    *   Lags: Se incorporaron valores pasados de características relevantes.

No se pudo aplicar técnicas de balanceo dado que el problema es de regresión. Todo el proceso está configurado en la función preprocess\_data\_pipeline() para asegurar la reproducibilidad.

## Entrenamiento y evaluación de modelos

Tras la ingeniería de características, se procedió a entrenar y evaluar dos tipos de modelos predictivos para las variables objetivo (total load actual, price actual, total\_renewable\_generation) en horizontes de H+1 a H+6. Los datos se dividieron en conjuntos de entrenamiento, validación y una prueba final con datos aislados. Las características numéricas se escalaron usando StandardScaler().

Los modelos escogidos fueron los siguientes:

*   XGBoost: Se utilizó xgb.XGBRegressor() dentro de un MultiOutputRegressor() para manejar las múltiples salidas. La principal razón de elegir este modelo fue debido a su eficiencia, robustez con datos tabulares y por su capacidad de manejar múltiples salidas  así como su regularización L1/L2 incorporadas.
    *   Hiperparámetros: n\_estimators=1700, max\_depth=8, subsample=0.8, learning\_rate=0.005.
*   Red Neuronal (MLP - Perceptrón Multicapa): Consta de una arquitectura secuencial con PyTorch, incluyendo cpas nn.Lenear(), normalización (nn.BatchNorm1d, … ), funciones de activación nn.ReLU() en capas ocultas y regularización con nn.Droptout(0.2). La capa de salida es lineal para nuestro problema de regresión. Se decidió por la capacidad de las redes neuronales de captar relaciones no lineales complejas que se alineaban con el proyecto. A parte daba resultados muy similares a otras redes más complejas como pueden ser las de series temporales (TSLM).
    *   Hiperparámetros:para la función de pérdida se usó L1Loss(); como optimizador optim.Adam() con lr=0.00001; como planificador de tasa de aprendizaje se usó ReduceOnPlateau(). Finalmente se aplicó un early stopping con una paciencia de 40 épocas para prevenir sobreajuste o que el modelo se siguiera entrenando con mejoras ínfimas.

## Comparativa de rendimiento y tiempos de entrenamiento

Los modelos se evaluaron utilizando R² (coeficiente de determinación), RMSE (Raíz del Error Cuadrático Medio), MAE (Error Absoluto Medio) y sMAPE (Error Porcentual Absoluto Medio Simétrico).

|                       | XGBoost     |             |             |          | MLP         |             |             |          |
| :-------------------- | :---------- | :---------- | :---------- | :------- | :---------- | :---------- | :---------- | :------- |
|                       | R2          | RMSE        | MAE         | sMAPE    | R2          | RMSE        | MAE         | sMAPE    |
| renewable\_H\_plus\_6 | 0.823469    | 1484.932725 | 1186.277652 | 11.958129| 0.847161    | 1381.698408 | 1089.494666 | 11.027053|
| load\_H\_plus\_6      | 0.905611    | 1511.633135 | 1121.651317 | 4.124332 | 0.846812    | 1925.743498 | 1428.098706 | 5.109202 |
| renewable\_H\_plus\_1 | 0.974325    | 565.720860  | 402.244674  | 4.114768 | 0.964282    | 667.256410  | 499.152064  | 5.006259 |
| load\_H\_plus\_1      | 0.988410    | 533.791674  | 336.940117  | 1.280638 | 0.974265    | 795.417798  | 610.786716  | 2.239124 |
| price\_H\_plus\_1     | 0.933953    | 1.836295    | 1.400207    | 2.104182 | 0.897759    | 2.284692    | 1.781431    | 2.662419 |

|             | XGBoost | MLP     |
| :---------- | :------ | :------ |
| R2          |         |         |
| RMSE        |         |         |
| MAE         |         |         |
| sMAPE       |         |         |

Ambos modelos mostraron un rendimiento prometedor, con condiciones para el horizonte H+1 generalmente más precisas que para H+6. No obstante XGBoost tuvo el mejor rendimiento en la mayoría de las métricas especialmente en R². La predicción más difícil de calcular es total\_renewable\_energy H+6 por la volatilidad de las características de las que depende (metereológicas).

Tiempos de entrenamiento: XGBoost : 190.3s VS MLP : 161.7s.

## Elección del modelo final y conclusiones

Tras comparar el rendimiento del conjunto de prueba. XGBoost se selecciona como el modelo principal debido a su robustez y superioridad general en las métricas para la mayoría de las preidcciones.

La red neuronal MLP mostró un buen resultado, destacando en la predicción de renovables a  H+6. Para este caso se podría pensar en algún sistema híbrofo como ensambling.

## Conclusión final

El proyecto deja claro que la IA puede predecir variables energéticas clave para Naturgy con precisión. La ingeniería de características fue fundamental, sin ellas los modelos no pordían captar patrones temporales. Las mejores predicciones son las que son a corto plazo debido a que hay menos incertidumbre.

En el futuro se buscará refinar hiperparámetros de los modelos, incorporar variables nuevas, considerar modelos más avanzados como TSLM pero bien configurados y obtener datasets más grandes.

Los modelos actuales, con XGBoost en el podium, proporcionan una herramienta valiosa para naturgy, con potencial de mejora continua y base para modelos más avanzados.
