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

col1.image('https://github.com/andrejarenkow/csv/blob/master/logo_cevs%20(2).png?raw=true', width=200)
col2.title('Buscador de Soros Antiveneno no Rio Grande do Sul')
col3.image('https://github.com/andrejarenkow/csv/blob/master/logo_estado%20(3)%20(1).png?raw=true', width=300)

tab_emergencia, tab1, tab2, tab3 = st.tabs(['Estoque manual', "Buscador de Soros", "Sobre", "Metodologia"])
                           
with tab1:
    st.header("Buscador de Soros")
    #dicionario soros
    dicionario_explicacao = {
        "SAB - Soro antibotrópico - jararacas, cruzeira, cotiara" : ": Esse antídoto é usado para tratamento de envenenamento por serpentes do gênero Bothrops sp. No Rio Grande do Sul encontramos: Bothrops jararaca (jararaca), Bothrops pubescens (jararaca-pintada), Bothrops alternatus (cruzeira), Bothrops diporus (jararaca-pintada) e Bothrops cotiara (cotiara)",
        "SAC - Soro anticrotálico - cascavel" : ": Esse antídoto é usado para tratamento de envenenamento por serpentes do gênero Crotalus sp. No Rio Grande do Sul temos a Crotalus durissus (cascavel).",
        "SAEl - Soro antielapídico - coral verdadeira" : ": Esse antídoto é usado para tratamento de envenenamento por serpentes do gênero Micrurus sp. No Rio Grande do Sul encontramos a Micrurus altirostris (coral-verdadeira).",
        "SAEsc - Soro antiescorpiônico - escorpião amarelo" : ": Esse antídoto é usado para tratamento de envenenamento por escorpiões do gênero Tityus sp. No Rio Grande do Sul, é utilizado principalmente para tratamento de envenenamento por Tityus serrulatus (escorpião-amarelo).",
        "SAAr - Soro antiaracnídico - armadeira, marrom" : ": Esse antídoto é usado para tratamento de envenenamento por aranhas dos gêneros Phoneutria sp. (aranha-armadeira), Loxosceles sp (aranha-marrom), e escorpiões do gênero Tityus sp.",
        "SALon - Soro antilonômico - taturana" : ": Esse antídoto é usado para tratamento de envenenamento por lagartas do gênero Lonomia sp. (taturana)."
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
        animal = st.selectbox("Qual tipo de animal causou o acidente?", dados_geral['Animal'].unique(), index=None, placeholder="Selecione o animal")
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
    st.header("Tipos de acidente")
    texto_sobre_ofidicos =     """
    ### ACIDENTES OFÍDICOS
    
    Os acidentes botrópicos são aqueles causados pelas serpentes do gênero _Bothrops_ sp., sendo as mais comuns a jararaca (_Bothrops jararaca_), a cruzeira (_Bothrops alternatus_) e a jararaca-pintada (_Bothrops pubescens_). Eventualmente, ocorrem acidentes com outras duas espécies mais raras, a _Bothrops diporus_ e a _Bothrops cotiara_. Os acidentes crotálicos são aqueles causados pela cascavel (_Crotalus durissus_). No Rio Grande do Sul, os acientes elapídicos são causados, principalmente, pela _Micrurus altirostris_, uma das várias espécies de corais-verdadeiras encontradas no Brasil, e que está distribuída por todo o estado.
    """

    st.markdown(texto_sobre_ofidicos)
    
    texto_bothrops_cotiara = """
    **_Bothrops cotiara_**: Cotiara, jararaca-da-barriga-preta, jararaca-preta. Apresenta coloração castanha esverdeada com desenhos de trapézios. O ventre é preto. Comprimento de, em média, 80 cm. Atividade noturna. Serpente terrícola de baixa densidade populacional, distribui-se ao norte do estado, nas áreas de mata de araucária - ecossistema que já foi amplamente reduzido. Desta forma, a cotiara encontra-se em ameaça de extinção do Rio Grande do Sul. Alimenta-se exclusivamente de pequenos roedores e marsupiais. Veneno de ação proteolítica, coagulante e hemorrágica.
    """
    imagem_bothrops_cotiara = 'https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/BCotiara_1.jpg?raw=true'
    
    bothrops_cotiara_container = st.container(border=True)
    with bothrops_cotiara_container:
        texto, imagem = st.columns(2)
        texto.markdown(texto_bothrops_cotiara)
        imagem.image(imagem_bothrops_cotiara, width=500)
    
    
    
    texto_bothrops_diporus = """
    **_Bothrops diporus_**: Jararaca-pintada, jararaca-pintada-argentina. Castanha com desenhos em forma de trapézios. Ventre manchado, semelhante à _B. pubescens_. Pode medir até 1 m. Atividade crepuscular e noturna. Comum em matas e plantações. Bastante adaptada a ambientes modificados pelo homem. Veneno de ação proteolítica, coagulante e hemorrágica.

    """
    bothrops_diporus_container = st.container(border=True)
    with bothrops_diporus_container:
        texto, imagem = st.columns(2)
        texto.markdown(texto_bothrops_diporus)
        imagem.image('https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/Bothrops_diporus_2.jpg?raw=true', width=500)    
       
    
    
    texto_bothrops_jararaca =  """
    **_Bothrops jararaca_**: Jararaca, jararaca-comum. Marrom-esverdeada, com desenhos escuros em forma de V invertido. Mede em média 1 m. Atividade crepuscular e noturna. Comum em matas e florestas, principalmente nos remanescentes de Mata Atlântica. Semi-arborícola. Veneno de ação proteolítica, coagulante e hemorrágica.
"""
    bothrops_jararaca_container = st.container(border=True)
    with bothrops_jararaca_container:
        texto, imagem = st.columns(2)
        texto.markdown(texto_bothrops_jararaca)
        imagem.image('https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/BJararaca_3.jpg?raw=true', width=500)        
 
    texto_bothrops_alternatus = """
    **_Bothrops alternatus_**: Cruzeira, urutu, urutu-cruzeira, vibora de la cruz. Marrom bronzeado ou esverdeado com desenhos de ferradura ou gancho de telefone de borda branca. Possuem manchas acastanhadas no ventre. Na cabeça, possui um desenho claro de cruz em fundo escuro. Entre 1 e 1,5 m. É a maior e mais robusta dentre as _Bothrops_ sp. do estado. Atividade crepuscular e noturna. Serpente mais robusta, de campo. Vive em locais úmidos e de vegetação baixa. Costuma entrar nas matas ou plantações para se alimentar, exclusivamente, de pequenos roedores e marsupiais. Veneno de ação proteolítica, coagulante e hemorrágica.
"""
    bothrops_alternatus_container = st.container(border=True)
    with bothrops_alternatus_container:
        texto, imagem = st.columns(2)
        texto.markdown(texto_bothrops_alternatus)
        imagem.image('https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/Balternathus_4.jpg?raw=true', width=500) 

    
    texto_bothrops_pubescens = """
    **_Bothrops pubescens_**: Jararaca-pintada, jararaca-do-rabo-branco, jararaca-pintada-uruguaia, jararaca-pampeana. Castanha com desenhos em forma de trapézios. Ventre manchado. Mede, em média, 60 cm. Atividade crepuscular e noturna. Espécie comum em campos abertos, como o bioma pampa podendo adentrar nas plantações. É de menor porte e bastante reativa. Veneno de ação proteolítica, coagulante e hemorrágica.
    """
    bothrops_pubescens_container = st.container(border=True)
    with bothrops_pubescens_container:
        texto, imagem = st.columns(2)
        texto.markdown(texto_bothrops_pubescens)
        imagem.image('https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/B-pubescens_5.jpg?raw=true', width=500)     

    texto_crotalus_durissus = """
    **_Crotalus durissus_**: Cascavel. Marrom amarelada com desenhos de losangos mais claros no dorso e nas laterais. Mede até 1,5 m. Período de atividades durante a tarde e a noite, principalmente no crepúsculo. Vive em locais altos, montanhosos, pedregosos, de campo entremeado com mato e invernos frios. Possuem o crepitáculo (chocalho) de anéis córneos na ponta da cauda que, ao se movimentar durante momentos estressantes, emite o som do choque dos anéis. Dificilmente ataca, e anuncia a sua presença através do som do chocalho. Praticam a caça por espreita - permanecem imóveis no solo esperando a passagem da presa (roedor). Veneno de ação neurotóxica, miotóxica e coagulante.
    """
    crotalus_durissus_container = st.container(border=True)
    with crotalus_durissus_container:
        texto, imagem = st.columns(2)
        texto.markdown(texto_crotalus_durissus)
        imagem.image('https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/Crotalus_durissus_6.jpg?raw=true', width=500)   
    

    texto_micrurus_altirostris = """
    **_Micrurus altirostris_**: Coral-verdadeira. A espécie tem como característica a presença de anéis pretos e brancos sobre fundo vermelho. Os anéis circundam todo o corpo. Mede até 80 cm. A atividade ocorre principalmente durante o dia, reduzindo até o período da noite. As corais-verdadeiras têm hábitos fossoriais, vivendo em tocas ou buracos embaixo da terra nas matas ou bordas de matas. Não possuem presas especializadas como as Viperidaes, mas pequenos dentes. Precisam morder e segurar a presa para inocular o veneno. Alimentam-se de outras serpentes. Veneno de ação neurotóxica.
    """
    micrurus_altirostris_container = st.container(border=True)
    with micrurus_altirostris_container:
        texto, imagem = st.columns(2)
        texto.markdown(texto_micrurus_altirostris)
        imagem.image('https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/M-altirostris_7.jpg?raw=true', width=500) 
        
    st.divider()
    texto_sobre_aranhas = """
    ### ACIDENTES POR ARANHAS
    
    Os envenenamentos por aranhas predominam no Rio Grande do Sul com relação aos demais acidentes por animais peçonhentos. Existem duas espécies de aranha de importância médica no estado, cujos envenenamentos podem ser tratados com soro antiveneno: _Loxosceles intermedia_, a aranha-marrom, e _Phoneutria nigriventris_, a aranha-armadeira. 
    """
    st.markdown(texto_sobre_aranhas)

    texto_loxosceles = """
    **_Loxosceles intermedia_**: a aranha-marrom é característica de centros urbanos e pode permanecer dentro das residências, escondidas atrás de mobiliário e, por vezes, no meio das roupas pessoais, roupa de cama e toalhas. Os acidentes ocorrem quando o paciente esmaga a Loxosceles acidentalmente contra o próprio corpo ao se vestir, calçar sapatos ou limpar a casa. Não é uma aranha agressiva e é bastante pequena. O acidente pode levar ao surgimento de áreas de isquemia e necrose na pele, sendo necessário o debridamento tecidual. Pode haver a perda de grandes áreas musculares.
    """
    loxosceles_container = st.container(border=True)
    with loxosceles_container:
        texto, imagem = st.columns(2)
        texto.markdown(texto_loxosceles)
        imagem.image('https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/thumbnail_Loxosceles%20-%20aranha-marrom_8.jpg?raw=true', width=500) 
    
    texto_phoneutria = """
    **_Phoneutria nigriventris_**: a armadeira é um aracnídeo de maior tamanho e apresenta comportamento reativo – ao se sentir ameaçada, pode saltar sobre a pessoa ou animal, causando o acidente. A armadeira é mais comum em áreas rurais e pode entrar em galpões, porões, e até nas residências durante o período reprodutivo, entre os meses de março e maio, quando os machos se tornam errantes em busca de fêmeas. O acidente causa dor intensa.
    """
    phoneutria_container = st.container(border=True)
    with phoneutria_container:
        texto, imagem = st.columns(2)
        texto.markdown(texto_phoneutria)
        imagem.image('https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/Phoneutria%20-%20armadeira_9.jpeg?raw=true', width=300) 

    texto_sobre_escorpiao = """
    ### ACIDENTES POR ESCORPIÃO
    
    No Rio Grande do Sul há diversas espécies de escorpiões, sendo que a maioria é de baixa toxicidade. Já o _Tityus serrulatus_, conhecido popularmente como escorpião-amarelo, é o responsável pelos acidentes de alta toxicidade e que, em alguns casos, necessidade de tratamento com soro antiescorpiônico ou antiaracnídico.
    """
    st.divider()
    st.markdown(texto_sobre_escorpiao)
    

    texto_tityus = """
    **_Tityus serrulatus_**: o escorpião-amarelo é exótico no estado, sendo natural de Minas Gerais, e é provável que ele tenha se distribuído por todo o Brasil a partir do transporte humano rodoviário, em meio a produtos como verduras e legumes. Ao chegar em locais novos, se houver alimento (principalmente baratas), água e abrigo o T. serrulatus logo se adapta e se multiplica, tornando-se endêmico. Os principais grupos de risco para acidentes causados por escorpião-amarelo são as crianças e os idosos. Chega, no máximo, a 7 cm de tamanho. Possui o corpo amarelo com detalhes mais escuros no dorso, ponta das pinças e ponta da causa. Ainda, é possível identificá-lo pelas serrilhas presentes na cauda. O veneno do escorpião-amarelo pode causar alterações na frequência cardíaca, respiratória e na pressão arterial.
    """
    tityus_container = st.container(border=True)
    with tityus_container:
        texto, imagem = st.columns(2)
        texto.markdown(texto_tityus)
        imagem.image('https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/Tiyus_serrulatus_10.jpg?raw=true', width=500)     

    texto_lagarta = """
    ### ACIDENTES POR LAGARTA
    
    Existem diversas lagartas urticantes no Rio Grande do Sul, mas a _Lonomia obliqua_, conhecida como taturana, é a única que pode causar acidentes graves com a necessidade do uso de soro antilonômico. 
    """
    st.divider()
    st.markdown(texto_lagarta)
    
    texto_lonomia = """
    **_Lonomia obliqua_**: conhecida como taturana, o seu ciclo de vida é de, em média, 150 dias. A fase de lagarta, que representa perigo devido à presença das cerdas urticantes, tem duração de 60 dias. Durante esta fase da vida, as lagartas permanecem agregadas em troncos de árvores durante o dia e, à noite, sobem para as copas para se alimentar de folhas. Por esta característica de permanecerem agregadas, quando um acidente ocorre, o paciente entra em contato com vários animais ao mesmo tempo. O maior perigo deste acidente é a sua toxina, que pode levar à insuficiência renal aguda.
    """
    lonomia_container = st.container(border=True)
    with lonomia_container:
        texto, imagem = st.columns(2)
        texto.markdown(texto_lonomia)
        imagem.image('https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/Taturana-11.jpg?raw=true', width=500)       
    


    
    
with tab3:
    st.header("Metodologia")
    texto_metodologia_1 = """    
        
    A metodologia utilizada na realização e coleta de informações para originar o “Buscador de Soros Antivenenos” foi desenvolvida no Software QGIS, a partir de um processo chamado de Network Analysis, com objetivo de adquirir as distâncias dos municípios do Rio Grande do Sul, ao ponto focal de soro antiveneno mais próximo. Para a idealização do projeto foram utilizados dados shapefile (linhas, pontos e polígonos), ferramentas e plugins do programa QGIS.
    
    Inicialmente foram introduzidos e espacializados os Pontos Focais (locais onde os soros antivenenos se encontram) no software, de forma que fosse possível a visualização dos mesmos no território do estado do Rio Grande do Sul. Estes Pontos Focais foram adquiridos por meio de uma tabela disponibilizada pelo Centro de Informação Toxicológica (CIT). Juntos dos Pontos Focais foram adicionados pontos das sedes municipais do Rio Grande do Sul (estes pontos foram identificados a partir do centro urbano dos municípios), um shapefile das rodovias do RS e um shapefile de polígonos do estado do RS (Figura 1). 
    
    ![Figura 1](https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/imagens_metodologia/figura1.png?raw=true "Figura 1")
    
    Pontos Focais de Soro Antiveneno, em vermelho. Sedes Municipais, em azul. Rodovias do RS, em marrom.
    
    Uma vez com todos os dados organizados, foi possível por meio de ferramentas e plugins do QGIS realizar o Network Analysis, onde foi feito um geoprocessamento dos dados para obter as distâncias das sedes municipais até os Pontos Focais de Soro Antiveneno. O geoprocessamento teve como base o plugin QNEAT3 que criou as distâncias em linha reta dos Pontos Focais até as sedes municipais do estado. Como sabemos que o principal meio de transporte da população é o automóvel, foi realizado uma correção das distâncias para que elas fossem feitas utilizando a rede de rodovias do estado (Figura 2). 
    
    ![Figura 2](https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/imagens_metodologia/figura4%20certa.png?raw=true "Figura 2")
    
    Geoprocessamento de Network Analysis realizada para Pontos Focais com Soro Antiveneno SAB. 
    Em verde, a distância da sede municipal de cada município do RS até o Ponto Focal mais próximo, com base nas rodovias do estado.
    
    Como nem todos Pontos Focais têm em seu estoque todos 6 Soros Antivenenos disponibilizados, o geoprocessamento foi realizado seis vezes, uma vez para cada Soro Antiveneno. Uma vez para Pontos Focais com SAB, uma vez para Pontos Focais com SAC, e assim por diante. (Figura 3)
    """
    
    
    
    
    texto_metodologia_2 =  """
    1- Soro antiveneno SAC | 2- Soro antiveneno SAE | 3- Soro antiveneno Saar |
    4- Soro antiveneno SAEsc | 5- Soro antiveneno SAB | 6- Soro antiveneno SALon
    
    Como produto final da metodologia aplicada foram obtidas tabelas dos municípios do Rio Grande do Sul e qual Ponto Focal se localiza mais próximo do mesmo, com distância em km. Foi obtida uma tabela para cada Soro Antiveneno (SAB, SAC, SAE, SAEsc, SALon e Saar). (Figura 4)
    
    ![Figura 4](https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/imagens_metodologia/figura4.png?raw=true "Figura 4")
    
    Exemplo de tabela gerada após o geoprocessamento dos dados.
    Tabela para Soro Antiveneno SAB.
    
    #### Fluxo Metodológico
    
    ![Fluxo Metodológico](https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/imagens_metodologia/fluxo%20metodologico.png?raw=true "Fluxo Metodológico")
    
    """

    st.markdown(texto_metodologia_1)
    st.image('https://github.com/andrejarenkow/Soro-Antiveneno/blob/main/imagens_metodologia/figura3.png?raw=true', width=1200 )
    st.markdown(texto_metodologia_2)

with tab_emergencia:
    dados_todos = pd.DataFrame()
    abas = ['SAB', 'SAAR', 'SAC', 'SAEL', 'SAEsc', 'SALON', 'SABC']
    
    for i in abas:
    
      dados = pd.read_excel('https://docs.google.com/spreadsheets/d/e/2PACX-1vSRHKbwxnZ_2aTw2nub-8Gp3cSZj5leSyyRMGRWquVhbffvxFLDdP6QW8MA-HKoXQ/pub?output=xlsx', skiprows=3, sheet_name=i) 
    
      dados = dados.drop(['Lote',	'Data de vencimento'], axis=1)
    
      dados['Regional'] = dados['Regional'].ffill()
      #dados = dados.dropna(subset=['N° de Ampolas'])
      dados['Soro'] = i
      dados_todos = pd.concat([dados_todos, dados])
      dados_todos = dados_todos.reset_index(drop=True)
    
    
    # Atualizar o valor da coluna 'Município' para 'Porto Alegre' onde 'Regional' é 'CEADI'
    dados_todos.loc[dados_todos['Regional'] == 'CEADI', 'Município'] = 'Porto Alegre'
    dados_todos['Município'] = dados_todos['Município'].fillna(method='ffill')
    dados_todos['Unidade de Saúde'] = dados_todos['Unidade de Saúde'].fillna(method='ffill')
    dados_todos = dados_todos[dados_todos['Município']!='TOTAL']
    dados_todos = dados_todos[dados_todos['Regional']!='TOTAL DISTRIBUÍDO']
    dados_todos = dados_todos[~dados_todos['Unidade de Saúde'].astype(str).str.isdigit()]
    dados_todos = dados_todos[['Regional', 'Município', 'Unidade de Saúde', 'N° de Ampolas', 'Soro']]
    dados_todos['N° de Ampolas'] = dados_todos['N° de Ampolas'].fillna(0)
    
    dados_todos = dados_todos.reset_index(drop=True)
    dados_todos['Município'] = dados_todos['Município'].replace({
        'São Luiza Gonzaga':'São Luiz Gonzaga',
        'Canguçú':'Canguçu'
    }).str.strip()
    
    # Estoque por município

    soro = st.selectbox('Selecione o soro', options=abas, index=0)
    
    dados_soro = dados_todos[dados_todos['Soro']==soro]
    
    dados_soro = dados_soro.groupby('Município')['N° de Ampolas'].sum().reset_index()
    dados_lat_lon = pd.read_csv('https://raw.githubusercontent.com/andrejarenkow/csv/master/Munic%C3%ADpios%20RS%20IBGE6%20Popula%C3%A7%C3%A3o%20CRS%20Regional%20-%20P%C3%A1gina1.csv')
    dados_soro = dados_soro.merge(dados_lat_lon, on='Município', how='left')
    dados_todos_soro = dados_todos[dados_todos['Soro']==soro]
    fig_estoque = px.scatter_mapbox(dados_soro, lat="lat", lon="lon", hover_name="Município", hover_data=["N° de Ampolas"],
                            zoom=5.5, height=600, size="N° de Ampolas", color_discrete_sequence=["#ED5A53"],
                                   )
    fig_estoque.update_layout(mapbox_style="open-street-map")
    fig_estoque.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.subheader(f'Locais com estoque de {soro} no RS')
    coluna_tabela_soro, coluna_mapa_soro = st.columns(2)
    coluna_mapa_soro.plotly_chart(fig_estoque)
    coluna_tabela_soro.dataframe(dados_todos_soro.sort_values('Município'), hide_index=True, height=600)



creditos = st.container(border=True)
with creditos:
    st.write('Aplicação desenvolvida pela equipe da Divisão de Vigilância Ambiental em Saúde do Centro Estadual de Vigilância em Saúde da Secretaria Estadual de Saúde do Rio Grande do Sul')
    st.write('Integrantes: Bárbara Mendes Pietoso, Carlo Johannes Lipp Nissinen, Carolina Schell Franceschina e André Jarenkow')
           
