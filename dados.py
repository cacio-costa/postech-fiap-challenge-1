from functools import reduce

import unicodedata
import pandas as pd
import numpy as np

def get_dataframe_vinho_original():
    df_exp_vinho = pd.read_csv('dados/ExpVinhoOriginal.csv', sep=';')

    anos_para_apagar = []
    for y in range(1970,2009):
        anos_para_apagar.append(str(y))
        anos_para_apagar.append(str(y)+'.1')

    df_exp_vinho = df_exp_vinho.drop(anos_para_apagar, axis=1)

    return df_exp_vinho


def get_dataframe_espumantes_original():
    df = pd.read_csv('dados/ExpEspumantesOriginal.csv', sep=';')
    df = df.drop(columns=df.columns[2:((2009-1970)*2+2)])

    return df


def get_colunas_para_analise():
    
    def agrega_valores(lista, valor):
        return [*lista, str(valor), f'{valor}.1']
    
    return reduce(agrega_valores, range(2009, 2024),[])


def melt_dataframe_vinho(dataframe):
    df_melt = pd.melt(dataframe, id_vars=['País'], value_vars=get_colunas_para_analise(), var_name='ano_medida', value_name='valor')

    df_melt['ano'] = df_melt['ano_medida'].apply(lambda x: x.split('.')[0])
    df_melt['medida'] = df_melt['ano_medida'].apply(lambda x: 'valor_usd' if '.1' in x else 'peso_l')
    df_melt = df_melt.drop('ano_medida', axis=1)

    return df_melt


def melt_dataframe_espumante(dataframe):
    df_melt = dataframe.melt(id_vars=['País'], value_vars=dataframe.columns[2:], var_name='ano_medida', value_name='valor')

    df_melt['ano'] = df_melt['ano_medida'].apply(lambda x: x.split('.')[0])
    df_melt['medida'] = df_melt['ano_medida'].apply(lambda x: 'valor_usd' if '.1' in x else 'peso_l')
    df_melt = df_melt.drop('ano_medida', axis=1)

    return df_melt


def get_dataframe_unificado_de_vinhos_e_espumantes():
    df_exp_vinho = get_dataframe_vinho_original()
    df_exp_vinho_melt = melt_dataframe_vinho(df_exp_vinho)

    df_exp_espumante = get_dataframe_espumantes_original()
    df_exp_espumante_melt = melt_dataframe_espumante(df_exp_espumante)

    df_exp_vinho_pivot = df_exp_vinho_melt.pivot_table(index=['País', 'ano'], columns='medida', values='valor').reset_index()
    df_exp_vinho_pivot['ano'] = df_exp_vinho_pivot['ano'].astype(int)

    df_exp_espumante_pivot =  df_exp_espumante_melt.pivot(index=['País', 'ano'], columns='medida', values='valor').reset_index()
    df_exp_espumante_pivot['ano'] = df_exp_espumante_pivot['ano'].astype(int)
    df_exp_espumante_pivot.columns.name=''

    df_exp_vinho_pivot['País'] = df_exp_vinho_pivot['País'].apply(lambda x: unicodedata.normalize('NFKD', x).encode('ascii', errors='ignore').decode('utf-8'))
    df_exp_espumante_pivot['País'] = df_exp_espumante_pivot['País'].apply(lambda x: unicodedata.normalize('NFKD', x).encode('ascii', errors='ignore').decode('utf-8'))

    index_alemanha = df_exp_vinho_pivot[df_exp_vinho_pivot['País'] == 'Alemanha, Republica Democratica'].index
    df_exp_vinho_pivot.loc[index_alemanha, 'País'] = 'Alemanha'

    index_coreia = df_exp_vinho_pivot[df_exp_vinho_pivot['País'] == 'Coreia, Republica Sul'].index
    df_exp_vinho_pivot.loc[index_coreia, 'País'] = 'Coreia do Sul, Republica da'

    index_guine = df_exp_vinho_pivot[df_exp_vinho_pivot['País'] == 'Guine Bissau'].index
    df_exp_vinho_pivot.loc[index_guine, 'País'] = 'Guine-Bissau'

    index_holanda = df_exp_vinho_pivot[df_exp_vinho_pivot['País'] == 'Paises Baixos'].index
    df_exp_vinho_pivot.loc[index_holanda, 'País'] = 'Paises Baixos (Holanda)'

    index_finlandia = df_exp_espumante_pivot[df_exp_espumante_pivot['País'] == 'Filanldia'].index
    df_exp_espumante_pivot.loc[index_finlandia, 'País'] = 'Finlandia'

    index_tcheca = df_exp_espumante_pivot[df_exp_espumante_pivot['País'] == 'Republica Tcheca'].index
    df_exp_espumante_pivot.loc[index_tcheca, 'País'] = 'Tcheca, Republica'

    index_trinidade = df_exp_espumante_pivot[df_exp_espumante_pivot['País'] == 'Trinidade e Tobago'].index
    df_exp_espumante_pivot.loc[index_trinidade, 'País'] = 'Trinidade Tobago'

    df_exp_vinho_pivot = df_exp_vinho_pivot.rename(columns={'peso_l': 'peso_l_vinho', 'valor_usd': 'valor_usd_vinho'})
    df_exp_espumante_pivot = df_exp_espumante_pivot.rename(columns={'peso_l': 'peso_l_espumante', 'valor_usd': 'valor_usd_espumante'})

    df_unificado = pd.merge(df_exp_vinho_pivot, df_exp_espumante_pivot, on=['País', 'ano'], how='outer')
    
    df_unificado = df_unificado.fillna(0)

    df_unificado['peso_l'] = df_unificado['peso_l_vinho'] + df_unificado['peso_l_espumante']
    df_unificado['valor_usd'] = df_unificado['valor_usd_vinho'] + df_unificado['valor_usd_espumante']
    df_unificado['peso_Ml'] = df_unificado['peso_l'] / 1_000_000
    df_unificado['valor_usd_M'] = df_unificado['valor_usd'] / 1_000_000
    df_unificado['usd_por_l'] = df_unificado['valor_usd'] / df_unificado['peso_l']

    df_unificado = df_unificado.fillna(0)
    df_unificado.loc[386, 'usd_por_l'] = 0

    return df_unificado
