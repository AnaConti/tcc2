import cv2
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

def extrair_cores_dominantes(imagem_path, n_cores=5, salvar_como=None):
    imagem = cv2.imread(imagem_path)
    if imagem is None:
        print("Erro: imagem não encontrada.")
        return
    imagem = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
    imagem = cv2.resize(imagem, (200, 200))
    imagem_array = imagem.reshape((-1, 3))

    kmeans = KMeans(n_clusters=n_cores, random_state=42)
    kmeans.fit(imagem_array)

    cores = kmeans.cluster_centers_.astype(int)
    labels = kmeans.labels_

    _, counts = np.unique(labels, return_counts=True)
    proporcoes = counts / counts.sum()

    # Ordena as cores pela proporção (opcional)
    idx_ordenado = np.argsort(-proporcoes)
    cores = cores[idx_ordenado]
    proporcoes = proporcoes[idx_ordenado]


    # Plot
    plt.figure(figsize=(8, 2))
    for i in range(n_cores):
        cor_rgb = cores[i] / 255  # normaliza para 0–1
        plt.bar(i, proporcoes[i], color=cor_rgb, width=1)
    plt.title("Paleta de cores dominantes")
    plt.xticks([])
    plt.yticks([])

    if salvar_como:
        plt.savefig(salvar_como)
        print(f"Gráfico salvo como: {salvar_como}")
    else:
        plt.show()

    return cores, proporcoes


cores, proporcoes = extrair_cores_dominantes("image_mais_clara.png", n_cores=40, salvar_como="paleta_frame3_1.png")

