import streamlit as st
import altair as alt
import io
import unicodedata
from millify import millify

import pandas as pd

import matplotlib.pyplot as plt

st.write("# Challenge 1 - Análise da exportação de vinhos e espumantes pelo Brasil")
st.divider()

st.write('## Tratamento de transformação dos datasets de exportação de vinhos e espumantes')

st.write('#### Dataset bruto utilizado para análise')
st.write('Como podemos observar na amostra abaixo, o dataset não é intuitivo. As colunas dos anos sem sufixo indicam o peso exportado. E as colunas com sufixo ".1" indicam o valor vendido.')
st.write('Além disso, só temos dados consistentes a partir de 2009.')

df_exp_vinho = pd.read_csv('dados/ExpVinhoOriginal.csv', sep=';')
st.write(df_exp_vinho.head())

st.write('Portanto foi necessário excluir os anos de 1970 a 2008. E o dataset foi transformado para facilitar as análises e obtenção de insights. Para isso, foram criadas as colunas **peso_kg** e **valor_usd**')

anos_para_apagar = []
for y in range(1970,2009):
    anos_para_apagar.append(str(y))
    anos_para_apagar.append(str(y)+'.1')

df_exp_vinho = df_exp_vinho.drop(anos_para_apagar, axis=1)

anos = [str(y) for y in range(2009, 2024)]

var_names = []
for a in anos:
    var_names.append(str(a))
    var_names.append(str(a) + '.1')

df_exp_vinho_melt = pd.melt(df_exp_vinho, id_vars=['País'], value_vars= var_names,
                  var_name='ano_medida', value_name='valor')

df_exp_vinho_melt['ano'] = df_exp_vinho_melt['ano_medida'].apply(lambda x: x.split('.')[0])
df_exp_vinho_melt['medida'] = df_exp_vinho_melt['ano_medida'].apply(lambda x: 'valor_usd' if '.1' in x else 'peso_l')
df_exp_vinho_melt = df_exp_vinho_melt.drop('ano_medida', axis=1)

df_exp_vinho_pivot = df_exp_vinho_melt.pivot_table(index=['País', 'ano'], columns='medida', values='valor').reset_index()


st.write('#### Dataset de exportação de vinhos transformado')
st.write(df_exp_vinho_pivot)
df_exp_vinho_pivot['ano'] = df_exp_vinho_pivot['ano'].astype(int)

# buffer = io.StringIO()
# df.info(buf=buffer)
# st.text(buffer.getvalue())

st.write('#### Dataset de exportação de espumantes')
st.write('O dataset de exportação de espumantes original precisou dos mesmos tratamentos de dados do dataset de vinhos.')

df_exp_espumante = pd.read_csv('dados/ExpEspumantesOriginal.csv', sep=';')
df_exp_espumante = df_exp_espumante.drop(columns=df_exp_espumante.columns[2:((2009-1970)*2+2)])

df_exp_espumante_melt = df_exp_espumante.melt(id_vars=['País'], value_vars=df_exp_espumante.columns[2:], var_name='ano_medida', value_name='valor')
df_exp_espumante_melt['ano'] = df_exp_espumante_melt['ano_medida'].apply(lambda x: x.split('.')[0])
df_exp_espumante_melt['medida'] = df_exp_espumante_melt['ano_medida'].apply(lambda x: 'valor_usd' if '.1' in x else 'peso_l')
df_exp_espumante_melt = df_exp_espumante_melt.drop('ano_medida', axis=1)

df_exp_espumante_pivot =  df_exp_espumante_melt.pivot(index=['País', 'ano'], columns='medida', values='valor').reset_index()
st.write(df_exp_espumante_pivot)

df_exp_espumante_pivot.columns.name=''
df_exp_espumante_pivot['ano'] = df_exp_espumante_pivot['ano'].astype(int)


## Merge dos datasets
st.write('## União dos datasets de vinhos e espumantes')
st.write('''A última transformação antes das análises consistiu em mesclar os dois datasets. As colunas de peso e valor de cada categoria foram especificadas (*peso_l_vinho, valor_usd_vinho, peso_l_espumante, valor_usd_espumante*), e duas novas colunas com o total dessas informações foram criadas: **peso_l** e **valor_usd**.''')

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

df_exp = pd.merge(df_exp_vinho_pivot, df_exp_espumante_pivot, on=['País', 'ano'], how='outer')
df_exp = df_exp.fillna(0)

df_exp['peso_l'] = df_exp['peso_l_vinho'] + df_exp['peso_l_espumante']
df_exp['valor_usd'] = df_exp['valor_usd_vinho'] + df_exp['valor_usd_espumante']

st.write(df_exp)

st.divider()

### Análises exploratórias
st.write('## Análises exploratórias dos dados')
st.write('#### Informações presentes e ausentes')

qtd_registros = df_exp['País'].count()
qtd_registros_zerados = df_exp.query('valor_usd == 0 & peso_l == 0').shape[0]
percentual_registros_ausentes = (qtd_registros_zerados / qtd_registros) * 100

col_registros1, col_registros2, col_registros3 = st.columns(3)
col_registros1.metric('Total de registros', qtd_registros)
col_registros2.metric('Registros sem informação (zerados)', qtd_registros_zerados)
col_registros3.metric('Percentual ausente', f'{millify(percentual_registros_ausentes, precision=2)}%')


df_paises_sem_importacao = df_exp.groupby('País').mean(numeric_only=True).query('valor_usd == 0 & peso_l == 0').reset_index()
st.write(df_paises_sem_importacao)

qtd_paises = len(df_exp['País'].unique())
qtd_paises_sem_medidas = df_paises_sem_importacao.shape[0]
percentual_paises_ausentes = (qtd_paises_sem_medidas / qtd_paises) * 100

col_paises1, col_paises2, col_paises3 = st.columns(3)
col_paises1.metric('Quantidade de países', qtd_paises)
col_paises2.metric('Países sem importação', qtd_paises_sem_medidas)
col_paises3.metric('Percentual sem importação', f'{millify(percentual_paises_ausentes, precision=2)}%')

st.write('#### Países que importaram em algum momento')

nomes_paises_sem_importacao = df_paises_sem_importacao['País'].tolist()
df_paises_com_importacao = df_exp.query('País not in @nomes_paises_sem_importacao').reset_index()

st.metric('Anos sem importar', df_paises_com_importacao.query('valor_usd == 0 & peso_l == 0').shape[0])
st.caption('Mesmo entre os países que importaram do Brasil em algum momento, o número de anos sem importação é grande, representando **57,43%**.')

st.info('Muitos registros ausentes. Então, a partir daqui, esses registros foram desconsiderados.')

df_exp_presentes = df_exp.query('not (peso_l == 0 & valor_usd == 0)')
# st.write(df_exp.describe())



st.write('#### Indicadores sobre o valor vendido')

col_peso1, col_peso2, col_peso3 = st.columns(3)
col_peso1.metric('Média de peso exportado', millify(df_exp_presentes['peso_l'].mean(), precision=2))
col_peso2.metric('Mediana de peso exportado', millify(df_exp_presentes['peso_l'].median(), precision=2))




st.write(df_exp_presentes[['peso_l', 'valor_usd']].describe(percentiles=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99]))
st.write(df_exp_presentes.query('peso_l > 2502632.98'))
