import streamlit as st
import datetime as dt
import pandas as pd


#==================
#funções
#==================
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

#==========================
#importando e limpando a base de dados
#==========================
df = pd.read_csv('./dataset/train.csv')
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

#====================
#Conteudo principal
#====================

st.write('# Curry Company Growth Dashboard')

st.markdown(
        """
        The Growth Dashboard was created to monitor the growth metrics of Delivery Drivers and Restaurants.
        ### How to use the Growth Dashboard?
        - Comapny Vision:
            - Management Vision: General behavior metrics   
            - Tatical Vision: Weekly growth indicators
            - Geographic Vision: Inights of geolocation
        - Delivery Person Vision
            - Monitoring weekly growth indicators
        - Restaraunts Vision:
            - Weekly indicators: of restaurants growth
        
        ### Ask for Help
        Pedro Dias
        (61) 9 8323-8070
        
        """
)