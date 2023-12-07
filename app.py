import pandas as pd
import geopandas as gpd
import plotly.express as px

dicionario = {"Restinga Seca": "Restinga Sêca",
    "Santana do Livramento": "Sant'Ana do Livramento","Santo Antônio Das Missões":"Santo Antônio das Missões", "São Pedro Das Missões":"São Pedro das Missões"}


dados_geral = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vTeWn7SmYQbdwulQtkslW2OeNEV-XGEPVcAnlUI1QnnstfjxpUgHgSl3cOrUsX0qlJ6Q9Ef7MvPAUOf/pub?gid=669334724&single=true&output=csv')

municipios = gpd.read_file('https://raw.githubusercontent.com/andrejarenkow/geodata/main/municipios_rs_CRS/RS_Municipios_2021.json')
municipios['geometry'] = municipios['geometry'].simplify(tolerance = 0.02)
municipios["NM_MUN"] = municipios["NM_MUN"].replace(dicionario)

municipios

soro = 'SALon'
#Saar, SAB, SAC, SAE, SAEsc, SALon
filtro = (dados_geral['soro'] == soro)

municipios_soro = municipios.merge(dados_geral[filtro], left_on='NM_MUN', right_on='Origin', how='left')


map_fig = px.choropleth_mapbox(municipios_soro, geojson=municipios_soro.geometry,
                          locations=municipios_soro.index, color='Município destino',
                          center ={'lat':-30.452349861219243, 'lon':-53.55320517512141},
                          zoom=5.5,
                          mapbox_style="open-street-map",
                          hover_name='NM_MUN',
                          hover_data =['Destination', 'Município destino'],)

map_fig
