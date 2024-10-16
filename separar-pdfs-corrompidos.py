import os
import shutil
import pikepdf

# Diretório onde os PDFs estão localizados
directory = "./pdfs"
# Diretório para onde os PDFs corrompidos serão movidos
corrupted_directory = "./pdfs_corrompidos"

# Cria o diretório para arquivos corrompidos, se não existir
os.makedirs(corrupted_directory, exist_ok=True)

# Percorre todos os arquivos no diretório
for filename in os.listdir(directory):
    if filename.endswith(".pdf"):
        try:
            # Tenta abrir o arquivo PDF
            with pikepdf.open(os.path.join(directory, filename)) as pdf:
                print(f"{filename} está OK")
        except pikepdf.PdfError:
            # Caso não consiga abrir, é provável que o PDF esteja corrompido
            print(f"Erro ao abrir {filename}, pode estar corrompido")
            # Move o arquivo corrompido para o diretório de corrompidos
            shutil.move(os.path.join(directory, filename), os.path.join(corrupted_directory, filename))
            print(f"{filename} movido para {corrupted_directory}")