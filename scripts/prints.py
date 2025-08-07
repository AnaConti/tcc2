import cv2
import os
import shutil
import re 

def extrair_frames_de_video(caminho_video, pasta_saida_frames, intervalo_segundos=5):
    
    if not os.path.exists(caminho_video):
        print(f"Erro: O arquivo de vídeo não foi encontrado em '{caminho_video}'")
        return

    if not os.path.exists(pasta_saida_frames):
        os.makedirs(pasta_saida_frames)
        print(f"Pasta de saída '{pasta_saida_frames}' criada com sucesso.")
    else:
        print(f"A pasta '{pasta_saida_frames}' já existe. Adicionando frames a ela.")
    
    vidcap = cv2.VideoCapture(caminho_video)

    if not vidcap.isOpened():
        print(f"Erro: Não foi possível abrir o vídeo '{caminho_video}'. Verifique o caminho ou o formato.")
        return

    fps = vidcap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        print("Erro: Não foi possível obter o FPS do vídeo. Possível corrupção ou formato inválido.")
        vidcap.release()
        return
        
    duracao_total = vidcap.get(cv2.CAP_PROP_FRAME_COUNT) / fps
    total_frames_previstos = int(duracao_total / intervalo_segundos)
    frame_count = 0
    frames_extraidos = 0
    
    print(f"Iniciando extração de frames de '{caminho_video}'...")
    print(f"FPS do vídeo: {fps:.2f}. Extraindo a cada {intervalo_segundos} segundos.")

    while True:
        milissegundos = frame_count * intervalo_segundos * 1000
        vidcap.set(cv2.CAP_PROP_POS_MSEC, milissegundos)
        success, image = vidcap.read()
        if not success:
            break
        nome_frame = os.path.join(pasta_saida_frames, f"frame_{frames_extraidos:06d}.png")
        try:
            cv2.imwrite(nome_frame, image)
            frames_extraidos += 1
            print(f"Frames extraídos: {frames_extraidos}/{total_frames_previstos}...", end='\r', flush=True)
        except Exception as e:
            print(f"Erro ao salvar o frame {frames_extraidos}: {e}")
        frame_count += 1
    vidcap.release()
    print(f"Extração concluída. Total de {frames_extraidos} frames salvos em '{pasta_saida_frames}'.")

if __name__ == "__main__":
    pasta_videos = "../Supernatural/SupernaturalS03"  
    
    pasta_saida_raiz = "frames" 

    intervalo_extra = 1

    if not os.path.exists(pasta_videos):
        print(f"Erro: A pasta de vídeos '{pasta_videos}' não foi encontrada.")
    else:
        print(f"Iniciando o processamento dos vídeos na pasta: '{pasta_videos}'")
        
        arquivos_video = [f for f in os.listdir(pasta_videos) if f.lower().endswith(('.mp4', '.mkv'))]

        if not arquivos_video:
            print("Nenhum arquivo de vídeo (.mp4, .mkv) encontrado na pasta. Verifique os caminhos.")
        else:
            for nome_arquivo in sorted(arquivos_video):
                caminho_completo_video = os.path.join(pasta_videos, nome_arquivo)
                
                match = re.search(r'(Supernatural.S\d{1,2})E(\d{1,2})', nome_arquivo, re.IGNORECASE)
                if match:
                    temporada = match.group(1).lower()
                    episodio = "e" + match.group(2).zfill(2) # Garante que o episódio tenha 2 dígitos (e.g. e01, e02)
                    
                    pasta_saida_episodio = os.path.join(pasta_saida_raiz, temporada, episodio)
                    
                    extrair_frames_de_video(caminho_completo_video, pasta_saida_episodio, intervalo_extra)
                    print("-" * 50) 
                else:
                    print(f"Aviso: Nome de arquivo '{nome_arquivo}' não segue o padrão 'SXXEYY'. Pulando.")