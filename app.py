import pandas as pd
import geopandas as gpd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
import streamlit_js_eval
import requests
import folium
from streamlit_folium import st_folium, folium_static

# Configurações da página
st.set_page_config(
    page_title="Buscador de soros antiveneno",
    page_icon="	:snake:",
    layout="wide",
    initial_sidebar_state='collapsed'
)
col1, col2, col3 = st.columns([1,4,1])

col1.image('https://github.com/andrejarenkow/PainelOvitrampas/blob/main/logo_cevs%20(1).png?raw=true', width=200)
col2.title('Buscador de soros antiveneno')
col3.image('https://github.com/andrejarenkow/PainelOvitrampas/blob/main/logo_estado%20(3).png?raw=true', width=300)

#dicionario soros
dicionario_explicacao = {
    "SAB - Soro antibotrópico" : ": Esse antídoto é usado para tratamento de envenenamento por serpentes do gênero Bothrops sp. No Rio Grande do Sul encontramos: Bothrops jararaca (jararaca), Bothrops pubescens (jararaca-pintada), Bothrops alternatus (cruzeira), Bothrops diporus (jararaca-pintada) e Bothrops cotiara (cotiara)",
    "SAC - Soro anticrotálico" : ": Esse antídoto é usado para tratamento de envenenamento por serpentes do gênero Crotalus sp. No Rio Grande do Sul temos a Crotalus durissus (cascavel).",
    "SAEl - Soro antielapídico" : ": Esse antídoto é usado para tratamento de envenenamento por serpentes do gênero Micrurus sp. No Rio Grande do Sul encontramos a Micrurus altirostris (coral-verdadeira).",
    "SAEsc - Soro antiescorpiônico" : ": Esse antídoto é usado para tratamento de envenenamento por escorpiões do gênero Tityus sp. No Rio Grande do Sul, é utilizado principalmente para tratamento de envenenamento por Tityus serrulatus (escorpião-amarelo).",
    "SAAr - Soro antiaracnídico" : ": Esse antídoto é usado para tratamento de envenenamento por aranhas dos gêneros Phoneutria sp. (aranha-armadeira), Loxosceles sp (aranha-marrom), e escorpiões do gênero Tityus sp.",
    "SALon - Soro antilonômico" : ": Esse antídoto é usado para tratamento de envenenamento por lagartas do gênero Lonomia sp. (taturana)."
}

#dicionario_imagens = {
    #"SAAr - Soro antiaracnídico" : "st.image('', caption='Phoneutria')"

if st.checkbox('Buscar minha localização atual'):
    try:
        loc = streamlit_js_eval.get_geolocation()
        location_json = streamlit_js_eval.get_page_location()
        lat = str(loc['coords']['latitude'])
        long = str(loc['coords']['longitude'])
        url = f'https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={long}'
        localizacao_usuario = requests.get(url)
        loc_usuario = localizacao_usuario.text
        index_inicio = loc_usuario.find('"city":')
        index_fim = loc_usuario.find(',"municipality"')
        municipio_do_usuario = loc_usuario[index_inicio+8:index_fim-1]
    except:
        st.error('Permita o uso da sua localização atual clicando em PERMITIR!')
else:
    municipio_do_usuario = ''
#unificando nomes de municipios
dicionario = {"Restinga Seca": "Restinga Sêca",
    "Santana do Livramento": "Sant'Ana do Livramento","Santo Antônio Das Missões":"Santo Antônio das Missões", "São Pedro Das Missões":"São Pedro das Missões"}


dados_geral = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vTeWn7SmYQbdwulQtkslW2OeNEV-XGEPVcAnlUI1QnnstfjxpUgHgSl3cOrUsX0qlJ6Q9Ef7MvPAUOf/pub?gid=669334724&single=true&output=csv')

municipios = gpd.read_file('https://raw.githubusercontent.com/andrejarenkow/geodata/main/municipios_rs_CRS/RS_Municipios_2021.json')
municipios['geometry'] = municipios['geometry'].simplify(tolerance = 0.01)
municipios["NM_MUN"] = municipios["NM_MUN"].replace(dicionario)

lista_mun_distinct = sorted(municipios['NM_MUN'].unique())
try:
    if municipio_do_usuario!='':
        lista_mun_distinct.remove(municipio_do_usuario)
        lista_mun_distinct.insert(0,municipio_do_usuario)
except:
     pass
#municipios
col5, col4 = st.columns([3, 4]) 
with col5:  
    animal = st.selectbox("Por qual animal o paciente foi picado?", dados_geral['Animal'].unique(), index=None, placeholder="Selecione o animal")
    soro = st.selectbox('Soro Antiveneno', dados_geral[dados_geral['Animal']==animal]['soro'].unique(), index=None, placeholder="Selecione o Soro Antiveneno")
        
    try: 
        container = st.container(border=True)
        with container: 
         st.write(soro, dicionario_explicacao[soro])
    except: 
        st.write("")

    mun_origem = st.selectbox('Município onde está o paciente', lista_mun_distinct, index=None, placeholder="Selecione o município onde está o paciente")
    #if mun_origem==municipio_do_usuario:
       # mun_origem = municipio_do_usuario
#try:
        
    #Filtro destino
    filtro = (dados_geral['soro'] == soro)&(dados_geral['Origin'] == mun_origem)
    municipios_soro = dados_geral[filtro]
    municipios_soro['Legenda'] = 'Origem'
    
    municipios_soro = municipios_soro.dropna()
    
    mun_destino = municipios_soro.dropna()['Município destino'].values[0]
        
    filtro_destino = (dados_geral['soro'] == soro)&(dados_geral['Origin'] == mun_destino)
    municipio_destino = dados_geral[filtro_destino].dropna()
    municipio_destino['Legenda'] = 'Destino'
    
    #municipios_soro_destino = pd.concat([municipio_destino, municipios_soro])
    #municipios_soro_destino = municipios_soro_destino.dropna()
    
    #map_fig = px.choropleth_mapbox(municipios_soro_destino, geojson=municipios_soro_destino.geometry,
                              #locations=municipios_soro_destino.index, color='Legenda',
                              #center = {'lat': municipios_soro_destino['Latitude'].values[0], 'lon': municipios_soro_destino['Longitude'].values[0]},
                              #center ={'lat':municipios_soro_destino.geometry.centroid.y.values[0], 'lon':municipios_soro_destino.geometry.centroid.x.values[0]},
                              #zoom=7.5,
                              #mapbox_style="open-street-map",
                              #hover_name='NM_MUN',
                              #hover_data =['Destination', 'Município destino'],
                              #color_discrete_sequence = ['red', 'green'],
                              #height = 700, opacity = 0.6,)
    
    mapa = folium.Map([-30, -50], zoom_start=12)

    folium.Marker(
        location= [municipios_soro['Latitude_destino'].values, municipios_soro['Longitude_destino'].values],
        #tooltip="Click me!",
        #popup="Mt. Hood Meadows",
        icon=folium.Icon(color="red"),
    ).add_to(mapa)
    
    #folium.Marker(
        #location=['Latitude_origem', 'Longitude_origem'],
        #tooltip="Click me!",
        #popup="Timberline Lodge",
        #icon=folium.Icon(color="green"),
    #).add_to(mapa)


    with col4: 
        st_data = folium_static(mapa, width=1000, height=600)
    with col5:
        mun_destino = municipios_soro.dropna()['Município destino'].values[0]
        distancia = municipios_soro.dropna()['shortest way (km)'].values[0]
        local = municipios_soro.dropna()['Destination'].values[0]
        endereco = municipios_soro.dropna()['Endereço'].values[0]
        telefone = municipios_soro.dropna()['Telefone'].values[0]
        container_respostas = st.container(border=True)
        with container_respostas: 
            st.write(f'Município onde está o soro mais próximo: **{mun_destino}**')
            st.write(f'Local: **{local}**')
            st.write(f'Endereço: **{endereco}**')
            st.write(f'Telefone: **{telefone}**')
            st.write(f'Distância: **{distancia} km**')
            st.write('**ATENÇÃO**: ligue para o local para fazer a confirmação da disponibilidade do soro.')
            municipios_soro_destino
