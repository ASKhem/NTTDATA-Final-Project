import pandas as pd
from openpyxl import load_workbook

ruta_excel = 'dq_report.xlsx'
weather_hoja = 'Tiempo'               
col_weather = 'D'
col_total_weather = 'E'               

weather_report = 'weather_report.csv' 
energy_report = 'energy_report.csv'          
col_energy = 'D'  
col_total_energy = 'E'               

energy_hoja = 'Energia'               

salida_excel = 'dq_report_results.xlsx' 

weather_df = pd.read_csv(weather_report, header=0)
weather_data = weather_df.iloc[0].tolist()

energy_df = pd.read_csv(energy_report, header=0)
energy_data = energy_df.iloc[0].tolist()
wb = load_workbook(ruta_excel)
hoja_wth = wb[weather_hoja]
hoja_eng = wb[energy_hoja]

total_rows_weather = weather_df.iloc[0, -1] 
for i, valor in enumerate(weather_data, start=2):
    celda = f'{col_weather}{i}'
    hoja_wth[celda] = valor
    if valor !='-':
        celda = f'{col_total_weather}{i}'
        hoja_wth[celda] = total_rows_weather

total_rows_energy = energy_df.iloc[0, -1] 
for i, valor in enumerate(energy_data, start=2):
    celda = f'{col_energy}{i}'
    hoja_eng[celda] = valor
    if valor !='-':
        celda = f'{col_total_weather}{i}'
        hoja_eng[celda] = total_rows_energy

wb.save(salida_excel)

print("Reporte realizado con éxito")
