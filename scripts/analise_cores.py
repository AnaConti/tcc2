import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import ast
import os
from tqdm import tqdm

def processar_chunk_e_salvar(chunk, n_cores_max, caminho_temp_medias, caminho_temp_dominancia):

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
    
    cores_empilhadas = pd.DataFrame()
    for i in range(1, n_cores_max + 1):
        temp_df = chunk[[f'cor_{i}_rgb', f'proporcao_cor_{i}']].copy()
        temp_df.rename(columns={f'cor_{i}_rgb': 'rgb', f'proporcao_cor_{i}': 'proporcao'}, inplace=True)
        cores_empilhadas = pd.concat([cores_empilhadas, temp_df], ignore_index=True)
    cores_empilhadas.dropna(inplace=True)
    cores_empilhadas['rgb_tuple'] = cores_empilhadas['rgb'].apply(tuple)
    
    dominancia_chunk = cores_empilhadas.groupby('rgb_tuple')['proporcao'].sum()
    
    return dominancia_chunk

def plotar_graficos(media_por_episodio, df_dominancia):
    
    top_5_cores = df_dominancia.sort_values(ascending=False).head(5)
    cores_rgb_tuplas = top_5_cores.index.tolist()
    proporcoes = top_5_cores.values.tolist()
    cores_rgb_norm = [np.array(cor) / 255.0 for cor in cores_rgb_tuplas]
    labels_rgb = [str(cor) for cor in cores_rgb_tuplas]

    plt.figure(figsize=(10, 6))
    plt.bar(range(len(top_5_cores)), proporcoes, color=cores_rgb_norm)
    plt.title('As 5 Cores Mais Dominantes da Série Supernatural')
    plt.xlabel('Cores (valores RGB)')
    plt.ylabel('Proporção Total de Ocorrência')
    plt.xticks(range(len(top_5_cores)), labels_rgb, rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('top_5_cores_dominantes_serie.png')
    print("\nGráfico 'top_5_cores_dominantes_serie.png' gerado com sucesso!")

    media_por_episodio.sort_values(by='identificador_episodio', inplace=True)
    indices_plot = np.arange(len(media_por_episodio))
    
    plt.figure(figsize=(20, 10))
    plt.plot(indices_plot, media_por_episodio['luminosidade_media'], label='Luminosidade Média')
    plt.plot(indices_plot, media_por_episodio['saturacao_media'], label='Saturação Média')
    plt.plot(indices_plot, media_por_episodio['contraste_medio'], label='Contraste Médio')

    plt.title('Evolução do Clima Visual de Supernatural (Temporadas Completas)')
    plt.xlabel('Episódio (Sequencial)')
    plt.ylabel('Média da Métrica')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('evolucao_metricas_serie.png')
    print("Gráfico 'evolucao_metricas_serie.png' gerado com sucesso!")

if __name__ == "__main__":
    caminho_csv = 'resultados/analise_supernatural_completa.csv'
    CHUNK_SIZE = 100000 
    n_cores_max = 25
    
    caminho_temp_medias = 'temp_medias.csv'
    caminho_temp_dominancia = 'temp_dominancia.csv'
    
    if os.path.exists(caminho_temp_medias):
        os.remove(caminho_temp_medias)
    if os.path.exists(caminho_temp_dominancia):
        os.remove(caminho_temp_dominancia)

    if not os.path.exists(caminho_csv):
        print(f"Erro: Arquivo '{caminho_csv}' não encontrado.")
    else:
        print(f"Iniciando a análise de dados em blocos do arquivo '{caminho_csv}'...")
        
        df_dominancia_total = pd.Series(dtype='float64')
        
        for chunk in tqdm(pd.read_csv(caminho_csv, chunksize=CHUNK_SIZE), desc="Processando blocos do dataset"):
            dominancia_chunk = processar_chunk_e_salvar(chunk, n_cores_max, caminho_temp_medias, caminho_temp_dominancia)
            df_dominancia_total = pd.concat([df_dominancia_total, dominancia_chunk]).groupby(level=0).sum()
        
        print("\nProcessamento em blocos concluído. Realizando agregação final no disco...")
        
        media_por_episodio_final = pd.read_csv(caminho_temp_medias)
        media_por_episodio_final = media_por_episodio_final.groupby('identificador_episodio').agg(
            temporada_rotulo=('temporada_rotulo', 'first'),
            episodio_rotulo=('episodio_rotulo', 'first'),
            luminosidade_media=('luminosidade_media', 'mean'),
            saturacao_media=('saturacao_media', 'mean'),
            contraste_medio=('contraste_medio', 'mean')
        ).reset_index()
        
        plotar_graficos(media_por_episodio_final, df_dominancia_total)