import pandas as pd
import geopandas as gpd
import plotly.express as px
import streamlit as st

# Configurações da página
st.set_page_config(
    page_title="Soro Antiveneno",
    page_icon="	:snake:",
    layout="wide",
    initial_sidebar_state='collapsed'
) 
col1, col2, col3 = st.columns([1,4,1])

col1.image('https://github.com/andrejarenkow/PainelOvitrampas/blob/main/logo_cevs%20(1).png?raw=true', width=200)
col2.title('Soro Antiveneno')
col3.image('https://github.com/andrejarenkow/PainelOvitrampas/blob/main/logo_estado%20(3).png?raw=true', width=300)

#unificando nomes de municipios
dicionario = {"Restinga Seca": "Restinga Sêca",
    "Santana do Livramento": "Sant'Ana do Livramento","Santo Antônio Das Missões":"Santo Antônio das Missões", "São Pedro Das Missões":"São Pedro das Missões"}


dados_geral = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vTeWn7SmYQbdwulQtkslW2OeNEV-XGEPVcAnlUI1QnnstfjxpUgHgSl3cOrUsX0qlJ6Q9Ef7MvPAUOf/pub?gid=669334724&single=true&output=csv')

municipios = gpd.read_file('https://raw.githubusercontent.com/andrejarenkow/geodata/main/municipios_rs_CRS/RS_Municipios_2021.json')
municipios['geometry'] = municipios['geometry'].simplify(tolerance = 0.01)
municipios["NM_MUN"] = municipios["NM_MUN"].replace(dicionario)

#municipios
col5, col4 = st.columns([2, 4]) 
with col5:
    soro = st.selectbox('Selecione o Soro Antiveneno', dados_geral['soro'].unique())
    mun_origem = st.selectbox('Selecione o município de partida', sorted(municipios['NM_MUN'].unique()))
    

#Filtro destino
filtro = (dados_geral['soro'] == soro)&(dados_geral['Origin'] == mun_origem)
municipios_soro = municipios.merge(dados_geral[filtro], left_on='NM_MUN', right_on='Origin', how='left')
municipios_soro['Legenda'] = 'Origem'

municipios_soro = municipios_soro.dropna()

mun_destino = municipios_soro.dropna()['Município destino'].values[0]
filtro_destino = (dados_geral['soro'] == soro)&(dados_geral['Origin'] == mun_destino)
municipio_destino = municipios.merge(dados_geral[filtro_destino], left_on='NM_MUN', right_on='Origin', how='left')
municipio_destino['Legenda'] = 'Destino'

municipios_soro_destino = pd.concat([municipio_destino, municipios_soro])
municipios_soro_destino = municipios_soro_destino.dropna()

map_fig = px.choropleth_mapbox(municipios_soro_destino, geojson=municipios_soro_destino.geometry,
                          locations=municipios_soro_destino.index, color='Legenda',
                          center ={'lat':municipios_soro_destino.geometry.centroid.y.values[0], 'lon':municipios_soro_destino.geometry.centroid.x.values[0]},
                          zoom=7.5,
                          mapbox_style="open-street-map",
                          hover_name='NM_MUN',
                          hover_data =['Destination', 'Município destino'],
                          color_discrete_sequence = ['red', 'green'],
                          height = 700, opacity = 0.6,
                        
                        )

with col4: 
    st.plotly_chart(map_fig, use_container_width=True)
with col5:
    mun_destino = municipios_soro.dropna()['Município destino'].values[0]
    distancia = municipios_soro.dropna()['shortest way (km)'].values[0]
    local = municipios_soro.dropna()['Destination'].values[0]
    st.write(f'Município mais próximo: **{mun_destino}**')
    st.write(f'Local: **{local}**')
    st.write(f'Distância: **{distancia} km**')
    
municipios_soro_destino

