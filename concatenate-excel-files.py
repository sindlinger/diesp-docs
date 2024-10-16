import os
import pandas as pd
import glob

def combine_excel_files(input_directory, output_file):
    """Combina todos os arquivos Excel em um diretório em um único arquivo."""
    
    # Lista todos os arquivos Excel no diretório
    all_files = glob.glob(os.path.join(input_directory, "*.xlsx"))
    
    # Lista para armazenar os DataFrames
    df_list = []
    
    # Lê cada arquivo Excel e adiciona à lista
    for file in all_files:
        df = pd.read_excel(file)
        
        # Adiciona uma coluna com o nome do arquivo original
        df['Arquivo_Fonte'] = os.path.basename(file)
        
        df_list.append(df)
    
    # Combina todos os DataFrames
    combined_df = pd.concat(df_list, ignore_index=True)
    
    # Salva o DataFrame combinado em um novo arquivo Excel
    combined_df.to_excel(output_file, index=False)
    
    return len(all_files), len(combined_df)

def main():
    input_directory = './excel-normalized'
    output_file = './unique-excel-file/combinado.xlsx'
    
    print("Iniciando a combinação de arquivos Excel...")
    
    try:
        num_files, num_rows = combine_excel_files(input_directory, output_file)
        
        print(f"\nCombinação concluída com sucesso!")
        print(f"Número de arquivos combinados: {num_files}")
        print(f"Número total de linhas no arquivo combinado: {num_rows}")
        print(f"Arquivo combinado salvo em: {output_file}")
        
    except Exception as e:
        print(f"\nOcorreu um erro durante a combinação dos arquivos:")
        print(str(e))

if __name__ == "__main__":
    main()