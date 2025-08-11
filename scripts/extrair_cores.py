import cv2
import numpy as np
from sklearn.cluster import KMeans
import os
import pandas as pd
from tqdm import tqdm


def calcular_luminosidade(imagem):
    if imagem is None: return None
    luminosidade = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    return np.mean(luminosidade)

def calcular_saturacao(imagem):
    if imagem is None: return None
    hsv = cv2.cvtColor(imagem, cv2.COLOR_BGR2HSV)
    saturacao = hsv[:, :, 1]
    return np.mean(saturacao)

def calcular_contraste(imagem):
    if imagem is None: return None
    grayscale = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    return np.std(grayscale)


def extrair_cores_dominantes(imagem, n_cores):
    if imagem is None:
        return None, None
    imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
    imagem_rgb = cv2.resize(imagem_rgb, (100, 100))
    imagem_array = imagem_rgb.reshape((-1, 3))
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

def analisar_cores_por_temporada(pasta_raiz_frames, temporada_alvo, n_cores_por_frame, pasta_saida_csv):
    caminho_temporada = os.path.join(pasta_raiz_frames, temporada_alvo)
    
    if not os.path.isdir(caminho_temporada):
        print(f"Erro: A pasta da temporada '{temporada_alvo}' não foi encontrada em '{pasta_raiz_frames}'.")
        return
    
    resultados_analise_temporada = []

    print(f"\n--- INICIANDO ANÁLISE DE CORES DA {temporada_alvo.upper()} ---")
    
    for pasta_episodio in sorted(os.listdir(caminho_temporada)):
        caminho_episodio = os.path.join(caminho_temporada, pasta_episodio)
        if not os.path.isdir(caminho_episodio):
            continue
        
        print(f"  - Processando episódio: {pasta_episodio}")
        
        frames_do_episodio = [f for f in os.listdir(caminho_episodio) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        for nome_frame in tqdm(sorted(frames_do_episodio), desc=f"    Analisando frames em {pasta_episodio}"):
            caminho_frame = os.path.join(caminho_episodio, nome_frame)
            
            imagem = cv2.imread(caminho_frame)
            
            cores, proporcoes = extrair_cores_dominantes(imagem, n_cores=n_cores_por_frame)

            if cores is not None:
                luminosidade = calcular_luminosidade(imagem)
                saturacao = calcular_saturacao(imagem)
                contraste = calcular_contraste(imagem)

                linha_resultado = {
                    "temporada": temporada_alvo,
                    "episodio": pasta_episodio,
                    "nome_frame": nome_frame,
                    "luminosidade": luminosidade,
                    "saturacao": saturacao,
                    "contraste": contraste,
                }
                
                for i in range(n_cores_por_frame):
                    if i < len(cores):
                        linha_resultado[f"cor_{i+1}_rgb"] = str(cores[i].tolist())
                        linha_resultado[f"proporcao_cor_{i+1}"] = proporcoes[i]
                    else:
                        linha_resultado[f"cor_{i+1}_rgb"] = None
                        linha_resultado[f"proporcao_cor_{i+1}"] = None
                
                resultados_analise_temporada.append(linha_resultado)

    df_resultados = pd.DataFrame(resultados_analise_temporada)
    csv_saida_temporada = os.path.join(pasta_saida_csv, f"analise_{temporada_alvo}.csv")
    df_resultados.to_csv(csv_saida_temporada, index=False)
    print(f"\nAnálise da {temporada_alvo.upper()} concluída! Resultados salvos em '{csv_saida_temporada}'.")
    print(f"Total de frames analisados nesta temporada: {len(df_resultados)}")

if __name__ == "__main__":
    pasta_raiz_dos_frames = "frames" 
    pasta_saida_resultados = "resultados"
    
    if not os.path.isdir(pasta_saida_resultados):
        os.makedirs(pasta_saida_resultados)
        print(f"Pasta de resultados '{pasta_saida_resultados}' criada.")
    
    temporada_alvo_para_analisar = "supernatural.s06"  
    n_cores_para_analise = 25
    
    print("--- INICIANDO ANÁLISE DE CORES AVANÇADA ---")
    analisar_cores_por_temporada(
        pasta_raiz_frames=pasta_raiz_dos_frames,  
        temporada_alvo=temporada_alvo_para_analisar,
        n_cores_por_frame=n_cores_para_analise,
        pasta_saida_csv=pasta_saida_resultados
    )
    
    print("\nPROCESSO COMPLETO. O arquivo CSV foi gerado para a temporada especificada.")