#==================================
#Limpeza de dados e imports
#==================================


#importando bibliotecas
from haversine import haversine as haversine
import pandas as pd
import re as re
import folium as folium
import streamlit as st
import datetime as dt
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


st.set_page_config(page_title='Visão Restaurantes', page_icon='👨‍🍳', layout='wide')



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

def delivery_time(df1, festival, std_mean ):

    ''' 
    1- cria um dataframe agrupa a coluna de tempo de entrega pela coluna festival

    2- calcula desvio padrão ou média da coluna de tempo dependendo do input

    3- retorna a média ou desvio padrao durante ou nao o festival
    



    input = df1, festival, std_mean

    df1 =dataframe
    festival = Yes ou No
    std_mean = std ou mean

    ouput = desvio padrao ou média do tempo de entrega durante o festival
    '''

    if std_mean == 'mean':
        cols = ['Festival', 'Time_taken(min)']
        df3 = df1.loc[:, cols].groupby(['Festival']).mean().reset_index()
        filtro =df3['Festival']== festival
        
        festival_deliveries_time = np.round(df3.loc[filtro, 'Time_taken(min)'], 2)
    elif std_mean == 'std':
        cols = ['Festival', 'Time_taken(min)']
        df3 = df1.loc[:, cols].groupby(['Festival']).std().reset_index()
        filtro = df3['Festival']== festival
        
        festival_deliveries_time = np.round(df3.loc[filtro, 'Time_taken(min)'], 2)

    return festival_deliveries_time            

def delivery_distance(df1, graph):

    '''
        1- calcula a distancia de entrega usando a posição dos restaurantes em relação ao local de entrega e retorna a distancia em uma nova coluna

        2- graph= 'no' retorna o valor da distancia média de entrega

        2- graph = 'yes'
    
        input df1, graph

        df1= dataframe

        graph= 'Yes' ele faz o grafico 'No' ele retona o valor da distancia média
    '''

    cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df1['delivery_distance'] = df1.loc[:, cols].apply(lambda x: 
                                haversine( 
                                (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                (x['Delivery_location_latitude'], x['Delivery_location_longitude']))
                                ,axis=1)

    if graph == 'no':
        distance = np.round(df1['delivery_distance'].mean(), 2)

    elif graph == 'yes':
        avg_distance = df1.loc[:, ['City', 'delivery_distance']].groupby(['City']).mean().reset_index()
        distance = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['delivery_distance'], pull=[0,0.1,0])]) 
    return distance

def  avg_std_time_graph(df1):
    cols = ['Time_taken(min)','City']
    avg_std_time_per_city = df1.loc[:, cols].groupby(['City']).agg({'Time_taken(min)': ['mean','std']})
    avg_std_time_per_city.columns= ['avg_time', 'std_time']
    avg_std_time_per_city = avg_std_time_per_city.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', x=avg_std_time_per_city['City'], y=avg_std_time_per_city['avg_time'], error_y=dict(type='data', array=avg_std_time_per_city['std_time'])))
    fig.update_layout(barmode='group')
    return fig

def time_per_city_graph(df):
    cols = ['Time_taken(min)','City', 'Road_traffic_density']
    avg_std_time_per_city_traffic = df1.loc[:, cols].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)': ['mean','std']})

    avg_std_time_per_city_traffic.columns= ['avg_time', 'std_time']
    avg_std_time_per_city_traffic = avg_std_time_per_city_traffic.reset_index()

    fig = px.sunburst(avg_std_time_per_city_traffic, path=['City', 'Road_traffic_density'], values='avg_time',
                        color='std_time', color_continuous_scale='RdBu',
                        color_continuous_midpoint= np.mean(avg_std_time_per_city_traffic['std_time']))
    return fig            


def std_avg_time(df1):
    cols = ['Time_taken(min)','City', 'Type_of_order']

    avg_std_time_per_city_order_type = df1.loc[:, cols].groupby(['City','Type_of_order']).agg({'Time_taken(min)': ['mean','std']})
    avg_std_time_per_city_order_type.columns= ['avg_time', 'std_time']
    avg_std_time_per_city_order_type = avg_std_time_per_city_order_type.reset_index()
    return avg_std_time_per_city_order_type
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

st.markdown('# Marketpalce-Restaurants Vision')






#========================================
#tabs de conteudo
#========================================
tab1, tab2, tab3 = st.tabs(['Management Vision', '__', '__'])

with tab1   :
    with st.container():
        col1, col2, col3 = st.columns(3)


        #Entregadores unicos
        with col1:
            
            delivery_person_qty = len(df1.loc[:, 'Delivery_person_ID'].unique())
            print(delivery_person_qty)
            st.metric('Unique Delivery People', delivery_person_qty)

            

        #Tempo de entrega médio sem festival
        with col2:
            festival_deliveries_time = delivery_time(df1, 'No', 'mean')
            st.metric('Avarage Delivery Time', festival_deliveries_time)



        #desvio padrao do tempo de entrega com festival
        with col3:
            festival_deliveries_time = delivery_time(df1, 'No', 'std')
            st.metric('STD delivery time', festival_deliveries_time)


    with st.container():
        col1, col2, col3 = st.columns(3)

        #dinstancia média  de entregas
        with col1:
            avg_distance = delivery_distance(df1, 'no')
            st.metric('Avarage Delivery Distance', avg_distance)

        #Tempo médio de entrega durante os festivais
        with col2:
            festival_deliveries_time = delivery_time(df1, 'Yes', 'mean')
            st.metric('Avarage delivery time in festival', festival_deliveries_time)            

        with col3:
            festival_deliveries_time = delivery_time(df1, 'Yes', 'std')
            st.metric('STD delivery time in Festival', festival_deliveries_time)
    st.markdown('''---''')



    
    with st.container():
        col1, col2 = st.columns(2, gap='medium')

        with col1:
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig, use_container_width=True   )


        with col2:
            avg_std_time_per_city_order_type = std_avg_time(df1)
            st.dataframe(avg_std_time_per_city_order_type)
    st.markdown("""---""")
    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            fig = delivery_distance(df1, 'yes')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = time_per_city_graph(df1)
            st.plotly_chart(fig, use_container_width=True)

        



