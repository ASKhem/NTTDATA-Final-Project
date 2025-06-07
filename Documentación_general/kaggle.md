# Demanda energética horaria, generación y clima

## Demanda eléctrica, generación por tipo, precios y clima en España

### Acerca del Dataset

**Contexto**
En un artículo publicado a principios de 2019, la predicción en los mercados energéticos se identifica como una de las áreas de contribución de mayor impacto del Aprendizaje Automático/Profundo hacia la transición a una infraestructura eléctrica basada en energías renovables.

**Contenido**
Este conjunto de datos contiene 4 años de datos horarios de consumo eléctrico, generación, precios y clima para España. Los datos de consumo y generación se obtuvieron de ENTSOE, un portal público de datos de los Operadores de Sistemas de Transmisión (TSO). Los precios de liquidación se obtuvieron del TSO español, Red Eléctrica de España. Los datos meteorológicos se compraron como parte de un proyecto personal a través de la API de Open Weather para las 5 ciudades más grandes de España y se hacen públicos aquí.

**Agradecimientos**
Estos datos están disponibles públicamente a través de ENTSOE y REE y se pueden encontrar en los enlaces mencionados (si se proporcionan).

**Inspiración**
El conjunto de datos es único porque contiene datos horarios del consumo eléctrico y las respectivas previsiones del TSO para el consumo y los precios. Esto permite comparar las previsiones prospectivas con las previsiones de última generación que se utilizan actualmente en la industria.

*   Visualizar las curvas de carga y de oferta marginal.
*   ¿Qué mediciones meteorológicas y qué ciudades influyen más en la demanda eléctrica, los precios y la capacidad de generación?
*   ¿Podemos pronosticar con 24 horas de antelación mejor que el TSO?
*   ¿Podemos predecir el precio de la electricidad por hora del día mejor que el TSO?
*   Pronosticar el precio intradiario o la demanda eléctrica hora por hora.
*   ¿Cuál es la próxima fuente de generación que se activará en la curva de carga?

### Archivos en el Dataset

*   **`hourly-energy-dataset/energy_dataset.csv`**: Contiene datos horarios relacionados con el consumo de energía, la generación por tipo y los precios en España.
*   **`hourly-energy-dataset/weather_features.csv`**: Contiene características meteorológicas horarias para las 5 ciudades más grandes de España.

### Enlace Original de Kaggle
[Energy Consumption Generation Prices and Weather](https://www.kaggle.com/datasets/nicholasjhana/energy-consumption-generation-prices-and-weather)
