#==================================
#imports
#==================================

from haversine import haversine as haversine
import pandas as pd
import re as re
import folium as folium
import streamlit as st
import datetime as dt
import plotly.express as px
from streamlit_folium import folium_static


st.set_page_config(page_title='Visão Empresa', page_icon='📈', layout='wide')

#==================================
#funções
#==================================

def data_clean(df1):
    '''
        Função Limpeza de dados


        1- Remove Espaços das strings

        2- Exclui as linhas vaizas

        3- Conversão de colunas (texto para numero, numero para data)

        4- Remoção do texto da colunas Time_taken(min) e conversão de tipo de variavel


        Input Data Frame
        Output Data Frame limpo
    
    
    '''
    # 1 Remover os espaços das strings
    df1.loc[:,'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:,'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:,'City'] = df1.loc[:, 'City'].str.strip()

    # 2 Excluir as linhas com a idade dos entregadores vazia
    linhas_vazias = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]
    linhas_vazias = df1['Delivery_person_Age'] != 'NaN '
    df1= df1.loc[linhas_vazias, :]
    linhas_vazias = df1['City'] != 'NaN'
    df1= df1.loc[linhas_vazias, :]
    linhas_vazias = df1['Road_traffic_density'] != 'NaN'
    df1= df1.loc[linhas_vazias, :]

    # 3 Conversao de texto/categoria/string para numeros inteiros
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

    # 3 Conversao de texto/categoria/strings para numeros decimais
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

    # 3 Conversao de texto para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )
    linhas_vazias = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    # 4 Comando para remover o texto de números
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split ( '(min)')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    return df1

def order_day_graph(df1):
    ''' 
        1- Agrupa as colunas pelo dia

        2- Conta o número de pedidos

        3- Faz o grafico de barras

        Input = df1
        Output = grafico 
    '''




    colums_01 = ['ID','Order_Date']
    df_qtd_pedidos_dia = df1.loc[:, colums_01].groupby(['Order_Date']).count().reset_index()
    fig= px.bar(df_qtd_pedidos_dia, x='Order_Date', y= 'ID')
    return fig

def orders_traffic_graph(df1):

    '''
        1- agrupa as pelo trafego

        2- conta o número de pedidos 

        3- retorna um grafico pizza
    
    '''

    cols = ['ID','Road_traffic_density']
    df_pedidos_trafego = df1.loc[:,cols].groupby(['Road_traffic_density']).count().reset_index()
    df_pedidos_trafego['entregas_perc'] = df_pedidos_trafego['ID']/df_pedidos_trafego['ID'].sum()
    fig = px.pie(df_pedidos_trafego, values='entregas_perc', names='Road_traffic_density')
    return fig

def order_city_traffic_graph(df1):
    colums_04 = ['ID','Road_traffic_density','City']
    pedidos_cidade_trafego = df1.loc[:, colums_04].groupby(['City', 'Road_traffic_density']).count().reset_index()
    pedidos_cidade_trafego = pedidos_cidade_trafego.loc[(pedidos_cidade_trafego['City']!= 'NaN') &(pedidos_cidade_trafego['Road_traffic_density']!= 'NaN'), :]
    fig = px.scatter(pedidos_cidade_trafego, x='City', y='Road_traffic_density', size='ID')
    return fig

def orders_week(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    colums_02 = ['ID','week_of_year']
    df_qtd_pedidos_semana = df1.loc[:, colums_02].groupby(['week_of_year']).count().reset_index()
    fig = px.line(df_qtd_pedidos_semana, x='week_of_year', y='ID')
    return fig

def deliveries_week(df1):
    df_aux01 = df1.loc[:,['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()
    df_aux02 = df1.loc[:,['Delivery_person_ID', 'week_of_year']].groupby(['week_of_year']).nunique().reset_index()

    df_aux = pd.merge(df_aux01, df_aux02, how='inner')
    df_aux['qtd_pedidos_entregador'] = df_aux['ID']/df_aux['Delivery_person_ID']

    fig = px.line(df_aux,x='week_of_year', y='qtd_pedidos_entregador')
    return fig

def country_map(df1):
    columns = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df_aux = df1.loc[:, columns].groupby(['City', 'Road_traffic_density']).median().reset_index()
    df_aux =df_aux.loc[df_aux['City'] != 'NaN']
    df_aux =df_aux.loc[df_aux['Road_traffic_density'] != 'NaN']
    df_aux = df_aux
    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
        location_info['Delivery_location_longitude']],
        popup = location_info[['City','Road_traffic_density']]).add_to(map)
    folium_static(map, width=1024, height=600)
    return None

#==========================
#importando e limpando a base de dados
#==========================
path = './dataset/train.csv'
df = pd.read_csv(path)
df1 = df.copy()
df1 = data_clean(df1)

#========================================
#Side Bar
#========================================


with st.sidebar:


    # Logo
    st.markdown('# Cury Company')
    st.markdown('## Fastest delivery in Town')
    st.markdown("""---""")




    #========================================
    #Slide bar
    #========================================
    # Filtro de data
    st.markdown('## Select a limit date')
    # Usando datetime para criar as datas
    date_slider = st.slider( '',
        value=dt.datetime(2022, 4, 13),  # Data ajustada
        min_value=dt.datetime(2022, 2, 11), 
        max_value=dt.datetime(2022, 4, 6), 
        format='DD-MM-YYYY'
    )

    #========================================
    #Multi select 
    #========================================
    st.markdown("""---""")
    st.markdown('## Chose the traffic density')
    traffic_options = st.multiselect('', ['High', 'Jam', 'Low', 'Medium'], default=['High', 'Jam', 'Low', 'Medium'])

    #========================================
    #Aplicando o filtro
    #========================================

    #Filtro de data
    linhas_selecionadas = df1['Order_Date'] < date_slider
    df1 = df1.loc[linhas_selecionadas, :]

    #Filtro de trafego 
    
    linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
    df1 = df1.loc[linhas_selecionadas, :]



#========================================
#Conteudo principal
#========================================

st.markdown('# Marketpalce-Customers Vision')


#========================================
#tabs de conteudo
#========================================
tab1, tab2, tab3 = st.tabs(['Management Vision', 'Tatical Vision', 'Geographic Vision'])


#========================================
#Visão Gerencial
#========================================

with tab1:


    with st.container():
        #gráfico pedidos por dia
       st.markdown('### Quantity Of Orders per Day')
       fig = order_day_graph(df1)
       st.plotly_chart(fig, use_container_width=True)


    st.markdown('''---''')


    with st.container():
        col1, col2= st.columns(2)
        with col1:
            # grafico distribuição dos pedidos por tipo de tráfego.
            st.markdown('### Quantity of Orders Per Traffic')
            fig = orders_traffic_graph(df1)
            st.plotly_chart(fig, use_container_width=True)


        with col2:
            #gráfico Comparação do volume de pedidos por cidade e tipo de tráfego.
            st.markdown('### Comparison Of Order Volume By City And Traffic')
            fig = order_city_traffic_graph(df1)
            st.plotly_chart(fig, use_container_width=True)

#========================================
#Visão Tatica
#========================================

with tab2:

    with st.container():

        #Quantidade de pedidos por semana
        st.markdown('### Orders per week')
        fig = orders_week(df1)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('''---''')

    with st.container():

        #Quantidade média de entregas por entregador
        st.markdown('### Mean Of Deliveries By Delivery Man')
        fig = deliveries_week(df1)
        st.plotly_chart(fig, use_container_width=True)


#========================================
#Geografica
#========================================

with tab3:

    ## A localização central de cada cidade por tipo de tráfego
    st.markdown('### Map')
    country_map(df1)

