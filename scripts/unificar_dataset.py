import pandas as pd
import os

def consolidar_datasets(pasta_datasets, nome_arquivo_saida):
    lista_de_dfs = []
    
    print(f"Buscando arquivos CSV na pasta '{pasta_datasets}'...")
    
    if not os.path.isdir(pasta_datasets):
        print(f"Erro: Pasta '{pasta_datasets}' não encontrada.")
        return

    for nome_arquivo in os.listdir(pasta_datasets):
        if nome_arquivo.endswith('.csv') and 'analise_supernatural' in nome_arquivo:
            caminho_completo = os.path.join(pasta_datasets, nome_arquivo)
            print(f"  - Lendo arquivo: {nome_arquivo}")
            try:
                df_temporada = pd.read_csv(caminho_completo)
                lista_de_dfs.append(df_temporada)
            except Exception as e:
                print(f"Aviso: Não foi possível ler o arquivo '{nome_arquivo}'. Erro: {e}")

    if not lista_de_dfs:
        print("Nenhum arquivo CSV encontrado para consolidar. Verifique a pasta e os nomes dos arquivos.")
        return

    df_consolidado = pd.concat(lista_de_dfs, ignore_index=True)
    
    df_consolidado.to_csv(nome_arquivo_saida, index=False)
    
    print("\nProcesso de consolidação concluído!")
    print(f"Total de linhas no dataset completo: {len(df_consolidado)}")
    print(f"Dataset consolidado salvo como '{nome_arquivo_saida}'.")

if __name__ == "__main__":
    pasta_com_datasets = "resultados"
    
    nome_do_dataset_completo = "analise_supernatural_completa.csv"
    
    consolidar_datasets(pasta_com_datasets, nome_do_dataset_completo)