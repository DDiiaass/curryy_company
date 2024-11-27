#==================================
#Imports
#==================================


#importando bibliotecas
from haversine import haversine as haversine
import pandas as pd
import folium as folium
import streamlit as st
import datetime as dt




st.set_page_config(page_title='Visão Entregadores', page_icon='🏍️', layout='wide')




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

def avarage_rating(df1):
    '''
        1- agrupa as notas por entregador

        2- calcula a média das avaliações

        3- retonar um df com a média de avaliação de cada entregador

        input = df1

        output = avg_delivery_ratings_df
    
    '''
    columns = ['Delivery_person_Ratings','Delivery_person_ID']
    avg_delivery_ratings_df = df1.loc[:, columns].groupby('Delivery_person_ID').mean()
    return avg_delivery_ratings_df

def std_avg_rating(df1, col):

    '''
        1- agrupa as notas pela colunas enviada

        2- cria duas novas colunas no datafram uma com o desvio padrão das notas pela colunas de agrupamento e a outra a média das notas pela coluna

        3- renomeia as colunas

        4- retorna o dataframe com as novas coluans

        inpput: df1, col

        df(o data frame), col(a colunas de agrupamento)

        output: avg_std_df
      
    '''  

    #avaliação média e desvio padrão 
    avg_std_df = (df1.loc[:, ['Delivery_person_Ratings', col]].groupby([col])
                                    .agg({'Delivery_person_Ratings': ['mean', 'std']}))

    #nome colunas
    avg_std_df.columns = ['Delivery_mean', 'Delivery_std']
    avg_std_df = avg_std_df.reset_index()
    return avg_std_df

def top_deliveries(df1, max_min, x):

    '''
        1- cria um dataframe agrupando as colunas por cidaded e id do entregador

        2- ordena o tmepo de entrega por menores tempos ou maiores tempos dependendo do input do usuario

        3- retorna uma colunas com os x entregadores mais rapidos

        input df1, max_min, x

        df1 = dataframe  
        max_min= max = maiores tempos min = menores tempos 
        x=número de entregadores desejados



        output df3

        df3 = dataframe com os x entregadores mais rapidos por cidade
    '''








    if max_min == min:
        cols = ['Delivery_person_ID', 'City', 'Time_taken(min)']
        df2 = df1.loc[:, cols].groupby(['City', 'Delivery_person_ID']).min().sort_values(['City', 'Time_taken(min)'], ascending=True).reset_index()

        df_aux01 = df2.loc[df2['City'] == 'Urban'].head(x)
        df_aux02 = df2.loc[df2['City'] == 'Metropolitian'].head(x)
        df_aux03 = df2.loc[df2['City'] == 'Semi-Urban'].head(x)

        df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index()

    
    elif max_min == max:
        cols = ['Delivery_person_ID', 'City', 'Time_taken(min)']
        df2 = df1.loc[:, cols].groupby(['City', 'Delivery_person_ID']).max().sort_values(['City', 'Time_taken(min)'], ascending=False).reset_index()

        df_aux01 = df2.loc[df2['City'] == 'Urban'].head(10)
        df_aux02 = df2.loc[df2['City'] == 'Metropolitian'].head(10)
        df_aux03 = df2.loc[df2['City'] == 'Semi-Urban'].head(10)

        df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index()  

       
    return df3


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
tab1, tab2, tab3 = st.tabs(['Management Vision', '--', '--'])

with tab1:
#========================================
#menor idade, maior idade, melhor e pior condição de veiculo
#========================================
    with st.container():
        col1, col2, col3, col4 = st.columns(4, gap="large")


        #maior idade
        with col1:
            max_age = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Highest Age', max_age)


        #menor idade
        with col2:
            min_age = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Lowest Age', min_age)


        #melhor condição
        with col3: 
            melhor_condicao_veiculo = df.loc[:, 'Vehicle_condition'].max()
            col3.metric('Best vehicle condition', melhor_condicao_veiculo)
        

        #pior condição
        with col4:
            pior_condicao_veiculo = df.loc[:, 'Vehicle_condition'].min()
            col4.metric('Worst vehicle contition', pior_condicao_veiculo)

    st.markdown("""---""")


#========================================
#data frames, avaliações
#========================================
    with st.container():
        col1, col2 = st.columns(2)


        #avaliação média por entregador
        with col1:
            st.markdown('#### Mean rating per delivery person ')
            avg_delivery_ratings = avarage_rating(df1)
            st.dataframe(avg_delivery_ratings, use_container_width=True)


        with col2:
             #avaliação média e desvio padrao por tipo de trafego
            with st.container():
                st.markdown('######     Mean and Standard Deviation Rating Per Traffic')
                avg_std_ratings_per_traffic = std_avg_rating(df1, 'Road_traffic_density')
                st.dataframe(avg_std_ratings_per_traffic, use_container_width=True)


            
            #avaliação média e desvio padrao por condição climatica
            with st.container():
                 #avaliação média e desvio padrao por condição climatica
                st.markdown('###### Mean and Standard Deviation Rating Per Weather Condtions')
                avg_std_ratings_per_weather = std_avg_rating(df1, 'Weatherconditions')
                st.dataframe( avg_std_ratings_per_weather, use_container_width=True)
    st.markdown("""---""")
    
    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('#### The Fastest Delivery People per city')
            df3 = top_deliveries(df1, min, 11)
            st.dataframe(df3.loc[:, ['City', 'Delivery_person_ID']], use_container_width=True)


        with col2:
            st.markdown('#### The Lowest Delivery People per city')
            df3 = top_deliveries(df1, max, 11)
            st.dataframe(df3.loc[:, ['City', 'Delivery_person_ID', 'Time_taken(min)']])
