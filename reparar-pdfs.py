import os
import pikepdf

# Defina o diretório onde os arquivos PDF estão localizados
directory = './pdfs'



# Percorre todos os arquivos no diretório
for filename in os.listdir(directory):
    if filename.endswith(".pdf"):
        try:
            # Tenta abrir o arquivo PDF
            with pikepdf.open(os.path.join(directory, filename)) as pdf:
                # Salva uma nova versão do PDF
                pdf.save(os.path.join(directory, "reparado_" + filename))
            print(f"{filename} reparado com sucesso")
        except pikepdf.PdfError:
            # Caso não consiga abrir, é provável que o PDF esteja corrompido
            print(f"Erro ao abrir {filename}, pode estar corrompido")
