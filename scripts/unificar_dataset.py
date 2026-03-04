import pandas as pd
import os
from tqdm import tqdm

def consolidar_datasets_eficiente(pasta_datasets, nome_arquivo_saida):
    print(f"Buscando arquivos CSV na pasta '{pasta_datasets}'...")
    
    if not os.path.isdir(pasta_datasets):
        print(f"Erro: Pasta '{pasta_datasets}' não encontrada.")
        return

    arquivos = [f for f in os.listdir(pasta_datasets) if f.endswith('.csv') and 'analise_supernatural' in f]
    arquivos.sort() 

    if not arquivos:
        print("Nenhum arquivo CSV encontrado para consolidar.")
        return

    if os.path.exists(nome_arquivo_saida):
        os.remove(nome_arquivo_saida)

    primeiro_arquivo = True
    total_linhas = 0

    print(f"Iniciando consolidação de {len(arquivos)} arquivos...")

    for nome_arquivo in tqdm(arquivos, desc="Unificando temporadas"):
        caminho_completo = os.path.join(pasta_datasets, nome_arquivo)
        
        try:
            df_temporada = pd.read_csv(caminho_completo)
            total_linhas += len(df_temporada)
            
            df_temporada.to_csv(
                nome_arquivo_saida, 
                mode='a', 
                index=False, 
                header=primeiro_arquivo
            )
            
            primeiro_arquivo = False 
            
        except Exception as e:
            print(f"\nErro ao processar {nome_arquivo}: {e}")

    print(f"\n{'='*40}")
    print(f"CONSOLIDAÇÃO CONCLUÍDA!")
    print(f"Dataset total: {total_linhas} linhas.")
    print(f"Arquivo final: {nome_arquivo_saida}")
    print(f"{'='*40}")

if __name__ == "__main__":
    pasta_com_datasets = "resultados"
    nome_do_dataset_completo = "analise_supernatural_completa2.csv"
    
    consolidar_datasets_eficiente(pasta_com_datasets, nome_do_dataset_completo)