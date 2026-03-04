import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import ast
import os
import time
import psutil
from tqdm import tqdm

def quantizar_cor(rgb_tuple, base=32):
    if rgb_tuple is None: return None
    return tuple((np.array(rgb_tuple) // base) * base)

def processar_chunk_e_salvar(chunk, n_cores_max, caminho_temp_medias):
    for col in chunk.columns:
        if 'cor_' in col and '_rgb' in col:
            chunk[col] = chunk[col].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else None)
    
    chunk['episodio_numero'] = chunk['episodio'].str.extract(r'(\d+)').astype(int)
    chunk['temporada_numero'] = chunk['temporada'].str.extract(r'(\d+)').astype(int)
    chunk['identificador_episodio'] = chunk['temporada_numero'] * 100 + chunk['episodio_numero']

    media_por_episodio_chunk = chunk.groupby(['identificador_episodio']).agg(
        temporada_rotulo=('temporada', 'first'),
        episodio_rotulo=('episodio', 'first'),
        luminosidade_media=('luminosidade', 'mean'),
        saturacao_media=('saturacao', 'mean'),
        contraste_medio=('contraste', 'mean')
    ).reset_index()
    
    media_por_episodio_chunk.to_csv(caminho_temp_medias, mode='a', header=not os.path.exists(caminho_temp_medias), index=False)
    
    cores_list = []
    for i in range(1, n_cores_max + 1):
        temp_df = chunk[[f'cor_{i}_rgb', f'proporcao_cor_{i}']].copy()
        temp_df.columns = ['rgb', 'proporcao']
        cores_list.append(temp_df)
    
    cores_total = pd.concat(cores_list).dropna()
    cores_total['rgb_agrupado'] = cores_total['rgb'].apply(lambda x: quantizar_cor(x, base=32))
    
    dominancia_chunk = cores_total.groupby('rgb_agrupado')['proporcao'].sum()
    
    return dominancia_chunk

def plotar_graficos(media_por_episodio, df_dominancia):
    top_cores = df_dominancia.sort_values(ascending=False).head(15)
    cores_rgb_norm = [np.array(cor) / 255.0 for cor in top_cores.index]
    labels_rgb = [str(cor) for cor in top_cores.index]

    plt.figure(figsize=(12, 7))
    plt.bar(range(len(top_cores)), top_cores.values, color=cores_rgb_norm)
    plt.title('Assinatura Cromática: Tons Dominantes Agrupados (Base 32)')
    plt.xlabel('Tons (Valores RGB Quantizados)')
    plt.ylabel('Soma de Proporção Acumulada')
    plt.xticks(range(len(top_cores)), labels_rgb, rotation=45)
    plt.tight_layout()
    plt.savefig('grafico_tons_agrupados.png')
    
    media_por_episodio.sort_values(by='identificador_episodio', inplace=True)
    plt.figure(figsize=(20, 8))
    indices = np.arange(len(media_por_episodio))
    plt.plot(indices, media_por_episodio['luminosidade_media'], label='Luminosidade', color='#3498db')
    plt.plot(indices, media_por_episodio['saturacao_media'], label='Saturação', color='#e67e22')
    plt.plot(indices, media_por_episodio['contraste_medio'], label='Contraste', color='#2ecc71')
    
    plt.title('Evolução Estética de Supernatural ao Longo das Temporadas')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.savefig('evolucao_estetica_final.png')

def capturar_metricas(inicio_tempo):
    tempo = time.time() - inicio_tempo
    memoria = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    return tempo, memoria

if __name__ == "__main__":
    caminho_csv = 'resultados/analise_supernatural_completa2.csv' 
    CHUNK_SIZE = 50000 
    n_cores_max = 25
    inicio_proc = time.time()

    caminho_temp_medias = 'temp_medias.csv'
    if os.path.exists(caminho_temp_medias): os.remove(caminho_temp_medias)

    if not os.path.exists(caminho_csv):
        print(f"Erro: Arquivo '{caminho_csv}' não encontrado.")
    else:
        df_dominancia_total = pd.Series(dtype='float64')
        
        for chunk in tqdm(pd.read_csv(caminho_csv, chunksize=CHUNK_SIZE), desc="Agregando Big Data"):
            dominancia_chunk = processar_chunk_e_salvar(chunk, n_cores_max, caminho_temp_medias)
            df_dominancia_total = df_dominancia_total.add(dominancia_chunk, fill_value=0)
        
        media_final = pd.read_csv(caminho_temp_medias).groupby('identificador_episodio').mean(numeric_only=True).reset_index()
        
        plotar_graficos(media_final, df_dominancia_total)
        
        tempo, memoria = capturar_metricas(inicio_proc)
        print(f"\n{'='*40}\nRELATÓRIO DE ENGENHARIA DE DADOS\n{'='*40}")
        print(f"Tempo de Processamento: {tempo:.2f}s")
        print(f"Pico de Memória RAM: {memoria:.2f} MB")
        print(f"{'='*40}")