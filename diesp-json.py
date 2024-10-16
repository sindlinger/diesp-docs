import os
import json
import pandas as pd

def process_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    rows = []
    for page in data:
        for item in page['items']:
            if item['type'] == 'table':
                for row in item['rows'][1:]:  # Skip the header row
                    rows.append(row)
    
    df = pd.DataFrame(rows, columns=[
        "PROCESSO ADMIN. Nº",
        "DATA DA AUTUCAO",
        "PARTE INTERESSADA",
        "JUÍZO (VARA)",
        "COMARCA",
        "PROCESSO Nº",
        "PROMOVENTE",
        "PROMOVIDO"
    ])
    
    return df

def main():
    input_directory = 'json-input'
    output_directory = 'excel-output'
    
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    for filename in os.listdir(input_directory):
        if filename.endswith('.json'):
            input_path = os.path.join(input_directory, filename)
            output_path = os.path.join(output_directory, f"{os.path.splitext(filename)[0]}.xlsx")
            
            df = process_json_file(input_path)
            df.to_excel(output_path, index=False)
            print(f"Arquivo Excel criado: {output_path}")

if __name__ == "__main__":
    main()