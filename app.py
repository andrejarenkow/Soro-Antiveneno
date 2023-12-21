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
    page_title="Buscador de Soros Antiveneno no Rio Grande do Sul",
    page_icon="	:snake:",
    layout="wide",
    initial_sidebar_state='collapsed'
)
col1, col2, col3 = st.columns([1,4,1])

col1.image('https://github.com/andrejarenkow/PainelOvitrampas/blob/main/logo_cevs%20(1).png?raw=true', width=200)
col2.title('Buscador de Soros Antiveneno no Rio Grande do Sul')
col3.image('https://github.com/andrejarenkow/PainelOvitrampas/blob/main/logo_estado%20(3).png?raw=true', width=300)

tab1, tab2, tab3 = st.tabs(["Buscador de Soros", "Sobre", "Metodologia"])
                           
with tab1:
    st.header("Buscador de Soros")
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
    
    #if st.checkbox('Buscar minha localização atual'):
    #    try:
    #        loc = streamlit_js_eval.get_geolocation()
    #        location_json = streamlit_js_eval.get_page_location()
    #        lat = str(loc['coords']['latitude'])
    #        long = str(loc['coords']['longitude'])
    #        url = f'https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={long}'
    #        localizacao_usuario = requests.get(url)
    #        loc_usuario = localizacao_usuario.text
    #        index_inicio = loc_usuario.find('"city":')
    #        index_fim = loc_usuario.find(',"municipality"')
    #        municipio_do_usuario = loc_usuario[index_inicio+8:index_fim-1]
    #    except:
    #        st.error('Permita o uso da sua localização atual clicando em PERMITIR!')
    #else:
    #    municipio_do_usuario = ''
    #unificando nomes de municipios
    dicionario = {"Restinga Seca": "Restinga Sêca",
        "Santana do Livramento": "Sant'Ana do Livramento","Santo Antônio Das Missões":"Santo Antônio das Missões", "São Pedro Das Missões":"São Pedro das Missões"}
    
    
    dados_geral = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vTeWn7SmYQbdwulQtkslW2OeNEV-XGEPVcAnlUI1QnnstfjxpUgHgSl3cOrUsX0qlJ6Q9Ef7MvPAUOf/pub?gid=669334724&single=true&output=csv')
    dados_geral['Latitude_origem']=pd.to_numeric(dados_geral['Latitude_origem'].str.replace(',','.'))
    dados_geral['Longitude_origem']=pd.to_numeric(dados_geral['Longitude_origem'].str.replace(',','.'))
    dados_geral['Latitude_destino']=pd.to_numeric(dados_geral['Latitude_destino'].str.replace(',','.'))
    dados_geral['Longitude_destino']=pd.to_numeric(dados_geral['Longitude_destino'].str.replace(',','.'))
    
    municipios = gpd.read_file('https://raw.githubusercontent.com/andrejarenkow/geodata/main/municipios_rs_CRS/RS_Municipios_2021.json')
    municipios['geometry'] = municipios['geometry'].simplify(tolerance = 0.01)
    municipios["NM_MUN"] = municipios["NM_MUN"].replace(dicionario)
    
    lista_mun_distinct = sorted(municipios['NM_MUN'].unique())
    #try:
    #    if municipio_do_usuario!='':
    #        lista_mun_distinct.remove(municipio_do_usuario)
    #        lista_mun_distinct.insert(0,municipio_do_usuario)
    #except:
    #     pass
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
        try:
            
            #Filtro destino
            filtro = (dados_geral['soro'] == soro)&(dados_geral['Origin'] == mun_origem)
            municipio_origem = dados_geral[filtro]
            municipio_origem['Legenda'] = 'Origem'
            
            #municipio_origem = municipio_origem.reset_index(drop=True)
            mun_destino = municipio_origem.dropna()['Município destino'].values[0]
                
            filtro_destino = (dados_geral['soro'] == soro)&(dados_geral['Origin'] == mun_destino)
            municipio_destino = dados_geral[filtro_destino].dropna()
            municipio_destino['Legenda'] = 'Destino'
        
            latitude_media = (municipio_origem['Latitude_origem'].values + municipio_destino['Latitude_destino'].values)/2
            longitude_media = (municipio_origem['Longitude_origem'].values + municipio_destino['Longitude_destino'].values)/2
           
            mapa = folium.Map([latitude_media,  longitude_media], zoom_start=9)
        
            folium.Marker(
                location= [municipio_origem['Latitude_origem'].values, municipio_origem['Longitude_origem'].values],
                tooltip="Origem",
                popup="Você está aqui",
                icon=folium.Icon(color="green"),
            ).add_to(mapa)
            
            folium.Marker(
                location= [municipio_destino['Latitude_destino'].values, municipio_destino['Longitude_destino'].values],
                tooltip="Destino",
                popup=f"O soro está aqui, na cidade de {municipio_destino['Município destino'].values[0]}, {municipio_destino['Destination'].values[0]}",
                icon=folium.Icon(color="red"),
             ).add_to(mapa)
            
            #folium.TileLayer('MapQuest Open Aerial').add_to(mapa)
        
            with col4: 
                st.subheader('Hospital mais próximo')
                st_data = folium_static(mapa, width=1000, height=600)
            with col5:
                mun_destino = municipio_origem.dropna()['Município destino'].values[0]
                distancia = municipio_origem.dropna()['shortest way (km)'].values[0]
                local = municipio_origem.dropna()['Destination'].values[0]
                endereco = municipio_origem.dropna()['Endereço'].values[0]
                telefone = municipio_origem.dropna()['Telefone'].values[0]
                container_respostas = st.container(border=True)
                with container_respostas: 
                    st.write(f'Município onde está o soro mais próximo: **{mun_destino}**')
                    st.write(f'Local: **{local}**')
                    st.write(f'Endereço: **{endereco}**')
                    st.write(f'Telefone: **{telefone}**')
                    st.write(f'Distância: **{distancia} km**')
                    st.write('**ATENÇÃO**: ligue para o local para fazer a confirmação da disponibilidade do soro.')
        except:
            with col4:
                if soro:
                    filtro = (dados_geral['soro'] == soro)&(dados_geral['Animal'] == animal)
                    dados_mapa_vazio = dados_geral[filtro]
                
                elif animal:
                    filtro = (dados_geral['Animal'] == animal)
                    dados_mapa_vazio = dados_geral[filtro] 
      
                else:
                    dados_mapa_vazio = dados_geral.copy()
                
                pontos = dados_mapa_vazio.drop_duplicates(['Destination'])
                #pontos['Latitude_destino'] = pontos['Latitude_destino'].astype('float')
                #pontos['Longitude_destino'] = pontos['Longitude_destino'].astype('float')
                #fig = px.scatter_mapbox(pontos,
                #                        lat="Latitude_destino", 
                #                        lon="Longitude_destino", 
                #                        hover_name="Destination",
                #                        zoom=5)
                #fig.update_layout(margin=go.layout.Margin(l=10, r=10, t=10, b=10),paper_bgcolor='rgba(0,0,0,0)',
                #                  mapbox_accesstoken= 'pk.eyJ1IjoiYW5kcmUtamFyZW5rb3ciLCJhIjoiY2xkdzZ2eDdxMDRmMzN1bnV6MnlpNnNweSJ9.4_9fi6bcTxgy5mGaTmE4Pw')
                #st.plotly_chart(fig)
          
                mapa_vazio = folium.Map([-29.492046590850748, -53.10367543293593], zoom_start=6.3)
                
                for latitude, longitude, hospital, endereco  in zip(pontos['Latitude_destino'], pontos['Longitude_destino'], pontos['Destination'], pontos['Endereço']):
                    folium.Marker(
                        location= [latitude, longitude],
                        tooltip=hospital,
                        popup=endereco,
                        icon=folium.Icon(color="red"),
                    ).add_to(mapa_vazio)
                st.subheader('Todos os hospitais')
                st_data = folium_static(mapa_vazio, width=1000, height=600)

with tab2:
    st.header("Sobre")
    texto_sobre =     """
    ### SOBRE
    #### ACIDENTES OFÍDICOS
    
    Os acidentes botrópicos são aqueles causados pelas serpentes do gênero _Bothrops_ sp., sendo as mais comuns a jararaca (_Bothrops jararaca_), a cruzeira (_Bothrops alternatus_) e a jararaca-pintada (_Bothrops pubescens_). Eventualmente, ocorrem acidentes com outras duas espécies mais raras, a _Bothrops diporus_ e a _Bothrops cotiara_. Os acidentes crotálicos são aqueles causados pela cascavel (_Crotalus durissus_). No Rio Grande do Sul, os acientes elapídicos são causados, principalmente, pela _Micrurus altirostris_, uma das várias espécies de corais-verdadeiras encontradas no Brasil, e que está distribuída por todo o estado.
    
    **_Bothrops cotiara_**: Cotiara, jararaca-da-barriga-preta, jararaca-preta. Apresenta coloração castanha esverdeada com desenhos de trapézios. O ventre é preto. Comprimento de, em média, 80 cm. Atividade noturna. Serpente terrícola de baixa densidade populacional, distribui-se ao norte do estado, nas áreas de mata de araucária - ecossistema que já foi amplamente reduzido. Desta forma, a cotiara encontra-se em ameaça de extinção do Rio Grande do Sul. Alimenta-se exclusivamente de pequenos roedores e marsupiais. Veneno de ação proteolítica, coagulante e hemorrágica.
    
    **_Bothrops diporus_**: Jararaca-pintada, jararaca-pintada-argentina. Castanha com desenhos em forma de trapézios. Ventre manchado, semelhante à _B. pubescens_. Pode medir até 1 m. Atividade crepuscular e noturna. Comum em matas e plantações. Bastante adaptada a ambientes modificados pelo homem. Veneno de ação proteolítica, coagulante e hemorrágica.
    
    **_Bothrops jararaca_**: Jararaca, jararaca-comum. Marrom-esverdeada, com desenhos escuros em forma de V invertido. Mede em média 1 m. Atividade crepuscular e noturna. Comum em matas e florestas, principalmente nos remanescentes de Mata Atlântica. Semi-arborícola. Veneno de ação proteolítica, coagulante e hemorrágica.
    
    **_Bothrops alternatus_**: Cruzeira, urutu, urutu-cruzeira, vibora de la cruz. Marrom bronzeado ou esverdeado com desenhos de ferradura ou gancho de telefone de borda branca. Possuem manchas acastanhadas no ventre. Na cabeça, possui um desenho claro de cruz em fundo escuro. Entre 1 e 1,5 m. É a maior e mais robusta dentre as _Bothrops_ sp. do estado. Atividade crepuscular e noturna. Serpente mais robusta, de campo. Vive em locais úmidos e de vegetação baixa. Costuma entrar nas matas ou plantações para se alimentar, exclusivamente, de pequenos roedores e marsupiais. Veneno de ação proteolítica, coagulante e hemorrágica.
    
    **_Bothrops pubescens_**: Jararaca-pintada, jararaca-do-rabo-branco, jararaca-pintada-uruguaia, jararaca-pampeana. Castanha com desenhos em forma de trapézios. Ventre manchado. Mede, em média, 60 cm. Atividade crepuscular e noturna. Espécie comum em campos abertos, como o bioma pampa podendo adentrar nas plantações. É de menor porte e bastante reativa. Veneno de ação proteolítica, coagulante e hemorrágica.
    
    **_Crotalus durissus_**: Cascavel. Marrom amarelada com desenhos de losangos mais claros no dorso e nas laterais. Mede até 1,5 m. Período de atividades durante a tarde e a noite, principalmente no crepúsculo. Vive em locais altos, montanhosos, pedregosos, de campo entremeado com mato e invernos frios. Possuem o crepitáculo (chocalho) de anéis córneos na ponta da cauda que, ao se movimentar durante momentos estressantes, emite o som do choque dos anéis. Dificilmente ataca, e anuncia a sua presença através do som do chocalho. Praticam a caça por espreita - permanecem imóveis no solo esperando a passagem da presa (roedor). Veneno de ação neurotóxica, miotóxica e coagulante.
    
    **_Micrurus altirostris_**: Coral-verdadeira. A espécie tem como característica a presença de anéis pretos e brancos sobre fundo vermelho. Os anéis circundam todo o corpo. Mede até 80 cm. A atividade ocorre principalmente durante o dia, reduzindo até o período da noite. As corais-verdadeiras têm hábitos fossoriais, vivendo em tocas ou buracos embaixo da terra nas matas ou bordas de matas. Não possuem presas especializadas como as Viperidaes, mas pequenos dentes. Precisam morder e segurar a presa para inocular o veneno. Alimentam-se de outras serpentes. Veneno de ação neurotóxica.
    
    #### ACIDENTES POR ARANHAS
    
    Os envenenamentos por aranhas predominam no Rio Grande do Sul com relação aos demais acidentes por animais peçonhentos. Existem duas espécies de aranha de importância médica no estado, cujos envenenamentos podem ser tratados com soro antiveneno: _Loxosceles intermedia_, a aranha-marrom, e _Phoneutria nigriventris_, a aranha-armadeira. 
    
    **_Loxosceles intermedia_**: a aranha-marrom é característica de centros urbanos e pode permanecer dentro das residências, escondidas atrás de mobiliário e, por vezes, no meio das roupas pessoais, roupa de cama e toalhas. Os acidentes ocorrem quando o paciente esmaga a Loxosceles acidentalmente contra o próprio corpo ao se vestir, calçar sapatos ou limpar a casa. Não é uma aranha agressiva e é bastante pequena. O acidente pode levar ao surgimento de áreas de isquemia e necrose na pele, sendo necessário o debridamento tecidual. Pode haver a perda de grandes áreas musculares.
    
    **_Phoneutria nigriventris_**: a armadeira é um aracnídeo de maior tamanho e apresenta comportamento reativo – ao se sentir ameaçada, pode saltar sobre a pessoa ou animal, causando o acidente. A armadeira é mais comum em áreas rurais e pode entrar em galpões, porões, e até nas residências durante o período reprodutivo, entre os meses de março e maio, quando os machos se tornam errantes em busca de fêmeas. O acidente causa dor intensa.
    
    #### ACIDENTES POR ESCORPIÃO
    
    No Rio Grande do Sul há diversas espécies de escorpiões, sendo que a maioria é de baixa toxicidade. Já o _Tityus serrulatus_, conhecido popularmente como escorpião-amarelo, é o responsável pelos acidentes de alta toxicidade e que, em alguns casos, necessidade de tratamento com soro antiescorpiônico ou antiaracnídico.
    
    **_Tityus serrulatus_**: o escorpião-amarelo é exótico no estado, sendo natural de Minas Gerais, e é provável que ele tenha se distribuído por todo o Brasil a partir do transporte humano rodoviário, em meio a produtos como verduras e legumes. Ao chegar em locais novos, se houver alimento (principalmente baratas), água e abrigo o T. serrulatus logo se adapta e se multiplica, tornando-se endêmico. Os principais grupos de risco para acidentes causados por escorpião-amarelo são as crianças e os idosos. Chega, no máximo, a 7 cm de tamanho. Possui o corpo amarelo com detalhes mais escuros no dorso, ponta das pinças e ponta da causa. Ainda, é possível identificá-lo pelas serrilhas presentes na cauda. O veneno do escorpião-amarelo pode causar alterações na frequência cardíaca, respiratória e na pressão arterial.
    
    #### ACIDENTES POR LAGARTA
    
    Existem diversas lagartas urticantes no Rio Grande do Sul, mas a _Lonomia obliqua_, conhecida como taturana, é a única que pode causar acidentes graves com a necessidade do uso de soro antilonômico. 
    
    **_Lonomia obliqua_**: conhecida como taturana, o seu ciclo de vida é de, em média, 150 dias. A fase de lagarta, que representa perigo devido à presença das cerdas urticantes, tem duração de 60 dias. Durante esta fase da vida, as lagartas permanecem agregadas em troncos de árvores durante o dia e, à noite, sobem para as copas para se alimentar de folhas. Por esta característica de permanecerem agregadas, quando um acidente ocorre, o paciente entra em contato com vários animais ao mesmo tempo. O maior perigo deste acidente é a sua toxina, que pode levar à insuficiência renal aguda.

    """
    st.markdown(texto_sobre)
    
with tab3:
    st.header("Metodologia")
    texto_metodologia = """    
    ### METODOLOGIA
    
    A metodologia utilizada na realização e coleta de informações para originar o “Buscador de Soros Antivenenos” foi desenvolvida no Software QGIS, a partir de um processo chamado de Network Analysis, com objetivo de adquirir as distâncias dos municípios do Rio Grande do Sul, ao ponto focal de soro antiveneno mais próximo. Para a idealização do projeto foram utilizados dados shapefile (linhas, pontos e polígonos), ferramentas e plugins do programa QGIS.
    
    Inicialmente foram introduzidos e espacializados os Pontos Focais (locais onde os soros antivenenos se encontram) no software, de forma que fosse possível a visualização dos mesmos no território do estado do Rio Grande do Sul. Estes Pontos Focais foram adquiridos por meio de uma tabela disponibilizada pelo Centro de Informação Toxicológica (CIT). Juntos dos Pontos Focais foram adicionados pontos das sedes municipais do Rio Grande do Sul (estes pontos foram identificados a partir do centro urbano dos municípios), um shapefile das rodovias do RS e um shapefile de polígonos do estado do RS (Figura 1). 
    
    ![Figura 1](https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/imagens_metodologia/figura1.png?raw=true "Figura 1")
    
    Pontos Focais de Soro Antiveneno, em vermelho. Sedes Municipais, em azul. Rodovias do RS, em marrom.
    
    Uma vez com todos os dados organizados, foi possível por meio de ferramentas e plugins do QGIS realizar o Network Analysis, onde foi feito um geoprocessamento dos dados para obter as distâncias das sedes municipais até os Pontos Focais de Soro Antiveneno. O geoprocessamento teve como base o plugin QNEAT3 que criou as distâncias em linha reta dos Pontos Focais até as sedes municipais do estado. Como sabemos que o principal meio de transporte da população é o automóvel, foi realizado uma correção das distâncias para que elas fossem feitas utilizando a rede de rodovias do estado (Figura 2). 
    
    ![Figura 2](https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/imagens_metodologia/figura2.png?raw=true "Figura 2")
    
    Geoprocessamento de Network Analysis realizada para Pontos Focais com Soro Antiveneno SAC.
    Em laranja, a distância do Ponto Focal até a sede municipal de cada município do RS, com base nas rodovias do estado.
    
    Como nem todos Pontos Focais têm em seu estoque todos 6 Soros Antivenenos disponibilizados, o geoprocessamento foi realizado seis vezes, uma vez para cada Soro Antiveneno. Uma vez para Pontos Focais com SAB, uma vez para Pontos Focais com SAC, e assim por diante. (Figura 3)
    
    ![Figura 3](https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/imagens_metodologia/figura3.png?raw=true)
    
    1- Soro antiveneno SAC | 2- Soro antiveneno SAE | 3- Soro antiveneno Saar |
    4- Soro antiveneno SAEsc | 5- Soro antiveneno SAB | 6- Soro antiveneno SALon
    
    Como produto final da metodologia aplicada foram obtidas tabelas dos municípios do Rio Grande do Sul e qual Ponto Focal se localiza mais próximo do mesmo, com distância em km. Foi obtida uma tabela para cada Soro Antiveneno (SAB, SAC, SAE, SAEsc, SALon e Saar). (Figura 4)
    
    ![Figura 4](https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/imagens_metodologia/figura4.png?raw=true "Figura 4")
    
    Exemplo de tabela gerada após o geoprocessamento dos dados.
    Tabela para Soro Antiveneno SAB.
    
    #### Fluxo Metodológico
    
    ![Fluxo Metodológico](https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/imagens_metodologia/fluxo%20metodologico.png?raw=true "Fluxo Metodológico")
    
    """

    st.markdown(texto_metodologia)
