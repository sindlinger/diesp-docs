import os
import pandas as pd
from unidecode import unidecode

def normalize_name(name):
    """Normaliza um nome para o formato desejado."""
    return ' '.join(word.capitalize() for word in unidecode(str(name)).lower().split())

def process_excel_file(file_path):
    """Processa um arquivo Excel, normalizando os nomes e gerando um relatório."""
    df = pd.read_excel(file_path)
    changes = {}
    
    for column in df.columns:
        if df[column].dtype == 'object':  # Apenas processa colunas de texto
            for idx, value in df[column].items():
                if isinstance(value, str):
                    normalized = normalize_name(value)
                    if normalized != value:
                        changes[(column, idx)] = (value, normalized)
                        df.at[idx, column] = normalized
    
    return df, changes

def generate_report(file_name, changes):
    """Gera um relatório detalhado das alterações."""
    report = f"Relatório de Normalização para {file_name}\n"
    report += "=" * 50 + "\n\n"
    
    if changes:
        report += f"Total de alterações: {len(changes)}\n\n"
        for (column, idx), (original, normalized) in changes.items():
            report += f"Coluna: {column}, Linha: {idx+2}\n"
            report += f"  Original: {original}\n"
            report += f"  Normalizado: {normalized}\n\n"
    else:
        report += "Nenhuma alteração necessária.\n"
    
    return report

def main():
    input_directory = 'excel-output'
    output_directory = 'excel-normalized'
    
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    for filename in os.listdir(input_directory):
        if filename.endswith('.xlsx'):
            input_path = os.path.join(input_directory, filename)
            output_path = os.path.join(output_directory, f"normalizado_{filename}")
            report_path = os.path.join(output_directory, f"relatorio_{filename.replace('.xlsx', '.txt')}")
            
            print(f"Processando {filename}...")
            df, changes = process_excel_file(input_path)
            
            # Salva o arquivo Excel modificado
            df.to_excel(output_path, index=False)
            print(f"Arquivo normalizado salvo: {output_path}")
            
            # Gera e salva o relatório
            report = generate_report(filename, changes)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Relatório salvo: {report_path}")
            
            print(f"Processamento de {filename} concluído.\n")

if __name__ == "__main__":
    main()