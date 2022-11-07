# Importar librerías de trabajo
from streamlit_echarts import st_echarts
from streamlit_echarts import JsCode
import streamlit as st
import numpy as np
import pandas as pd
import os

# Definir las opciones de pandas para visualizar todos los registros y columnas
pd.options.display.max_rows = None
pd.options.display.max_columns = None

# Definir una función para calcular la variable del deflactor
def deflactor_serie(year:int):

  # Importar información del PIB Nominal y Real
  # deflactors = pd.read_csv('https://raw.githubusercontent.com/miguellosoyo/financial_statements/main/Cifras%20del%20PIB%20Nominal-Real.csv', encoding='latin', index_col=0)
  deflactors = pd.read_csv('https://raw.githubusercontent.com/miguellosoyo/financial_statements/main/Cifras%20del%20PIB%20Nominal-Real.csv?token=GHSAT0AAAAAABZLORHNL6MJFQW3TAC2CBHIY3JMASA', encoding='latin', index_col=0)
  
  # Establecer el índice de precios base 2013
  deflactors['INPC'] = deflactors['PIB Nominal'].div(deflactors['PIB Real'])

  # Calcular el deflactor 
  deflactors['Deflactor'] = deflactors['INPC'].div(deflactors.loc[year, 'INPC'])

  # Devolver la serie del deflactor
  return deflactors['Deflactor']

# Crear una función para deflactar información
def deflact_values(df:pd.DataFrame, var_id:str, columns:list, deflactors):

  # Iterar cada año contenido dentro de la base de datos
  for year in df[f'{var_id}'].unique():

    # Definir las variables a deflactar
    columns = df.columns.tolist()[2:]

    # Filtrar información por año y dividir entre el deflactor que corresponde
    
    df.loc[df['Año']==year, columns] = df.loc[df['Año']==year, columns].div(deflactors[year])

  # Regresar la información
  return df

# Crear una función para deflactar información
def inverse_deflact_values(df:pd.DataFrame, var_id:str, columns:list):

  # Calcular el deflactor que tenga como base el año 2020
  deflactors_1 = deflactor_serie(2020)

  # Iterar cada año contenido dentro de la base de datos
  for year in df[f'{var_id}'].unique():

    # Definir las variables a deflactar
    columns = df.columns.tolist()[2:]

    # Filtrar información por año y dividir entre el deflactor que corresponde
    
    df.loc[df['Año']==year, columns] = df.loc[df['Año']==year, columns].multiply(deflactors_1[year])

  # Regresar la información
  return df

# Definir una función que ilumine una fila sí y otra no de un color en específico
def highlight(x):

  # Definir los colores para las filas impares y pares
  c1 = 'background-color: #dedede'
  c2 = 'background-color: white'

  # Definir un DataFrame con el mapeo de los colores
  df1 = pd.DataFrame('', index=x.index, columns=x.columns)
  df1.loc[df1.index%2!=0, :] = c1
  df1.loc[df1.index%2==0, :] = c2
  return df1  

# Crear una función para calcular la TIR
def irr(values, guess=0.1, tol=1e-12, maxiter=100):
    
  # Convertir los valores integrados a un vector de una dimensión
  values = np.atleast_1d(values)
  
  # Evaluar que sea un vector unidimensional
  if values.ndim != 1:
      raise ValueError("Cashflows must be a rank-1 array")

  # Evaluar que los valores sean mayores a 0
  same_sign = np.all(values > 0) if values[0] > 0 else np.all(values < 0)
  if same_sign:
      return np.nan

  # Crear una función polinómica con los valores
  npv_ = np.polynomial.Polynomial(values)
  
  # Aplicar su derivada
  d_npv = npv_.deriv()
  x = 1 / (1 + guess)

  # Iterar sobre las derivadas hasta obtener la TIR
  for _ in range(maxiter):
      x_new = x - (npv_(x) / d_npv(x))
      if abs(x_new - x) < tol:
          return 1 / x_new - 1
      x = x_new

  # Devolver valor nulo en caso de no hallar la TIR
  return np.nan

# Definir usuarios y contraseñas
names = ['César','Angélica', 'Paola', 'Edith']
usernames = ['cesar_artf','angelica_artf', 'paola_artf', 'edith_artf']
passwords = ['Sandía99.','Sandía99.', 'Sandía99.', 'Sandía99.']

# Definir variables vacías para usuario y contraseña
username = '' 
password = ''

# Generar el objeto de autenticación
with st.sidebar:
  
  # Definir un cuadro expansivo
  expander = st.expander('Login')

  # Integrar título del área de login
  expander.header('Iniciar Sesión')

  # Incorprar el cuadro de ingreso del usuario
  username = expander.text_input('Usuario')

  # Incorprar el cuadro de ingreso de la 
  password = expander.text_input('Contraseña', type='password')

# Obtener los datos que ingresará el usuario
if username=='' and password=='':
  authentication_status = None
else:
  authentication_status = (username in usernames) & (password in passwords)

# Evaluar los eventos identificados durante el login
if authentication_status:
  
  # Integrar a la barra lateral la selección de tipo de análisis
  with st.sidebar:
    
    # Definir un cuadro expansivo
    expander_analysis = st.expander('Tipos de Análisis')
  
    # Definir un menú de selección para los concesionarios
    expander_analysis.subheader('Tipos de Análisis')
    analysis_elements = sorted(('Estados Financieros', 'Análisis de Inversiones',))
    analysis = expander_analysis.radio('Selección de Análisis', options=analysis_elements)

    # Definir un cuadro expansivo para la selección del tipo de saldos
    expander_deflact = st.expander('Deflactores')

    # Integrar título del área de login
    expander_deflact.header('Variables para Deflactar')

    # Colocar cuadros de selección para las tareas de Saldos Corrientes o Deflactados
    ammounts = expander_deflact.radio('Tipo de Saldos', options=['Saldos Corrientes', 'Saldos Constantes'])
        
    # Evaluar si los saldos serán corrientes
    if ammounts=='Saldos Corrientes':
      
      # Importar la información de los deflactores
      deflactors = deflactor_serie(2020)

    elif ammounts=='Saldos Constantes':
    
      # Incorprar el cuadro de ingreso del usuario
      year_deflact = expander_deflact.selectbox('Seleccione el Año Base', options=sorted(range(1997,2022), reverse=True))

      # Importar la información de los deflactores
      deflactors = deflactor_serie(year_deflact)    
  
  # Evaluar si es un análisis financiero el que se quiere realizar
  if analysis=='Estados Financieros':

    # Integrar a la barra lateral la selección de concesionarios y tipo de reporte
    with st.sidebar:

      # Definir un menú de selección para los concesionarios
      st.subheader('Concesionarios')
      licensee_elements = sorted(['KCSM', 'Ferrosur', 'Ferromex'])
      licensee = st.selectbox(label='Selección de Concesionarios', options=licensee_elements)

      # Definir un menú de selección para los diferentes reportes financieros
      st.subheader('Reportes Financieros')
      report_elements = ['Balance General', 'Estado de Resultados', 'Estado de Flujos de Efectivo']
      report = st.selectbox(label='Selección de Reporte Financiero', options=report_elements)

    # Evaluar el tipo de reporte seleccionado
    if report=='Balance General':
      try:
        data = pd.read_csv(f'https://raw.githubusercontent.com/miguellosoyo/financial_statements/main/{licensee}%20ESF.csv?token=GHSAT0AAAAAABZLORHNL6MJFQW3TAC2CBHIY3JMASA', encoding='utf-8', index_col=0, na_values='-').fillna(0)
      except:
        data = pd.read_csv(f'https://raw.githubusercontent.com/miguellosoyo/financial_statements/main/{licensee}%20ESF.csv?token=GHSAT0AAAAAABZLORHNL6MJFQW3TAC2CBHIY3JMASA', encoding='latin', index_col=0, na_values='-').fillna(0)
      
    elif report=='Estado de Resultados':
      try:
        data = pd.read_csv(f'https://raw.githubusercontent.com/miguellosoyo/financial_statements/main/{licensee}%20ERI.csv?token=GHSAT0AAAAAABZLORHNL6MJFQW3TAC2CBHIY3JMASA', encoding='utf-8', index_col=0, na_values='-').fillna(0)
      except:
        data = pd.read_csv(f'https://raw.githubusercontent.com/miguellosoyo/financial_statements/main/{licensee}%20ERI.csv?token=GHSAT0AAAAAABZLORHNL6MJFQW3TAC2CBHIY3JMASA', encoding='latin', index_col=0, na_values='-').fillna(0)
    elif report=='Estado de Flujos de Efectivo':
      try:
        data = pd.read_csv(f'https://raw.githubusercontent.com/miguellosoyo/financial_statements/main/{licensee}%20ERI.csv?token=GHSAT0AAAAAABZLORHNL6MJFQW3TAC2CBHIY3JMASA', encoding='utf-8', index_col=0, na_values='-').fillna(0)
      except:
        data = pd.read_csv(f'https://raw.githubusercontent.com/miguellosoyo/financial_statements/main/{licensee}%20ERI.csv?token=GHSAT0AAAAAABZLORHNL6MJFQW3TAC2CBHIY3JMASA', encoding='latin', index_col=0, na_values='-').fillna(0)
    # Obtener los periodos de estudio
    years = data.columns.tolist()

    # Integrar a la barra lateral una línea de selección de periodos
    with st.sidebar:

      # Definir una línea de selección de periodos
      st.subheader('Periodo de Selección')
      range_years = st.slider('Seleccione el rango de años a analizar', int(years[0]), int(years[-1]), (int(years[0]), int(years[-1])))
      years = [str(x) for x in range(range_years[0],range_years[-1]+1)]

    # Eliminar espacios en blanco de los encabezados y conceptos
    data.reset_index(inplace=True)
    data.columns = [x.strip() for x in data.columns]
    data = data[['Concepto']+years]
    columns = data.columns.tolist()
    data['Concepto'] = [x.strip() for x in data['Concepto'].values]

    # Definir la variable de comparación en caso de requerir Análisis Vertical
    variable = data['Concepto'][0]

    # Definir elementos de la página
    st.title('Información Financiera')  

    st.write('''
            Estados Financieros del Concesionario
            ''')

    # Ingresar subtítulo para selección de tipo de análisis
    st.write('''
            ### Seleccione el Tipo de Análisis que quiera visualizar
            ''')

    # Seleccionar Análisis Vertical y Horizontal
    if st.checkbox('Vertical y Horizontal'):
        
      # Hacer una copia de la información
      df = data.copy()
      
      # Columnas de Análisis Vertical
      columns_v = [f'{x} V' for x in years]

      # Calcular el análisis vertical del reporte correspondiente
      denominator = df[df['Concepto']==variable].drop('Concepto', axis=1)
      df[columns_v] = df[years].div(denominator.values, axis=1)
        
      # Columnas de Análisis Horizontal
      columns_h = [f'{int(x)-1}-{x}' for i, x in enumerate(years) if i > 0]

      # Calcular el análisis horizontal
      df[columns_h] = df[years].pct_change(axis=1).iloc[:, 1:]
      
      # Eliminar valores NaN e infinitos
      df.replace([np.inf, -np.inf], np.nan, inplace=True)
      df.fillna(0, inplace=True)
      
      # Aplicar definir formato de la tabla
      format = {x:("{:,.0f}" if i<len(years) else "{:.2%}") for i, x in enumerate(years+columns_v+columns_h)}
        
      # Mostrar información financiera
      st.subheader(f'''
                  Análisis Vertical y Horizontal del {report} de {licensee}
                  ''')
        
    # Evaluar si se requiere calcular el análisis vertical
    elif st.checkbox('Vertical'):
        
      # Hacer una copia de la información
      df = data.copy()
      
      # Columnas de Análisis Vertical
      columns = [f'{x} V' for x in years]

      # Calcular el análisis vertical del reporte correspondiente
      denominator = df[df['Concepto']==variable].drop('Concepto', axis=1)
      df[columns] = df[years].div(denominator.values, axis=1)

      # Eliminar valores NaN e infinitos
      df.replace([np.inf, -np.inf], np.nan, inplace=True)
      df.fillna(0, inplace=True)
      
      # Definir el formato para aplicar en la tabla
      format = {x:("{:,.0f}" if i<len(years) else "{:.2%}") for i, x in enumerate(years+columns)}
        
      # Mostrar información financiera
      st.subheader(f'''
                  Análisis Vertical del {report} de {licensee}
                  ''')
      
    # Seleccionar que se efectue el análisis horizontal
    elif st.checkbox('Horizontal'):
        
      # Hacer una copia de la información
      df = data.copy()
      
      # Columnas de Análisis Horizontal
      columns = [f'{int(x)-1}-{x}' for i, x in enumerate(years) if i > 0]

      # Calcular el análisis horizontal
      df[columns] = df[years].pct_change(axis=1).iloc[:, 1:]
      
      # Eliminar valores NaN e infinitos
      df.replace([np.inf, -np.inf], np.nan, inplace=True)
      df.fillna(0, inplace=True)
      
      # Definir el formato para aplicar en la tabla
      format = {x:("{:,.0f}" if i<len(years) else "{:.2%}") for i, x in enumerate(years+columns)}
        
      # Mostrar información financiera
      st.subheader(f'''
                  Análisis Vertical del {report} de {licensee}
                  ''')

    # En caso de no seleccionar ninguna opción, mostrar la información
    else:
        
      # Definir el tipo de formato para aplicar en la tabla
      df = data.copy()
      format = {x:("{:,.0f}" if i < len(years) else "{:.2%}") for i, x in enumerate(years)}
      
      # Mostrar información financiera
      st.subheader(f'''
                  Estado de Resultados de {licensee}
                  ''')

    # Aplicar el formato definido en el caso respectivo, y esconder el índice de números consecutivos
    df = df.style.apply(highlight, axis=None).set_properties(**{'font-size': '10pt', 'font-family': 'monospace', 'border': '', 'width': '110%'}).format(format)

    # Definir las propiedades de estilo para los encabezados
    th_props = [
                ('font-size', '12pt'),
                ('text-align', 'center'),
                ('font-weight', 'bold'),
                ('color', 'white'),
                ('background-color', '#328f1d')
                ]

    # Definir las propiedades de estilo para la información de la tabla
    td_props = [
                ('font-size', '8pt'),
                ('width', '110%'),
                ]

    # Integrar los estilos en una variable de estilos
    styles = [
              dict(selector='th', props=th_props),
              dict(selector='td', props=td_props)
              ]

    # Aplicar formatos
    df.set_table_styles(styles)

    # Definir formato CSS para eliminar los índices de la tabla, centrar encabezados, aplicar líneas de separación y cambiar tipografía
    hide_table_row_index = """
                            <style>
                            tbody th {display:none;}
                            .blank {display:none;}
                            .col_heading {font-family: monospace; border: 3px solid white; text-align: center !important;}
                            </style>
                          """

    # Integrar el CSS con Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)

    # Integrar el DataFrame a la aplicación Web
    # df.data.set_index('Concepto', inplace=True)
    st.table(df)

    # Insertar una nota al pie de la tabla
    st.caption(f'Información financiera de {licensee}.')

  # Evaluar si es un análisis de inversiones
  elif analysis=='Análisis de Inversiones':
    
    # Integrar a la barra lateral la selección de concesionarios, campo para poner la tasa de descuento y la lista de variables para inversiones y flujos de efectivo
    with st.sidebar:
      
      # Integrar un subtitulo
      st.subheader('Parámetros de Selección')
      
      # Importar información de las inversiones de los concesionarios
      investments = pd.read_csv(f'https://raw.githubusercontent.com/miguellosoyo/financial_statements/main/IRR/Investments.csv?token=GHSAT0AAAAAABZLORHNL6MJFQW3TAC2CBHIY3JMASA', encoding='latin', na_values='-').fillna(0)
      investments = pd.read_csv(f'https://raw.githubusercontent.com/miguellosoyo/financial_statements/main/IRR/Investments%20Mod.csv?token=GHSAT0AAAAAABZLORHNL6MJFQW3TAC2CBHIY3JMASA', encoding='latin', na_values='-').fillna(0)
      
      # Importar información de los flujos de efectivo de los concesionarios
      cash_flows = pd.read_csv(f'https://raw.githubusercontent.com/miguellosoyo/financial_statements/main/IRR/Cash%20Flows.csv?token=GHSAT0AAAAAABZLORHNL6MJFQW3TAC2CBHIY3JMASA', encoding='utf-8', na_values='-').fillna(0)
      cash_flows = pd.read_csv(f'https://raw.githubusercontent.com/miguellosoyo/financial_statements/main/IRR/Cash%20Flows%20Mod.csv?token=GHSAT0AAAAAABZLORHNL6MJFQW3TAC2CBHIY3JMASA', encoding='utf-8', na_values='-').fillna(0)

      # Evaluar si se pide deflactar o no
      if ammounts=='Saldos Constantes':

        # Inversiones
        columns = investments.columns.tolist()[:2]
        investments = inverse_deflact_values(investments, 'Año', columns)
        investments = deflact_values(investments, 'Año', columns, deflactors)
        
        # Flujos de efectivo
        columns = cash_flows.columns.tolist()[:2]
        cash_flows = inverse_deflact_values(cash_flows, 'Año', columns)
        cash_flows = deflact_values(cash_flows, 'Año', columns, deflactors)

      # Definir un menú de selección para los concesionarios
      licensee_elements = sorted(['KCSM', 'Ferrosur', 'Ferromex'])
      licensee = st.selectbox(label='Selección de Concesionarios', options=licensee_elements)
      
      # Definir una línea de selección de 
      years = [cash_flows[cash_flows["Concesionario"]==licensee.upper()]['Año'].min(), cash_flows[cash_flows["Concesionario"]==licensee.upper()]['Año'].max()]
      range_years = st.slider('Seleccione el Rango de Años a Analizar', int(years[0]), int(years[-1]), (int(years[0]), int(years[-1])))
      years = list(range(range_years[0],range_years[-1]+1))

      # Definir el campo para ingresa la tasa de descuento
      dr = st.number_input('Ingresar la Tasa de Descuento', min_value=0., max_value=100., value=7.32)/100
      
      # Definir una lista con la selección de inversiones
      inv_type = st.selectbox(label='Seleccione el Tipo de Inversión a Analizar', options=[x for x in investments.columns[2:].tolist() if not 'Acumulada' in x])

      # Definir una lista con la selección de flujos de efectivo
      cf_type = st.selectbox(label='Seleccione el Tipo de Flujo de Efectivo a Analizar', options=sorted(['Ingresos Totales', 'NOPAT', 'Utilidad de  Operación', 'Utilidad Neta']))
      
      # Importar información del WACC
      wacc = pd.read_csv('https://raw.githubusercontent.com/miguellosoyo/financial_statements/main/IRR/WACC.csv?token=GHSAT0AAAAAABZLORHNL6MJFQW3TAC2CBHIY3JMASA', encoding='utf-8', na_values='-').fillna(0)
      
      # Integrar una lista de los años disponibles del WACC
      year = st.selectbox(label='Seleccione el Año del que Desea el WACC', options=sorted(wacc['Año'].unique().tolist(), reverse=True)[1:])
        
    # Filtrar DataFrames por periodo seleccionado
    investments = investments[(investments['Año'].isin(years)) & (investments['Concesionario']==licensee.upper())]
    cash_flows = cash_flows[(cash_flows['Año'].isin(years)) & (cash_flows['Concesionario']==licensee.upper())]
    
    # Filtrar información por concesionario y seleccionar las variables de interés
    df_inv = investments[['Año', inv_type]].reset_index(drop=True).copy().set_index('Año')
    df_cf = cash_flows.reset_index(drop=True).copy().set_index('Año')
    
    # Calcular NOPAT
    df_cf['NOPAT'] = df_cf['Utilidad de Operación']*(1-0.3)
    
    # Obtener el dato del WACC del concesionario
    wacc_value = wacc[(wacc['Concesionario']==licensee.upper()) & (wacc['Año']==year)]['WACC'].values[0]
    
    # Concatenar información
    df = pd.concat([df_inv, df_cf], axis=1).fillna(0)

    # Calcular los flujos de efectivo
    df['Flujos de Efectivo'] = df[cf_type] + df['Amortización y Depreciación'] - df[inv_type] - df['Pago Concesión']
      
    # Obtener los flujos de efectivo descontados
    dcf = []
    for i, x in enumerate(df['Flujos de Efectivo'].values):
      
      # Descontar los flujos de efectivo y asignarlos
      dcf.append(x/((1+dr)**i))
      
    # Integrar los flujos de efectivo descontados al DataFrame
    df['Flujos de Efectivo Descontados'] = dcf

    # Calcular la Tasa Interna de Retorno con los FLujos de Efectivo
    irr = irr(df['Flujos de Efectivo'].tolist())
    
    # Importar información para el cálculo de la tasa de reinversión
    try:
      balance = pd.read_csv(f'https://raw.githubusercontent.com/miguellosoyo/financial_statements/main/{licensee}%20ESF.csv?token=GHSAT0AAAAAABZLORHNL6MJFQW3TAC2CBHIY3JMASA', encoding='utf-8', index_col=0, na_values='-').fillna(0)
    except:
      balance = pd.read_csv(f'https://raw.githubusercontent.com/miguellosoyo/financial_statements/main/{licensee}%20ESF.csv?token=GHSAT0AAAAAABZLORHNL6MJFQW3TAC2CBHIY3JMASA', encoding='latin', index_col=0, na_values='-').fillna(0)
    
    # Calcular VPN
    vpn = df['Flujos de Efectivo Descontados'].sum()
    
    # Calcular la tasa de reinversión (TRI) acumulada
    capex = df.loc[year, inv_type]
    am = df.loc[year, 'Amortización y Depreciación']
    non_cash_wc = (balance.loc['Activo circulante', f'{year}'] - balance.loc['Efectivo y equivalentes de efectivo', f'{year}'])
    nopat = df.loc[year, 'NOPAT']
    rir = (capex - am + non_cash_wc) / nopat
    
    # Transponer DataFrame para presentar
    df = df[['Pago Concesión', inv_type, cf_type, 'Amortización y Depreciación', 'Flujos de Efectivo', 'Flujos de Efectivo Descontados']].T
    df.reset_index(inplace=True)

    # Renombrar columna de índice
    df.columns = [str(x) for x in df.columns]
    df.rename(columns={'index':'Concepto'}, inplace=True)

    # Definir el formato para aplicar en la tabla
    columns = df.columns.tolist()[1:]

    # Definir el formato para aplicar en la tabla
    format = {x:"{:,.0f}" for i, x in enumerate(columns)}

    # Aplicar el formato definido en el caso respectivo, y esconder el índice de números consecutivos
    df = df.style.apply(highlight, axis=None).set_properties(**{'font-size': '10pt', 'font-family': 'monospace', 'border': '', 'width': '110%'}).format(format)

    # Definir las propiedades de estilo para los encabezados
    th_props = [
                ('font-size', '12pt'),
                ('text-align', 'center'),
                ('font-weight', 'bold'),
                ('color', 'white'),
                ('background-color', '#328f1d')
                ]

    # Definir las propiedades de estilo para la información de la tabla
    td_props = [
                ('font-size', '8pt'),
                ('width', '110%'),
                ]

    # Integrar los estilos en una variable de estilos
    styles = [
              dict(selector='th', props=th_props),
              dict(selector='td', props=td_props)
              ]

    # Aplicar formatos
    df.set_table_styles(styles)

    # Definir formato CSS para eliminar los índices de la tabla, centrar encabezados, aplicar líneas de separación y cambiar tipografía
    hide_table_row_index = """
                            <style>
                            tbody th {display:none;}
                            .blank {display:none;}
                            .col_heading {font-family: monospace; border: 3px solid white; text-align: center !important;}
                            </style>
                          """
    
    # Integrar métricas de WACC, TIR, tasa de reinversión (TRI), diferencia entre TIR y WACC, diferencia entre TRI y WACC
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric('VPN (Saldos en MM)', f'$ {round(vpn/1000000,1)}')
    col2.metric('WACC', f'{round(wacc_value*100,1)}%')
    col3.metric('TIR', f'{round(irr*100,1)}%')
    col4.metric('TIR - WACC', f'{round((irr-wacc_value)*100,1)}%')
    col5.metric('TRI', f'{round(rir,1)}')
    
    # Integrar el CSS con Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)
    
    # Mostrar información financiera
    st.subheader(f'''
                Flujos de Efectivo de {licensee}
                ''')
    
    # Integrar el DataFrame a la aplicación Web
    st.table(df)

    # Insertar una nota al pie de la tabla
    st.caption(f'Información financiera de {licensee}.')
    
    # Integrar un título y subtitulo para el gráfico
    st.subheader(f"Componentes del Flujo de Efectivo",)
    st.text(f"Información Financiera de {licensee}")
    
    # Definir las especificaciones de una gráfica de barras apiladas 
    options = {
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "legend": {"data": df.data['Concepto'].tolist()},
            "grid": {"left": "5%", "right": "15%", "bottom": "5%", "containLabel": True},
            "yAxis": {"type": "value",},
            "xAxis": {
                "type": "category",
                "data": df.data.columns.tolist()[1:],
                },
            "series": [{"name": f"{x}",
                        "type": "bar",
                        "stack": "total",
                        "emphasis": {"focus": "series"},
                        "data": df.data.loc[df.data['Concepto']==x,:].round(2).values[0][1:].tolist(),
                        } for x in df.data['Concepto'].tolist()
                        ],
            }
    
    # Integrar gráfica de barras
    st_echarts(options=options, height="400px")
    
    # Integrar un título y subtitulo para el gráfico
    st.subheader(f"Evolución de los Conceptos de Inversión",)
    st.text(f"Información Financiera de {licensee}")
    
    # Definir las especificaciones de un gráfico de área
    options = {"xAxis": {"type": "category",
                             "data": investments['Año'].tolist(),
                             },
               "yAxis":{"type": "value"},
               "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
               "series": [{"name": f"{x}",
                           "type": "line",
                           "areaStyle": {},
                           "stack": "Total",
                           "emphasis": {"focus": "series"},
                           "data": investments[x].round(2).values.tolist(),
                           } for x in [i for i in investments.columns if 'Anual' in i]
                          ],
               "legend": {
                   "data": [i for i in investments.columns if 'Anual' in i],
                   },
               }
    
    # Integrar gráfica de área
    st_echarts(options=options, height="400px")
    
    # Integrar un título y subtitulo para el gráfico
    st.subheader(f"Contraste Factor de Ingreso e Inversión",)
    st.text(f"Información Financiera de {licensee}")

    # Definir los colores a asignar a las barras y línea, respectivamente
    colors = ['#C7A479', '#1E5847']
    
    # Definir las especificaciones de un gráfico de barras y línea
    options = {"color": colors,
               "tooltip":{
                   "trigger": "axis", "axisPointer": {"type": "shadow"}
                   },
               "grid":{
                   "right": "20%",
                   },
               "legend":{
                   "data": [inv_type, cf_type],
                   },
               "xAxis":[
                        {"type": "category",
                         "axisTick":{
                             "alignWithLabel":True,
                             },
                         "data": investments['Año'].tolist(),
                         },
                        ],
               "yAxis":[
                        {"type": "value",
                         "name": f"{inv_type}",
                         "position": "right",
                         "alignTicks": True,
                         "axisLine":{
                             "show": True,
                             "lineStyle": {
                                 "color": colors[0]
                                 }
                                 },
                         },
                        {"type": "value",
                         "name": f"{cf_type}",
                         "position": "left",
                         "alignTicks": True,
                         "axisLine": {
                         "show": True,
                         "lineStyle": {
                             "color": colors[1]
                             }
                             },
                         }
                        ],
               "series":[
                         {"name": f'{inv_type}',
                          "type": "bar",
                          "data": investments[inv_type].values.tolist()
                          },
                         {"name": f"{cf_type}",
                          "type": "line",
                          "yAxisIndex": 2,
                          "data": cash_flows[cf_type].values.tolist()
                          }
                         ]
               }
    
    # Integrar gráfica de barras y línea
    st_echarts(options=options, height="500px")

# Evaluar si son incorrectos los datos de ingreso
elif authentication_status==False:
  st.error('Usuario/Contraseña son incorrectos')
elif authentication_status==None:
  st.warning('Por favor, introduzca su usuario y contraseña')
