import os
import subprocess

def reparar_pdf_ghostscript(input_pdf, output_pdf):
    try:
        # Chama o Ghostscript para reprocessar o PDF
        gs_command = [
            'gs', '-o', output_pdf,
            '-sDEVICE=pdfwrite',
            '-dPDFSETTINGS=/prepress',  # Alta qualidade
            input_pdf
        ]
        subprocess.run(gs_command, check=True)
        print(f"{input_pdf} reparado com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao tentar reparar {input_pdf}: {e}")

# Diretório com os arquivos corrompidos
directory = './pdfs'
for filename in os.listdir(directory):
    if filename.endswith(".pdf"):
        input_file = os.path.join(directory, filename)
        output_file = os.path.join(directory, "reparado_" + filename)
        reparar_pdf_ghostscript(input_file, output_file)
