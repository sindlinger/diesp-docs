import pandas as pd
import re
import os

def replace_capital_with_joao_pessoa(input_file, output_file):
    """
    Lê um arquivo Excel, substitui 'da Capital' por 'de João Pessoa' na coluna 'JUÍZO (VARA)',
    e salva o resultado em um novo arquivo Excel.
    """
    # Lê o arquivo Excel
    df = pd.read_excel(input_file)
    
    # Verifica se a coluna 'JUÍZO (VARA)' existe
    if 'JUÍZO (VARA)' not in df.columns:
        raise ValueError("A coluna 'JUÍZO (VARA)' não foi encontrada no arquivo.")
    
    # Função para substituir 'da Capital' por 'de João Pessoa' em cada entrada
    def replace_entry(entry):
        if pd.isna(entry):  # Verifica se o valor é NaN
            return entry
        try:
            # Converte para string se não for
            entry = str(entry)
            # Substitui 'da Capital' por 'de João Pessoa'
            replaced = re.sub(r'\bda Capital\b', 'de João Pessoa', entry)
            # Remove espaços duplos que podem ter sido criados
            replaced = re.sub(r'\s+', ' ', replaced).strip()
            return replaced
        except Exception as e:
            print(f"Erro ao processar entrada '{entry}': {str(e)}")
            return entry  # Retorna o valor original se houver erro
    
    # Aplica a substituição à coluna 'JUÍZO (VARA)'
    df['JUÍZO (VARA)'] = df['JUÍZO (VARA)'].apply(replace_entry)
    
    # Salva o DataFrame modificado em um novo arquivo Excel
    df.to_excel(output_file, index=False)
    
    return len(df)

def main():
    input_directory = 'excel-output'
    output_directory = 'excel-normalized-joao-pessoa'
    
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    for filename in os.listdir(input_directory):
        if filename.endswith('.xlsx'):
            input_path = os.path.join(input_directory, filename)
            output_path = os.path.join(output_directory, f"substituido_{filename}")
            
            print(f"Processando {filename}...")
            try:
                rows_processed = replace_capital_with_joao_pessoa(input_path, output_path)
                print(f"Arquivo processado com sucesso. Linhas processadas: {rows_processed}")
                print(f"Arquivo modificado salvo em: {output_path}")
            except Exception as e:
                print(f"Erro ao processar {filename}: {str(e)}")
            
            print("-----------------------------")

if __name__ == "__main__":
    main()