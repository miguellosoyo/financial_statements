# Importar librerías de trabajo
# from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
import streamlit as st
import numpy as np
import pandas as pd
import os

# Definir las opciones de pandas para visualizar todos los registros y columnas
pd.options.display.max_rows = None
pd.options.display.max_columns = None

# Integrar a la barra lateral la selección de tipo de análisis
with st.sidebar:

  # Definir un menú de selección para los concesionarios
  st.subheader('Tipos de Análisis')
  analysis_elements = ('Estados Financieros', 'Análisis de Inversiones',)
  analysis = st.radio('Selección de Análisis', options=analysis_elements)

if analysis=='Estados Financieros':
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

  # Integrar a la barra lateral la selección de concesionarios y tipo de reporte
  with st.sidebar:

    # Definir un menú de selección para los concesionarios
    st.subheader('Concesionarios')
    licensee_elements = sorted(['KCSM', 'Ferrosur', 'Ferromex'])
    licensee = st.selectbox(label='Selección de Concesionarios', options=licensee_elements)

    # Definir un menú de selección para los diferentes reportes financieros
    st.subheader('Reportes Financieros')
    report_elements = ['Balance General', 'Estado de Resultados', 'Flujos de Efectivo']
    report = st.selectbox(label='Selección de Reporte Financiero', options=report_elements)

  # Evaluar el tipo de reporte seleccionado
  if report=='Balance General':
    data = pd.read_csv(f'https://raw.githubusercontent.com/miguellosoyo/financial_statements/main/{licensee}%20ESF.csv', encoding='utf-8', index_col=0, na_values='-').fillna(0)
    
  elif report=='Estado de Resultados':
    data = pd.read_csv(f'https://raw.githubusercontent.com/miguellosoyo/financial_statements/main/{licensee}%20ERI.csv', encoding='utf-8', index_col=0, na_values='-').fillna(0)

  elif report=='Flujos de Efectivo':
    data = pd.read_csv(f'https://raw.githubusercontent.com/miguellosoyo/financial_statements/main/{licensee}%20ERI.csv', encoding='utf-8', index_col=0, na_values='-').fillna(0)
    
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
                Análisis Vertical y Horizontal del Estado de Resultados de {licensee}
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
                Análisis Vertical del Estado de Resultados de {licensee}
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
                Análisis Vertical del Estado de Resultados de {licensee}
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

elif analysis=='Análisis de Inversiones':
  pass


# pd.set_option("max_colwidth", None)
# Exportar en formato Excel
# df.to_excel('/content/drive/MyDrive/ARTF/1. Hojas de Trabajo/Streamlit/Ferromex ERI.xlsx', index=False) 
# df.to_html('/content/drive/MyDrive/ARTF/1. Hojas de Trabajo/Streamlit/Ferromex ERI.html') 
