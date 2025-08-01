import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ast # Para converter a string RGB de volta para lista/tupla

df = pd.read_csv('analise_cores_teste_episodio.csv')

# Converte as strings de RGB de volta para listas/tuplas de inteiros
# Isso é importante para manipulações numéricas ou plotagem de cores
for col in df.columns:
    if 'cor_' in col and '_rgb' in col:
        df[col] = df[col].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else None)


def plotar_paleta_de_dataframe(df_linha, n_cores_max=5):
    plt.figure(figsize=(8, 2))
    cores = []
    proporcoes = []
    for i in range(1, n_cores_max + 1):
        cor_col = f'cor_{i}_rgb'
        prop_col = f'proporcao_cor_{i}'
        if cor_col in df_linha and df_linha[cor_col] is not None:
            cores.append(df_linha[cor_col])
            proporcoes.append(df_linha[prop_col])
        else:
            break # Pára se não houver mais cores

    for i in range(len(cores)):
        cor_rgb_norm = np.array(cores[i]) / 255
        plt.bar(i, proporcoes[i], color=cor_rgb_norm, width=1)
    plt.title(f"Paleta de Cores do Frame: {df_linha['nome_frame']}")
    plt.xticks([])
    plt.yticks([])
    plt.show()

# Exemplo: Plotar a paleta do primeiro frame do DataFrame
# Certifique-se de que a coluna 'cor_1_rgb' e outras foram convertidas de string para lista/tupla
plotar_paleta_de_dataframe(df.iloc[100], n_cores_max=5)

def calcular_rgb_medio_ponderado(row, n_cores_max=5):
    total_r, total_g, total_b = 0, 0, 0
    total_proporcao = 0
    for i in range(1, n_cores_max + 1):
        cor_col = f'cor_{i}_rgb'
        prop_col = f'proporcao_cor_{i}'
        if cor_col in row and row[cor_col] is not None:
            r, g, b = row[cor_col]
            proporcao = row[prop_col]
            total_r += r * proporcao
            total_g += g * proporcao
            total_b += b * proporcao
            total_proporcao += proporcao

    if total_proporcao == 0:
        return None
    return [int(total_r / total_proporcao), int(total_g / total_proporcao), int(total_b / total_proporcao)]

df['rgb_medio_frame'] = df.apply(lambda row: calcular_rgb_medio_ponderado(row, n_cores_max=5), axis=1)

# Converter RGB médio para uma representação numérica para cálculo de saturação/luminosidade
# Ou calcular saturação/luminosidade diretamente do RGB médio.
# Ex: Para Luminosidade (simples): (R*0.299 + G*0.587 + B*0.114) / 255
def rgb_to_luminosity(rgb):
    if rgb is None: return None
    return (rgb[0]*0.299 + rgb[1]*0.587 + rgb[2]*0.114) / 255

df['luminosidade_frame'] = df['rgb_medio_frame'].apply(rgb_to_luminosity)

# Média de luminosidade por episódio (se tiver dados de mais de um episódio)
# se df tiver apenas um episódio de teste, a média será para esse episódio
media_luminosidade_episodio = df.groupby(['temporada', 'episodio'])['luminosidade_frame'].mean().reset_index()
# print("\nMédia de Luminosidade por Episódio:")
# print(media_luminosidade_episodio)