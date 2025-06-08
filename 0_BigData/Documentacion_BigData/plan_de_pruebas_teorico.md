# Elaboración do plan de probas teórico

## Definición de obxetivos
Aspectos de calidade que queremos comprobar (que dimensións nos interesan)

## Identificación de criterios
Definimos reglas ou métricas específicas para avaliar a calidade dos datos (esto veremolo sobretodo máis adiante) ex: valores que non poden ser nulos, formatos de fechas, ids unicos…

## Preparación de probas
- **Probas validación:** Verificar que os datos cumplen as reglas predefinidas
- **Probas de integridade:** relaciones entre os datos
- **Probas de consistencia:** Asegurarse que os datos en ambos datasets son coherentes e non se contradicen (ex: si non hai sol non hay producción de enerxía solar)
- **Probas de completitude:** Detectar valors faltantes e avaliar o seu impacto.

## Diseño de casos de proba
Escenarios nos que os datos poderían fallar.
Datos fora dos rangos esperados (ex: 100º de temperatura), valores duplicados, datos erroneamente formateados…

## Facer probas
Usar a ferramenta de análise de datos para detectar estos problemas.

## Documentación dos resultados
Aquí rexistraremos os problemas atopados, o seu impacto e como os correximos.

## Accións correctivas
Si detectamos problemas → buscar como mellorar a calidade.

---

### Exemplo de Regra de Calidade

| ID | Regla de Calidad | Medida | Umbral | Conteo Medida | Total Registros | KQI = (Registros OK / Perímetro) | ¿KQI Aceptable? |
|:---|:---|:---|:---|:---|:---|:---|:---|
| 1 | Los registros deben ser únicos para cada elemento | Conteo de registros con ID repetido. **Sacar errores** | 0 registros: Aceptable <br> > 0 registros: Inaceptable | 249 | 100016 | 95,75% | Inaceptable |
| 2 | Los registros deben tener informados los siguientes campos: ID, Nombre, Primer apellido, Fecha de nacimiento | % de registros con el dato informado frente al total de registros. **Calcular para cada uno de los campos. Sacar los casos OK** | >= 90%: Aceptable <br> < 90%: Inaceptable | 95259 (ID) <br> 95040 (Nombre) <br> 95019 (Apellido) <br> 95021 (Fecha) | 100016 | 95.24% <br> 95.02% <br> 95.00% <br> 95.05% | Aceptable <br> Aceptable <br> Aceptable <br> Aceptable |
| 3 | Los países informados deben existir en la tabla maestra de países. | % de registros cuyo país informado existe en la tabla maestra de países frente al total de registros. **Sacar los casos OK** | 100%: Aceptable <br> < 100%: Inaceptable | 95123 | 100016 | 95.1078% | Inaceptable |
| 4 | El código postal en España es un número de 5 dígitos que empieza por un valor igual o inferior a 52 | % de registros de España cuyo código postal informado tiene un formato correcto frente al total de registros. **Sacar casos OK** | >= 80%: Aceptable <br> < 80%: Inaceptable | 808 | 100016 | 0.8079% | Inaceptable |
| 5 | El código postal en España sólo puede estar relacionado con una ciudad | % de registros de España que contienen un código postal que ha aparecido asociado a más de una ciudad sobre el total de registros. **Sacar errores** | >= 95%: Aceptable <br> < 95%: Inaceptable | 77933 | 100016 | 22.0795% | Inaceptable |
| 6 | La fecha de modificación del registro siempre tiene que ser igual o posterior a la fecha de alta | % de registros en los que la fecha de modificación es igual o posterior a la fecha de alta sobre el total de registros. **Sacar registros OK** | 100%: Aceptable <br> < 100%: Inaceptable | 89247 | 100016 | 89.2327% | Inaceptable |
| 7 | Los datos referentes a legalidad deben estar informados | % de registros en los que TODOS los campos de LEGALIDAD están informados sobre el total de registros. **Sacar registros OK** | 100%: Aceptable <br> < 100%: Inaceptable | 65087 | 100016 | 65.0766% | Inaceptable |

---

### Exemplos tendo en conta o tipo de datos que manexamos:
- datos temporais faltantes?
- Rangos validos? → temperaturas anomalas (ex: 60º, humidade do 0%con chuvia...)
- Xeración negativa de enerxía ou máis baixa da capacidade instalada (ver datos totais)
- Datos faltantes (integridade)
- Datos duplicados (integridade)
- Fechas e horas de ambos datasets iguais (consistencia)
- Coincidencia dos picos de demanda con olas de calor/frío? (consistencia)

---

## Dimensións

- **Unicidade:** Garantizar que non haxa rexistros duplicados. Establece que non existe máis dunha entidade no mesmo conxunto de datos.
- **Exactitude:** validar os rangos físicos posibles (temperaturas lóxicas). refirese ao modo no que o dato representa o mundo real.
- **Validez:** comprobación dos formatos das fechas(?). indica si os valores son consistentes con os definidos dentro do dominio de valores definido.
- **Razonabilidade:** Os datos teñen loxica (menos demanda de noite, menos xeracion solar). debe considerarse cando as expectativas de consistencia son relevantes dentro de contextos operacionais específicos.
- **Integridade:** Valores faltantes (nulos e demais). Consistencia entre indices de taboas ou coherencia interna para que non falten os datos.
- **Consistencia:** entre os datasets. (nos formatos das fechas por exemplo). refiere a como o dato almaceado nun repositorio é consistente con outro dato almaceado noutro repositorio por estar relacionados.
- **Precisión:** duplicados (fechas repetidas?). Nivel de detalle do elemento do dato. Os datos númericos poden necesitar precisión a varios dixitos significativos.
- **Completidude:** Busqueda de valores vacios ou nulos. Presencia dos datos requeridos.
