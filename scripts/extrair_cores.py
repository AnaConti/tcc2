import cv2
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import os
import pandas as pd
from tqdm import tqdm

# --- Sua função original para extrair cores dominantes (sem alterações) ---
def extrair_cores_dominantes(imagem_path, n_cores=5):
    imagem = cv2.imread(imagem_path)
    if imagem is None:
        return None, None
    imagem = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
    imagem = cv2.resize(imagem, (100, 100))
    imagem_array = imagem.reshape((-1, 3))
    kmeans = KMeans(n_clusters=n_cores, random_state=42, n_init='auto')
    kmeans.fit(imagem_array)
    cores = kmeans.cluster_centers_.astype(int)
    labels = kmeans.labels_
    _, counts = np.unique(labels, return_counts=True)
    proporcoes = counts / counts.sum()
    idx_ordenado = np.argsort(-proporcoes)
    cores = cores[idx_ordenado]
    proporcoes = proporcoes[idx_ordenado]
    return cores, proporcoes

# --- Função principal para processar TODOS os frames na pasta 'teste' ---
# Esta é a parte que vamos adaptar
def analisar_cores_em_lote_adaptado(pasta_com_frames, n_cores_por_frame=5, output_csv="analise_cores_frames.csv", temporada="sXX", episodio="eYY"):
    """
    Percorre a pasta especificada, analisa as cores dominantes de cada frame
    e salva os resultados em um arquivo CSV.
    Assume que todos os frames são do mesmo episódio.

    Args:
        pasta_com_frames (str): Caminho para a pasta que contém os frames diretamente
                                (ex: 'scripts/teste/').
        n_cores_por_frame (int): Número de cores dominantes a extrair por frame.
        output_csv (str): Nome do arquivo CSV para salvar os resultados.
        temporada (str): Identificador da temporada para esses frames (ex: "s01").
        episodio (str): Identificador do episódio para esses frames (ex: "e01").
    """
    resultados_analise = []

    if not os.path.exists(pasta_com_frames):
        print(f"Erro: A pasta '{pasta_com_frames}' não foi encontrada.")
        return

    # Lista todos os arquivos de frame na pasta
    frames_encontrados = [f for f in os.listdir(pasta_com_frames) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not frames_encontrados:
        print(f"Nenhum frame encontrado na pasta '{pasta_com_frames}'. Verifique o caminho e as extensões dos arquivos.")
        return

    print(f"\nProcessando frames da pasta: {pasta_com_frames}")
    print(f"Assumindo Temporada: {temporada}, Episódio: {episodio}")

    for nome_frame in tqdm(sorted(frames_encontrados), desc=f"Analisando frames em {pasta_com_frames}"):
        caminho_frame = os.path.join(pasta_com_frames, nome_frame)
        
        cores, proporcoes = extrair_cores_dominantes(caminho_frame, n_cores=n_cores_por_frame)

        if cores is not None:
            linha_resultado = {
                "temporada": temporada,
                "episodio": episodio,
                "nome_frame": nome_frame,
            }
            
            for i in range(n_cores_por_frame):
                if i < len(cores):
                    linha_resultado[f"cor_{i+1}_rgb"] = str(cores[i].tolist())
                    linha_resultado[f"proporcao_cor_{i+1}"] = proporcoes[i]
                else:
                    linha_resultado[f"cor_{i+1}_rgb"] = None
                    linha_resultado[f"proporcao_cor_{i+1}"] = None
            
            resultados_analise.append(linha_resultado)

    df_resultados = pd.DataFrame(resultados_analise)
    df_resultados.to_csv(output_csv, index=False)
    print(f"\nAnálise de cores concluída! Resultados salvos em '{output_csv}'.")
    print(f"Total de frames analisados: {len(df_resultados)}")

# --- COMO USAR ---
if __name__ == "__main__":
    # Supondo que você está executando este script de dentro da pasta 'scripts/'
    # E os frames estão em 'scripts/teste/'
    
    # 1. Defina o caminho para a pasta que contém seus frames diretamente
    # Caminho relativo se você estiver na pasta 'scripts'
    pasta_dos_frames = "teste/" # Se você executar o script da pasta 'scripts'
    
    # Se você for executar o script de dentro da pasta 'teste' (navegar para 'teste' no terminal e executar)
    # pasta_dos_frames = "./" # ou "."

    # 2. Defina quantas cores dominantes você quer por frame
    num_cores_por_frame = 5

    # 3. Nome do arquivo CSV de saída (será salvo na mesma pasta do script de análise)
    arquivo_csv_saida = "analise_cores_teste_episodio.csv"

    # 4. **IMPORTANTE:** Como a estrutura não tem 'sXX/eYY', você precisa informar a temporada e o episódio
    # manualmente para este batch de frames. Adapte estes valores!
    temporada_atual = "s01"
    episodio_atual = "e01"

    print("Iniciando a análise de cores dos frames do episódio de teste...")
    analisar_cores_em_lote_adaptado(
        pasta_com_frames=pasta_dos_frames,
        n_cores_por_frame=num_cores_por_frame,
        output_csv=arquivo_csv_saida,
        temporada=temporada_atual,
        episodio=episodio_atual
    )
    print("Processo concluído. O arquivo CSV contém os resultados da análise.")