import numpy as np
import matplotlib.pyplot as plt

import dados


def cria_grafico_producao_versus_exportacao(df_vinho, df_total):
    fig, ax1 = plt.subplots()

    prod_color = 'green'
    ax1.plot(df_vinho.index,df_vinho['prod_total_Ml'],color=prod_color)
    ax1.set_ylabel("Produção (milhões litros)", color=prod_color)
    ax1.tick_params(axis='y', labelcolor=prod_color)
    ax1.set_ylim(ymin=50, ymax=500)

    ax2 = ax1.twinx()

    exp_color = 'red'
    ax2.plot(df_total.index,df_total['peso_Ml'],color=exp_color)
    ax2.set_ylabel("Exportação (milhões litros)", color=exp_color)
    ax2.tick_params(axis='y', labelcolor=exp_color)
    ax2.set_ylim(ymin=0, ymax=50)

    ax1.set_title("Produção x Exportação de Vinhos e Espumantes no Brasil")
    ax1.grid(ls="--")
    
    return fig


def cria_grafico_de_representatividade_de_exportacao_no_brasil(df_representatividade):
    media_pct_Ml = df_representatividade.mean()

    fig, ax = plt.subplots()
    ax.plot(df_representatividade, color = 'black')
    ax.set_title('Representatividade de exportação no Brasil')
    ax.set_ylabel("%Representatividade")
    ax.grid(ls="--")
    ax.axhline(media_pct_Ml, linestyle='--', color='red', linewidth=1, alpha=0.5)
    ax.annotate(f'{media_pct_Ml:.2f} Média % de representatividade', xy=(2016, media_pct_Ml), xytext=(-10, 40),
                textcoords='offset points', arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-.5'), color='k')

    return fig


def cria_grafico_de_quantidade_de_paises_exportados(df_exportacao):
    df_tem_medidas = df_exportacao[(df_exportacao['valor_usd'] != 0) & (df_exportacao['peso_l'] != 0)]
    df_pais_com_medidas_por_ano = df_tem_medidas.groupby('ano')[['País']].nunique()

    fig, ax = plt.subplots()

    ax.plot(df_pais_com_medidas_por_ano.index,df_pais_com_medidas_por_ano['País'],alpha=0.5)
    ax.set_title("Aumento de países para os quais o Brasil exportou")
    ax.set_ylabel("% Variação")
    ax.grid(ls="--")

    return fig


def cria_grafico_top_10_paises_consumidores(df):
    df = df.reset_index().sort_values(by='peso_Ml', ascending=True)

    fig, ax = plt.subplots()
    ax.barh(df['País'], df['peso_Ml'])
    ax.set_title('Top 10 países por litro de vinho e espumantes exportados')
    ax.set_xlabel('Total de litros (em Milhões)')

    return fig


def min_square(X, Y, n):
    if len(Y) < n:
        return np.nan
    
    a = (n*np.sum(X*Y) - np.sum(X)*np.sum(Y))/(n*np.sum(X**2) - np.sum(X)**2)
    b = np.mean(Y) - a * np.mean(X)

    return (a,b)


def cria_grafico_da_tendencia_de_crescimento_de_valor(df_exp_total):
    anos_previsao = np.arange(2024, 2026+1)
    anos = df_exp_total.index

    (a, b) = min_square(anos, df_exp_total['usd_por_l'], anos.size)
    anos_previsao_usd_por_l = a * anos_previsao + b
    
    media_usd_por_l = df_exp_total['usd_por_l'].mean()

    xticks = df_exp_total.index.to_list() + list(anos_previsao)

    fig, ax = plt.subplots()
    ax.plot(anos, df_exp_total['usd_por_l'], color='blue')
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
    return fig


def cria_grafico_de_variacao_percentual_de_exportacao(df):
    fig, ax = plt.subplots()

    ax.bar(df.index, df['pct_var_peso'], color = 'red',alpha=0.5)
    ax.set_title("Variação Percentual de Exportação de Vinhos e Espumantes no Brasil")
    ax.set_ylabel("% Variação")
    ax.grid(ls="--")

    return fig


def cria_grafico_de_valores_anuais_de_exportacao(df):
    color = 'tab:red'
    anos = df.index

    anos_previsao = np.arange(2024, 2026+1)
    xticks = df.index.to_list() + list(anos_previsao)

    y = df['peso_Ml']
    media_peso_Ml = df['peso_Ml'].mean()
    media_peso_kg_M = df['peso_Ml'].mean()

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
    
    return fig


def cria_grafico_de_importacao_dos_maiores_paises(paises_maior_valor_total, df_exp):
    fig, ax = plt.subplots()

    for p in paises_maior_valor_total:
        df_exp_vinho_pais = df_exp.query('@p in País')
        ax.plot(df_exp_vinho_pais['ano'], df_exp_vinho_pais['valor_usd_M'])


    ax.legend(paises_maior_valor_total, loc='upper right', fontsize='small')
    ax.set_xlabel('Ano')
    ax.set_ylabel('Valor (milhões USD)')
    ax.grid(linestyle='--', alpha=0.5)

    return fig
    

def cria_grafico_de_previsao_com_paraguai(df_exportacao, df_total_por_ano):
    fig, ax = plt.subplots()

    df_exp_vinho_pais = df_exportacao[df_exportacao['País'] == 'Paraguai']

    anos = df_total_por_ano.index
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

    return fig


def cria_grafico_de_previsao_com_haiti(df_exportacao, df_total_ano):
    fig, ax = plt.subplots()

    df_exp_vinho_pais = df_exportacao[df_exportacao['País'] == 'Haiti']

    anos = df_total_ano.index
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

    return fig


def cria_grafico_de_previsao_com_eua(df_exportacao, df_total_ano):
    fig, ax = plt.subplots()

    df_exp_vinho_pais = df_exportacao[df_exportacao['País'] == 'Estados Unidos']

    anos = df_total_ano.index
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

    return fig
