import cv2
import os
import shutil # Para remover diretórios e seu conteúdo

def extrair_frames_de_video(caminho_video, pasta_saida_frames, intervalo_segundos=5):
    """
    Extrai frames de um arquivo de vídeo em intervalos regulares.

    Args:
        caminho_video (str): O caminho completo para o arquivo de vídeo (ex: 'videos/supernatural_s01e01.mp4').
        pasta_saida_frames (str): O caminho da pasta onde os frames serão salvos
                                  (ex: 'frames/s01e01/').
        intervalo_segundos (int): O intervalo em segundos para extrair cada frame.
                                  (Ex: 1 para cada segundo, 5 para cada 5 segundos).
    """

    if not os.path.exists(caminho_video):
        print(f"Erro: O arquivo de vídeo não foi encontrado em '{caminho_video}'")
        return

    # Certifica-se de que a pasta de saída existe. Se já existir, remove e cria novamente.
    if os.path.exists(pasta_saida_frames):
        print(f"A pasta de saída '{pasta_saida_frames}' já existe. Removendo conteúdo antigo...")
        shutil.rmtree(pasta_saida_frames)
    os.makedirs(pasta_saida_frames)
    print(f"Pasta de saída '{pasta_saida_frames}' criada/limpa com sucesso.")

    vidcap = cv2.VideoCapture(caminho_video)

    # Verifica se o vídeo foi aberto corretamente
    if not vidcap.isOpened():
        print(f"Erro: Não foi possível abrir o vídeo '{caminho_video}'. Verifique o caminho ou o formato.")
        return

    fps = vidcap.get(cv2.CAP_PROP_FPS)  # Frames por segundo do vídeo
    if fps == 0:
        print("Erro: Não foi possível obter o FPS do vídeo. Possível corrupção ou formato inválido.")
        vidcap.release()
        return

    frame_count = 0
    frames_extraidos = 0
    
    print(f"Iniciando extração de frames de '{caminho_video}'...")
    print(f"FPS do vídeo: {fps:.2f}. Extraindo a cada {intervalo_segundos} segundos.")

    while True:
        # Define a posição no vídeo em milissegundos
        # A cada 'intervalo_segundos', pulamos para a próxima posição.
        milissegundos = frame_count * intervalo_segundos * 1000
        vidcap.set(cv2.CAP_PROP_POS_MSEC, milissegundos)

        success, image = vidcap.read()

        if not success:
            # Significa que chegamos ao final do vídeo
            break

        nome_frame = os.path.join(pasta_saida_frames, f"frame_{frames_extraidos:06d}.png")
        
        try:
            cv2.imwrite(nome_frame, image)
            frames_extraidos += 1
        except Exception as e:
            print(f"Erro ao salvar o frame {frames_extraidos}: {e}")
            
        frame_count += 1 # Conta os intervalos tentados, não os frames salvos.

    vidcap.release()
    print(f"Extração concluída. Total de {frames_extraidos} frames salvos em '{pasta_saida_frames}'.")

# --- COMO USAR O SCRIPT ---
if __name__ == "__main__":
    # Exemplo de uso:
    # 1. Defina o caminho para o seu arquivo de vídeo
    video_exemplo = "S01E01.mkv"
    # 2. Defina o caminho para a pasta onde os frames serão salvos
    # Cuidado: O conteúdo desta pasta será limpo a cada execução!
    pasta_saida_exemplo = "frames/teste"
    
    # 3. Defina o intervalo de extração em segundos (ex: 1 segundo, 5 segundos)
    intervalo_extra = 5 

    # --- ATENÇÃO ---
    # Altere os caminhos e o intervalo abaixo para testar!
    # Certifique-se de que o vídeo 'supernatural_s01e01.mp4' exista no caminho especificado.
    # Exemplo:
    # video_exemplo = "C:/Users/SeuUsuario/Videos/Supernatural/Temporada01/Supernatural.S01E01.Pilot.mp4"
    # pasta_saida_exemplo = "C:/Users/SeuUsuario/Documentos/TCC_Frames/S01E01_Frames/"
    
    extrair_frames_de_video(video_exemplo, pasta_saida_exemplo, intervalo_extra)