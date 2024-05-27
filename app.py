import streamlit as st
import altair as alt
import io
import unicodedata
from millify import millify

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

def min_square(X, Y, n):
    if len(Y) < n:
        return np.nan
    
    a = (n*np.sum(X*Y) - np.sum(X)*np.sum(Y))/(n*np.sum(X**2) - np.sum(X)**2)
    b = np.mean(Y) - a * np.mean(X)

    return (a,b)

df_exp_vinho = pd.read_csv('dados/ExpVinhoOriginal.csv', sep=';')

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
df_exp_vinho_pivot['ano'] = df_exp_vinho_pivot['ano'].astype(int)

df_exp_espumante = pd.read_csv('dados/ExpEspumantesOriginal.csv', sep=';')
df_exp_espumante = df_exp_espumante.drop(columns=df_exp_espumante.columns[2:((2009-1970)*2+2)])

df_exp_espumante_melt = df_exp_espumante.melt(id_vars=['País'], value_vars=df_exp_espumante.columns[2:], var_name='ano_medida', value_name='valor')
df_exp_espumante_melt['ano'] = df_exp_espumante_melt['ano_medida'].apply(lambda x: x.split('.')[0])
df_exp_espumante_melt['medida'] = df_exp_espumante_melt['ano_medida'].apply(lambda x: 'valor_usd' if '.1' in x else 'peso_l')
df_exp_espumante_melt = df_exp_espumante_melt.drop('ano_medida', axis=1)

df_exp_espumante_pivot =  df_exp_espumante_melt.pivot(index=['País', 'ano'], columns='medida', values='valor').reset_index()
df_exp_espumante_pivot.columns.name=''
df_exp_espumante_pivot['ano'] = df_exp_espumante_pivot['ano'].astype(int)

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
df_exp['peso_Ml'] = df_exp['peso_l'] / 1_000_000
df_exp['valor_usd_M'] = df_exp['valor_usd'] / 1_000_000
df_exp['usd_por_l'] = df_exp['valor_usd'] / df_exp['peso_l']
df_exp = df_exp.fillna(0)
df_exp.loc[386, 'usd_por_l'] = 0

df_paises_sem_importacao = df_exp.groupby('País').mean(numeric_only=True).query('valor_usd == 0 & peso_l == 0').reset_index()

nomes_paises_sem_importacao = df_paises_sem_importacao['País'].tolist()
df_paises_com_importacao = df_exp.query('País not in @nomes_paises_sem_importacao').reset_index()

df_exp_total_por_ano = df_paises_com_importacao.groupby('ano')[['peso_Ml', 'valor_usd_M', 'usd_por_l']].sum()
df_exp_total_por_ano['pct_var_peso'] = df_exp_total_por_ano['peso_Ml'].pct_change()*100

df_prod_vinho = pd.read_csv('dados/ProducaoVinhoOriginal.csv', sep=';')
df_prod_vinho = df_prod_vinho.loc[[0,4,14]]
df_prod_vinho = df_prod_vinho.drop(columns = [str(y) for y in range(1970,2009)])

df_prod_vinho_melt = pd.melt(df_prod_vinho, id_vars=['produto'], value_vars= df_prod_vinho.columns[3:], var_name='ano', value_name='producao')
df_prod_vinho_melt['ano'] = df_prod_vinho_melt['ano'].astype(int)

df_prod_vinho_pivot = df_prod_vinho_melt.pivot_table(index=['ano'], columns='produto', values='producao').reset_index()
df_prod_vinho_pivot.columns = ['ano',  'derivados','vinho_mesa','vinho_fino']
df_prod_vinho_pivot['prod_total'] = df_prod_vinho_pivot['derivados'] + df_prod_vinho_pivot['vinho_mesa'] + df_prod_vinho_pivot['vinho_fino']
df_prod_vinho_pivot['prod_total_Ml'] = df_prod_vinho_pivot['prod_total']/1_000_000
df_prod_vinho_pivot = df_prod_vinho_pivot.set_index('ano')

representatividade_exportacao = df_exp_total_por_ano['peso_Ml'] / df_prod_vinho_pivot['prod_total_Ml']*100

peso_Ml_totais_por_pais = df_exp.groupby('País')[['peso_Ml']].sum().sort_values(by='peso_Ml', ascending=False)
top_peso_kg = peso_Ml_totais_por_pais.head(10)

anos_previsao = np.arange(2024, 2026+1)
anos = df_exp_total_por_ano.index

media_usd_por_l = df_exp_total_por_ano['usd_por_l'].mean()

(a, b) = min_square(anos, df_exp_total_por_ano['usd_por_l'], anos.size)
anos_previsao_usd_por_l = a * anos_previsao + b

valor_USD_totais_por_pais = df_exp.groupby('País')[['valor_usd_M']].sum().sort_values(by='valor_usd_M', ascending=False)
paises_maior_valor_total = valor_USD_totais_por_pais.head(10).index.to_list()

#### FIM DO TRATAMENTO DOS DATAFRAMES ####

st.write("# Fase 1 - Data Analysis and Exploration")
st.write('##### Tech Challenge - Análise da exportação de vinhos e espumantes pelo Brasil')
st.write('''###### Grupo 46
* Integrantes: 
    * Alexandre Aquiles Sipriano da Silva (alexandre.aquiles@alura.com.br)
    * Gabriel Machado Costa (gabrielmachado2211@gmail.com)
    * Caio Martins Borges (caio.borges@bb.com.br)
    * Cácio José da Costa Silva (cacio.costa@alura.com.br)
    * Tais de Assis Santos (tais.santos.mg@hotmail.com)
''')
st.divider()

st.write("## O Brasil no contexto mundial de exportação de vinho")
st.write("### Produção e cultivo")
st.write('O Brasil ocupa o 14º lugar no ranking de exportação de vinhos em nível mundial, marcando um avanço significativo de 12 posições em relação ao último levantamento realizado pela Wine Intelligence. Essa ascensão foi validada pela OIV (International Organisation of Vine), instituição de renome global no setor.')
with st.expander('Visualizar ranking de produção segundo a International Organisation of Vine and Wine'):
    st.image('imagens/ranking-de-producao.png', caption='International Organisation of Vine and Wine - https://www.oiv.int/sites/default/files/2024-04/OIV_STATE_OF_THE_WORLD_VINE_AND_WINE_SECTOR_IN_2023.pdf', use_column_width='auto')

st.write("<br>", unsafe_allow_html=True)
st.write('Além disso, o estudo apresentado pela OIV em 2023 revela que o Brasil detém apenas 1,3% das terras destinadas ao cultivo de vinhedos em todo o mundo, situando-se na 22ª posição. Esses dados contrastam com a realidade de sermos o 5º maior país em extensão territorial no planeta.')
with st.expander('Visualizar ranking de área de cultivo de vinho segundo a International Organisation of Vine and Wine'):
    st.image('imagens/ranking-de-area.png', caption='International Organisation of Vine and Wine - https://www.oiv.int/sites/default/files/2024-04/OIV_STATE_OF_THE_WORLD_VINE_AND_WINE_SECTOR_IN_2023.pdf', use_column_width='auto')

st.write('Com essas informações iniciais sobre produção e exportação de vinhos e espumantes, já pode-se comparar essas duas áreas e perceber que o Brasil produz muito mais do que exporta. Isso significa que grande parte do consumo interno que demanda essa alta produção, e que o país ainda tem grandes janelas de oportunidade a explorar com parcerias comerciais. O gráfico abaixo dá a real dimensão da distância entre produção e exportação de vinhos e espumantes.')

fig, ax = plt.subplots()

ax.plot(df_prod_vinho_pivot.index,df_prod_vinho_pivot['prod_total_Ml'], color = 'green')
ax.plot(df_exp_total_por_ano.index,df_exp_total_por_ano['peso_Ml'],color = 'red')
ax.set_title("Produção x Exportação de Vinhos e Espumantes no Brasil")
ax.set_ylabel("(milhões litros)")
ax.legend(["Produção total","Exportação Total"])
ax.set_yscale("log")
ax.grid(ls="--")

st.pyplot(fig)

st.write("<br>", unsafe_allow_html=True)
st.write('Nota-se também que no último ano a produção de vinho mundial teve uma queda de 9.6%, considerando vinhos e espumantes, enquanto que o Brasil apresentou um crescimento, indo na contramão do mundo em 2023, obtendo um crescimento de 12,6 p.p. em relação ao último período.')
st.write('Grande parte da baixa mundial de produção se deu pelas condições climáticas e econômicas apresentadas no último ano - o que desencadeia não apenas em dificuldades, mas também em oportunidades, frente à concorrência com os demais players.')



st.write("### Potencial e oportunidades de crescimento")
st.write('Embora o Brasil não tenha uma reputação consolidada como grande exportador de vinhos, há um vasto potencial que nossa empresa pode explorar,  já que apenas, em média, cerca de 1,86% da nossa produção de vinhos e espumantes é destinada ao mercado externo. Estamos diante de um mar azul de oportunidades, e há um longo caminho a percorrer para capitalizarmos totalmente esse mercado.')
st.write('Conforme imagem abaixo, mesmo que localizados na maior das seis regiões produtoras do país, o percentual representativo de exportação de vinhos e espumantes, versus produção, manteve-se historicamente baixo.')

media_pct_Ml = representatividade_exportacao.mean()

fig, ax = plt.subplots()
ax.plot(representatividade_exportacao, color = 'black', marker = 'o')
ax.set_title('Representatividade de exportação no Brasil')
ax.set_ylabel("%Representatividade")
ax.grid(ls="--")
ax.axhline(media_pct_Ml, linestyle='--', color='red', linewidth=1, alpha=0.5)
ax.annotate(f'{media_pct_Ml:.2f} Média % de representatividade', xy=(2016, media_pct_Ml), xytext=(-10, 40),
             textcoords='offset points', arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-.5'), color='k')

st.pyplot(fig, use_container_width=True)

st.write('A quantidade de países para os quais exportamos praticamente dobrou de 2016 para 2023. Mesmo que a relação produção/exportação apresente um valor baixo, ela acompanhou o ritmo do aumento mencionado antes. O que indica que nossa empresa está expandindo em quantidade de compradores e tem aqui a oportunidade de expandir também a quantidade em litros exportados para cada um deles, e por consequência aumentar o percentual de produção exportada. Destacaremos mais adiante nossas principais oportunidades nesse sentido.')

df_tem_medidas = df_exp[(df_exp['valor_usd'] != 0) & (df_exp['peso_l'] != 0)]
df_pais_com_medidas_por_ano = df_tem_medidas.groupby('ano')[['País']].nunique()

fig, ax = plt.subplots()

ax.plot(df_pais_com_medidas_por_ano.index,df_pais_com_medidas_por_ano['País'],alpha=0.5)
ax.set_title("Aumento de países para os quais o Brasil exportou")
ax.set_ylabel("% Variação")
ax.grid(ls="--")

st.pyplot(fig, use_container_width=True)


st.write('Embora tenhamos tido alguns grandes parceiros comerciais no decorrer destes 15 anos, podemos explorar ainda mais algumas oportunidades. Olhando para litros/exportados, nossos 5 (cinco) maiores compradores são: Rússia, Paraguai, Estados Unidos, China e Haiti.')

fig, ax = plt.subplots()
top_peso_kg = top_peso_kg.reset_index().sort_values(by='peso_Ml', ascending=True)

ax.barh(top_peso_kg['País'], top_peso_kg['peso_Ml'])
ax.set_title('Top 10 países por litro de vinho e espumantes exportados')
ax.set_xlabel('Total de litros (em Milhões)')
st.pyplot(fig, use_container_width=True)

st.write("### Futuro otimista - tendência de crescimento em volume e valor")
st.write('Além dos fatores mencionados, é importante destacar o cenário significativo em que o vinho/espumante brasileiro está se tornando uma commodity mais cara para o mercado global. Mesmo assim, continuamos exportando uma quantidade significativa desses produtos. O gráfico abaixo ilustra essa tendência, mostrando como o valor em dólares por litro está aumentando e prevê continuar crescendo nos próximos três anos, alcançando o melhor patamar da história.')

xticks = df_exp_total_por_ano.index.to_list() + list(anos_previsao)

fig, ax = plt.subplots()
ax.plot(anos, df_exp_total_por_ano['usd_por_l'], color='blue')
ax.plot(anos_previsao, anos_previsao_usd_por_l, 'o', color='blue', label='Previsão USD/L')
ax.axhline(media_usd_por_l, linestyle='--', color='g', linewidth=1)
ax.axvline(2023, linestyle='--', color='black', linewidth=1, alpha=0.5)
ax.set_xlabel('Ano')
ax.set_ylabel('USD/L')
ax.set_title('USD/L (anual)')
ax.grid(linestyle='--', alpha=0.5)
ax.set_xticks(xticks[::2])
ax.set_xticklabels(xticks[::2], rotation=45)
ax.legend()
ax.axhline(media_usd_por_l, linestyle='--', color='black', linewidth=1)

fig.tight_layout()
st.pyplot(fig, use_container_width=True)

st.write('Surpreendentemente, poderíamos supor que essa tendência seria influenciada pela valorização de nossa moeda. No entanto, observamos exatamente o oposto. No início de 2009, um dólar equivalia a aproximadamente R\$ 2,34. Ao término de 2023, essa cotação estava na casa dos R$ 4,92, representando um aumento de mais de 100% na desvalorização de nossa moeda em relação ao dólar. Mesmo diante desse cenário desafiador, o setor de vinho e espumante brasileiro continua a expandir suas exportações, e o preço desses produtos no mercado internacional segue em ascensão.')
st.write('Esse fenômeno contraditório desafia as expectativas tradicionais e aponta para a qualidade e competitividade crescentes dos vinhos e espumantes brasileiros. O gráfico abaixo retrata essa dinâmica do dólar.')
with st.expander('Visualizar histórico da cotação do dólar'):
    st.image('imagens/cotacao-dolar.png', caption='Google Finanças', use_column_width='auto')

st.write("### A falta de consistência é um desafio")
st.write('A instabilidade persiste nos dados apresentados pela Embrapa, com o Brasil demonstrando flutuações significativas. Apesar disso, o país tem muito a aprender para se firmar como um dos  líderes neste setor. Os gráficos abaixo ilustram essa realidade: o primeiro revela oscilações positivas seguidas de dois ou três anos de declínio, embora sempre tendendo ao crescimento a longo prazo.')
st.write('Neste contexto, estamos vivendo um período de recuperação, o que representa uma excelente oportunidade de investimento neste ramo. Desde 2020, mantemos um desempenho acima da média, impulsionado principalmente pelo ano de 2009. Portanto, o crescimento é uma realidade, apenas necessitando do direcionamento adequado para seguir adiante.')

fig, ax = plt.subplots()

ax.bar(df_exp_total_por_ano.index,df_exp_total_por_ano['pct_var_peso'], color = 'red',alpha=0.5)
ax.set_title("Variação Percentual de Exportação de Vinhos e Espumantes no Brasil")
ax.set_ylabel("% Variação")
ax.grid(ls="--")

st.pyplot(fig, use_container_width=True)


color = 'tab:red'
y = df_exp_total_por_ano['peso_Ml']
media_peso_Ml = df_exp_total_por_ano['peso_Ml'].mean()
media_peso_kg_M = df_exp_total_por_ano['peso_Ml'].mean()

fig, ax = plt.subplots()
ax.set_xlabel('ano')
ax.set_ylabel('Peso (Milhões Litros)')
ax.plot(anos, y, color=color)
ax.tick_params(axis='y')
ax.set_xticks(xticks[::2])
ax.axhline(media_peso_Ml, linestyle='--', color='k', linewidth=1, alpha=0.5)
ax.set_title("Exportação de Vinhos e Espumantes (Valores anuais em milhões de litros)")
ax.grid(linestyle='--', alpha=0.5)
ax.annotate(f'{media_peso_kg_M:.2f} Média em ML', xy=(2016, media_peso_kg_M), xytext=(-10, 40),
             textcoords='offset points', arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-.5'), color='k')

st.pyplot(fig, use_container_width=True)

####### Análise dos países #######
st.write("## Principais parceiros e oportunidades de colaboração")
st.write("### Paraguai")
st.write('Entre os dez países que mais gastaram nos últimos quinze anos em dólares para adquirir vinho ou espumante brasileiro, destaca-se o Paraguai como o país que mais investiu nesse produto. Essa informação, conforme ilustrado na imagem abaixo, oferece uma oportunidade significativa para estabelecermos um marco em nossos acordos comerciais e nos inspirarmos nessa relação comercial bem-sucedida para futuras negociações. O fato de o Paraguai liderar os gastos com produtos vinícolas brasileiros indica um interesse consolidado nesta oferta e sugere um potencial promissor para expandir ainda mais nossas relações comerciais bilaterais. Portanto, essa constatação pode servir como um ponto de partida valioso para explorar novas oportunidades de cooperação e desenvolvimento mútuo entre os dois países. O Fator Mercosul também nos ajuda com esse país.')

fig, ax = plt.subplots()

for p in paises_maior_valor_total:
    df_exp_vinho_pais = df_exp.query('@p in País')
    ax.plot(df_exp_vinho_pais['ano'], df_exp_vinho_pais['valor_usd_M'])

ax.legend(paises_maior_valor_total, bbox_to_anchor=(1,1), loc='upper left')
ax.set_xlabel('Ano')
ax.set_ylabel('valor (milhões USD)')
ax.grid(linestyle='--', alpha=0.5)

st.pyplot(fig, use_container_width=True)

st.write("##### Previsão de futuro com o Paraguai")
st.write('Com base nas tendências observadas, é possível projetar que o Paraguai continuará liderando os gastos com vinhos e espumantes brasileiros no futuro próximo. Além disso, essa projeção é respaldada pelo fato de que o Paraguai demonstra uma tendência constante de aumentar suas importações desses produtos ano após ano. Essa previsão sugere uma estabilidade e até mesmo um crescimento contínuo nas transações comerciais entre o Brasil e o Paraguai neste setor específico. Portanto, essa perspectiva reforça ainda mais a importância de fortalecer os laços comerciais entre os dois países e explorar estratégias para otimizar essa relação bilateral em benefício mútuo.')

fig, ax = plt.subplots()

df_exp_vinho_pais = df_exp[df_exp['País'] == 'Paraguai']

anos = df_exp_total_por_ano.index
anos_previsao = np.arange(2024, 2026+1)

xticks = anos.to_list() + list(anos_previsao)

color = 'tab:blue'
(a, b) = min_square(anos, df_exp_vinho_pais['valor_usd_M'], anos.size)
anos_previsao_valor_usd = a * anos_previsao + b
ax.set_xlabel('ano')
ax.set_ylabel('Valor USD (em milhões)', color=color)
ax.plot(anos, df_exp_vinho_pais['valor_usd_M'], color=color, alpha=0.7)
ax.plot(anos_previsao, anos_previsao_valor_usd, 'o', color=color, alpha=0.7)
ax.tick_params(axis='y', labelcolor=color)

ax2 = ax.twinx()

color = 'tab:red'
(a, b) = min_square(anos, df_exp_vinho_pais['peso_Ml'], anos.size)
anos_previsao_peso_kg = a * anos_previsao + b
ax2.set_xlabel('ano')
ax2.set_ylabel('Peso Litros (em milhões)', color=color)
ax2.plot(anos, df_exp_vinho_pais['peso_Ml'], color=color, alpha=0.7)
ax2.plot(anos_previsao, anos_previsao_peso_kg, 's', color=color, alpha=0.7)
ax2.tick_params(axis='y', labelcolor=color)

ax.set_title(f"Exportação de Vinhos e Espumantes para Paraguai")
ax.grid(True)
ax.axvline(2023, linestyle='--', color='black', linewidth=1, alpha=0.5)
ax.set_xticks(xticks[::2])

st.pyplot(fig, use_container_width=True)


st.write("### Haiti")
st.write('É surpreendente notar que o Haiti se destaca como o oitavo país que mais importa produtos brasileiros em termos de valor. Esse crescimento constante ao longo dos anos sugere que o Haiti está se tornando um parceiro cada vez mais importante para o Brasil, e é crucial compreender o máximo do potencial desse relacionamento bilateral. Um aspecto notável é o crescimento exponencial das exportações brasileiras para o Haiti de 2019 a 2021. Nesse período, o volume de exportações de vinho e espumante do Brasil aumentou de 0.1 megalitros para 0.6 megalitros por ano, representando um aumento impressionante de 600% em apenas dois anos. Embora tenha havido uma pequena queda em 2022, o cenário continua promissor para esse país.')
st.write('Além disso, apesar da diminuição no volume de litros exportados em 2023, o Brasil registrou seu maior valor arrecadado nesse mesmo ano, o que indica uma valorização crescente por parte dos consumidores haitianos em relação aos vinhos e espumantes brasileiros. Outro fator relevante é a presença brasileira nas missões de paz no Haiti. Como o Brasil é um aliado importante nessas operações, isso estabelece uma conexão adicional entre os dois países. Além de contribuir para a estabilidade e segurança no Haiti, os soldados brasileiros possivelmente propagam a cultura brasileira na região, o que pode influenciar positivamente as preferências de consumo e abrir portas para mais oportunidades comerciais. Assim, o Haiti não apenas se destaca como um parceiro comercial em ascensão, mas também como um importante ponto de conexão estratégica no Caribe para as mercadorias brasileiras.')

fig, ax = plt.subplots()

df_exp_vinho_pais = df_exp[df_exp['País'] == 'Haiti']

anos = df_exp_total_por_ano.index
anos_previsao = np.arange(2024, 2026+1)

xticks = anos.to_list() + list(anos_previsao)

color = 'tab:blue'
(a, b) = min_square(anos, df_exp_vinho_pais['valor_usd_M'], anos.size)
anos_previsao_valor_usd = a * anos_previsao + b
ax.set_xlabel('ano')
ax.set_ylabel('Valor USD (em milhões)', color=color)
ax.plot(anos, df_exp_vinho_pais['valor_usd_M'], color=color, alpha=0.7)
ax.plot(anos_previsao, anos_previsao_valor_usd, 'o', color=color, alpha=0.7)
ax.tick_params(axis='y', labelcolor=color)

ax2 = ax.twinx()

color = 'tab:red'
(a, b) = min_square(anos, df_exp_vinho_pais['peso_Ml'], anos.size)
anos_previsao_peso_kg = a * anos_previsao + b
ax2.set_xlabel('ano')
ax2.set_ylabel('Peso Litros (em milhões)', color=color)
ax2.plot(anos, df_exp_vinho_pais['peso_Ml'], color=color, alpha=0.7)
ax2.plot(anos_previsao, anos_previsao_peso_kg, 's', color=color, alpha=0.7)
ax2.tick_params(axis='y', labelcolor=color)

ax.set_title(f"Previsão de exportação de Vinhos e Espumantes para Haiti")
ax.grid(True)
ax.axvline(2023, linestyle='--', color='black', linewidth=1, alpha=0.5)
ax.set_xticks(xticks[::2])

st.pyplot(fig, use_container_width=True)

st.write("### Estados Unidos")
st.write('A parceria econômica entre Brasil e Estados Unidos é uma das mais significativas para a economia brasileira. Essa relação sólida abrange diversas áreas comerciais, proporcionando uma base sólida para o comércio de produtos entre os dois países. Acordos comerciais e a boa relação diplomática entre Brasil e Estados Unidos simplificam o processo de exportação de produtos brasileiros para o mercado norte-americano, incluindo os vinhos e espumantes produzidos no Brasil.')
st.write('Um ponto importante a ser destacado é a presença da maior comunidade brasileira fora do Brasil nos Estados Unidos, com aproximadamente 1,9 milhão de pessoas. Essa significativa massa de brasileiros que vivem lá não só cria laços culturais e sociais, mas também abre portas para oportunidades comerciais, facilitando a introdução e a promoção de vinhos e espumantes brasileiros no mercado norte-americano.')
st.write('Embora tenha havido uma queda no cenário econômico em 2023, os próximos três anos apresentam perspectivas promissoras. Ainda há espaço para evolução e para a realização de novos acordos comerciais que impulsionem o comércio bilateral entre os dois países. O potencial de mercado nos Estados Unidos é enorme, sendo o país com a terceira maior população do mundo. O crescimento contínuo desse mercado pode até mesmo superar os picos alcançados em 2022, oferecendo oportunidades ainda mais amplas para os produtores de vinho brasileiros.')

fig, ax = plt.subplots()

df_exp_vinho_pais = df_exp[df_exp['País'] == 'Estados Unidos']

anos = df_exp_total_por_ano.index
anos_previsao = np.arange(2024, 2026+1)

xticks = anos.to_list() + list(anos_previsao)

color = 'tab:blue'
(a, b) = min_square(anos, df_exp_vinho_pais['valor_usd_M'], anos.size)
anos_previsao_valor_usd = a * anos_previsao + b
ax.set_xlabel('ano')
ax.set_ylabel('Valor USD (em milhões)', color=color)
ax.plot(anos, df_exp_vinho_pais['valor_usd_M'], color=color, alpha=0.7)
ax.plot(anos_previsao, anos_previsao_valor_usd, 'o', color=color, alpha=0.7)
ax.tick_params(axis='y', labelcolor=color)

ax2 = ax.twinx()

color = 'tab:red'
(a, b) = min_square(anos, df_exp_vinho_pais['peso_Ml'], anos.size)
anos_previsao_peso_kg = a * anos_previsao + b
ax2.set_xlabel('ano')
ax2.set_ylabel('Peso Litros (em milhões)', color=color)
ax2.plot(anos, df_exp_vinho_pais['peso_Ml'], color=color, alpha=0.7)
ax2.plot(anos_previsao, anos_previsao_peso_kg, 's', color=color, alpha=0.7)
ax2.tick_params(axis='y', labelcolor=color)

ax.set_title(f"Previsão de exportação de Vinhos e Espumantes \npara Estados Unidos")
ax.grid(True)
ax.axvline(2023, linestyle='--', color='black', linewidth=1, alpha=0.5)
ax.set_xticks(xticks[::2])

st.pyplot(fig, use_container_width=True)

################################## FIM DO RELATÓRIO #####################################
# st.write('## Tratamento de transformação dos datasets de exportação de vinhos e espumantes')

# st.write('#### Dataset bruto utilizado para análise')
# st.write('Como podemos observar na amostra abaixo, o dataset não é intuitivo. As colunas dos anos sem sufixo indicam o peso exportado. E as colunas com sufixo ".1" indicam o valor vendido.')
# st.write('Além disso, só temos dados consistentes a partir de 2009.')


# st.write(df_exp_vinho.head())

# st.write('Portanto foi necessário excluir os anos de 1970 a 2008. E o dataset foi transformado para facilitar as análises e obtenção de insights. Para isso, foram criadas as colunas **peso_kg** e **valor_usd**')



# st.write('#### Dataset de exportação de vinhos transformado')
# st.write(df_exp_vinho_pivot)


# # buffer = io.StringIO()
# # df.info(buf=buffer)
# # st.text(buffer.getvalue())

# st.write('#### Dataset de exportação de espumantes')
# st.write('O dataset de exportação de espumantes original precisou dos mesmos tratamentos de dados do dataset de vinhos.')


# st.write(df_exp_espumante_pivot)




# ## Merge dos datasets
# st.write('## União dos datasets de vinhos e espumantes')
# st.write('''A última transformação antes das análises consistiu em mesclar os dois datasets. As colunas de peso e valor de cada categoria foram especificadas (*peso_l_vinho, valor_usd_vinho, peso_l_espumante, valor_usd_espumante*), e duas novas colunas com o total dessas informações foram criadas: **peso_l** e **valor_usd**.''')


# st.write(df_exp)

# st.divider()

# ### Análises exploratórias
# st.write('## Análises exploratórias dos dados')
# st.write('#### Informações presentes e ausentes')

# qtd_registros = df_exp['País'].count()
# qtd_registros_zerados = df_exp.query('valor_usd == 0 & peso_l == 0').shape[0]
# percentual_registros_ausentes = (qtd_registros_zerados / qtd_registros) * 100

# col_registros1, col_registros2, col_registros3 = st.columns(3)
# col_registros1.metric('Total de registros', qtd_registros)
# col_registros2.metric('Registros sem informação (zerados)', qtd_registros_zerados)
# col_registros3.metric('Percentual ausente', f'{millify(percentual_registros_ausentes, precision=2)}%')



# st.write(df_paises_sem_importacao)

# qtd_paises = len(df_exp['País'].unique())
# qtd_paises_sem_medidas = df_paises_sem_importacao.shape[0]
# percentual_paises_ausentes = (qtd_paises_sem_medidas / qtd_paises) * 100

# col_paises1, col_paises2, col_paises3 = st.columns(3)
# col_paises1.metric('Quantidade de países', qtd_paises)
# col_paises2.metric('Países sem importação', qtd_paises_sem_medidas)
# col_paises3.metric('Percentual sem importação', f'{millify(percentual_paises_ausentes, precision=2)}%')

# st.write('#### Países que importaram em algum momento')



# st.metric('Anos sem importar', df_paises_com_importacao.query('valor_usd == 0 & peso_l == 0').shape[0])
# st.caption('Mesmo entre os países que importaram do Brasil em algum momento, o número de anos sem importação é grande, representando **57,43%**.')

# st.info('Muitos registros ausentes. Então, a partir daqui, esses registros foram desconsiderados.')

# df_exp_presentes = df_exp.query('not (peso_l == 0 & valor_usd == 0)')
# st.write(df_exp.describe())



# st.write('#### Indicadores sobre o valor vendido')

# col_peso1, col_peso2, col_peso3 = st.columns(3)
# col_peso1.metric('Média de peso exportado', millify(df_exp_presentes['peso_l'].mean(), precision=2))
# col_peso2.metric('Mediana de peso exportado', millify(df_exp_presentes['peso_l'].median(), precision=2))




# st.write(df_exp_presentes[['peso_l', 'valor_usd']].describe(percentiles=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99]))
# st.write(df_exp_presentes.query('peso_l > 2502632.98'))
