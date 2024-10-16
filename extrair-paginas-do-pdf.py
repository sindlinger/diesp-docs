import os
import re
import sys
import subprocess
import argparse
import tempfile
from PyPDF2 import PdfReader, PdfWriter
import pytesseract
from pdf2image import convert_from_path

# Defina os diretórios padrão aqui
DEFAULT_INPUT_DIR = "./pdfs"
DEFAULT_OUTPUT_DIR = "./pdfs-output"
DEFAULT_THRESHOLD = 0.7  # Limiar padrão de probabilidade


def install_tesseract():
    print("Tesseract não encontrado. Tentando instalar...")
    if sys.platform.startswith('linux'):
        try:
            subprocess.check_call(['sudo', 'apt-get', 'update'])
            subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'tesseract-ocr'])
            print("Tesseract instalado com sucesso.")
        except subprocess.CalledProcessError:
            print("Falha ao instalar o Tesseract. Por favor, instale manualmente.")
            sys.exit(1)
    elif sys.platform == 'darwin':
        try:
            subprocess.check_call(['brew', 'install', 'tesseract'])
            print("Tesseract instalado com sucesso.")
        except subprocess.CalledProcessError:
            print("Falha ao instalar o Tesseract. Por favor, instale manualmente.")
            sys.exit(1)
    else:
        print("Sistema operacional não suportado para instalação automática do Tesseract.")
        print("Por favor, instale o Tesseract manualmente e adicione-o ao PATH do sistema.")
        sys.exit(1)

def check_tesseract():
    try:
        pytesseract.get_tesseract_version()
    except pytesseract.TesseractNotFoundError:
        install_tesseract()

def install_poppler():
    print("Poppler não encontrado. Tentando instalar...")
    if sys.platform.startswith('linux'):
        try:
            subprocess.check_call(['sudo', 'apt-get', 'update'])
            subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'poppler-utils'])
            print("Poppler instalado com sucesso.")
        except subprocess.CalledProcessError:
            print("Falha ao instalar o Poppler. Por favor, instale manualmente.")
            sys.exit(1)
    elif sys.platform == 'darwin':
        try:
            subprocess.check_call(['brew', 'install', 'poppler'])
            print("Poppler instalado com sucesso.")
        except subprocess.CalledProcessError:
            print("Falha ao instalar o Poppler. Por favor, instale manualmente.")
            sys.exit(1)
    else:
        print("Sistema operacional não suportado para instalação automática do Poppler.")
        print("Por favor, instale o Poppler manualmente e adicione-o ao PATH do sistema.")
        sys.exit(1)

def check_poppler():
    try:
        subprocess.check_call(['pdfinfo', '-v'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        install_poppler()

check_poppler()
check_tesseract()
import os
import re
import sys
import argparse
import io
from PyPDF2 import PdfReader, PdfWriter
import pytesseract
from pdf2image import convert_from_bytes

# Defina os diretórios padrão aqui
DEFAULT_INPUT_DIR = "./pdfs"
DEFAULT_OUTPUT_DIR = "./pdfs-output"
DEFAULT_THRESHOLD = 0.7  # Limiar padrão de probabilidade

def extract_text_from_page(page):
    # Converte o objeto PageObject em bytes
    pdf_writer = PdfWriter()
    pdf_writer.add_page(page)
    pdf_bytes = io.BytesIO()
    pdf_writer.write(pdf_bytes)
    pdf_bytes.seek(0)

    # Converte os bytes do PDF em imagens
    images = convert_from_bytes(pdf_bytes.getvalue())
    
    # Extrai texto das imagens usando OCR
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img)
    
    return text

def calculate_probability(text, case_patterns):
    scores = [0, 0, 0]
    for case_index, patterns in enumerate(case_patterns):
        last_match_index = -1
        consecutive_matches = 0
        for i, (pattern, weight) in enumerate(patterns):
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                if i > last_match_index + 1:
                    # Desconta pontuação se a ordem não for seguida
                    scores[case_index] -= 0.1 * weight
                else:
                    consecutive_matches += 1
                
                # Aumenta o peso baseado no número de matches consecutivos
                adjusted_weight = weight * (1 + 0.1 * consecutive_matches)
                scores[case_index] += adjusted_weight
                
                last_match_index = i
            else:
                consecutive_matches = 0
    
    total_score = sum(scores)
    if total_score == 0:
        return [0, 0, 0]
    
    # Normaliza as probabilidades
    max_score = max(scores)
    probabilities = [score / max_score for score in scores]
    return probabilities

def is_matching_page(text, page_number, threshold):
    case_patterns = [
        # Case 1 patterns
        [
            (r"PROCESSO ADMINISTRATIVO PROCESSO nº \d{10} \(PA-TJ\)", 0.3),
            (r"Assunto: HONORÁRIOS PERICIAIS - EXPEDIENTE DO JUÍZO", 0.2),
            (r"Data da Autuação:", 0.1),
            (r"Parte:", 0.1),
            (r"Interessado:", 0.1),
            (r"Área:", 0.05),
            (r"Comarca:", 0.05),
            (r"Vara:", 0.05),
            (r"Processo Judicial de Origem:", 0.05)
        ],
        # Case 2 patterns
        [
            (r"Poder Judiciário do Estado da Paraíba", 0.15),
            (r"Diretoria Especial", 0.15),
            (r"Processo nº", 0.1),
            (r"Requerente:", 0.1),
            (r"Interessado:", 0.1),
            (r"requisição de pagamento de honorários, no valor de", 0.15),
            (r"A Resolução 09/2017, deste Tribunal,", 0.1),
            (r"À Gerência de Programação Orçamentária deste Tribunal", 0.1),
            (r"CASO HAJA DOTAÇÃO ORÇAMENTÁRIA PARA O CORRENTE EXERCÍCIO", 0.05)
        ],
        # Case 3 patterns
        [
            (r"ESTADO DA PARAÍBA PODER JUDICIÁRIO TRIBUNAL DE JUSTIÇA", 0.15),
            (r"Assessoria do Conselho da Magistratura", 0.15),
            (r"PROCESSO ADMINISTRATIVO", 0.1),
            (r"Requerente:", 0.1),
            (r"Assunto:", 0.1),
            (r"Certidão", 0.1),
            (r"Certifico, para fins e efeitos legais,", 0.1),
            (r"que os integrantes do Egrégio Conselho da Magistratura,", 0.05),
            (r"em sessão ordinária, hoje realizada,", 0.05),
            (r"apreciando o processo acima identificado,", 0.05),
            (r"proferiram a seguinte decisão:", 0.05)
        ]
    ]
    
    probabilities = calculate_probability(text, case_patterns)
    
    if page_number == 0 and probabilities[0] >= threshold:
        return 1, probabilities[0]
    elif probabilities[1] >= threshold:
        return 2, probabilities[1]
    elif probabilities[2] >= threshold:
        return 3, probabilities[2]
    else:
        return 0, max(probabilities)

def process_pdf(input_path, output_path, threshold):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    case_found = {1: False, 2: False, 3: False}
    probabilities = {1: 0, 2: 0, 3: 0}
    
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text = extract_text_from_page(page)
        
        case, probability = is_matching_page(text, page_num, threshold)
        if case > 0:
            writer.add_page(page)
            case_found[case] = True
            probabilities[case] = max(probabilities[case], probability)
    
    if any(case_found.values()):
        try:
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            print(f"Páginas extraídas salvas em {output_path}")
            for case, found in case_found.items():
                if found:
                    print(f"Caso {case} encontrado com probabilidade: {probabilities[case]:.2f}")
        except PermissionError:
            print(f"Erro de permissão ao salvar em {output_path}. Verifique as permissões do diretório.")
    else:
        print(f"Nenhuma página correspondente encontrada em {input_path}")

def main():
    parser = argparse.ArgumentParser(description="Extrai páginas específicas de PDFs.")
    parser.add_argument("-i", "--input", help="Diretório de entrada contendo os PDFs")
    parser.add_argument("-o", "--output", help="Diretório de saída para os PDFs extraídos")
    parser.add_argument("-t", "--threshold", type=float, default=DEFAULT_THRESHOLD,
                        help="Limiar de probabilidade para considerar uma correspondência (0.0 a 1.0)")
    args = parser.parse_args()

    input_directory = args.input if args.input else DEFAULT_INPUT_DIR
    output_directory = args.output if args.output else DEFAULT_OUTPUT_DIR
    threshold = args.threshold

    print(f"Diretório de entrada: {input_directory}")
    print(f"Diretório de saída: {output_directory}")
    print(f"Limiar de probabilidade: {threshold}")

    if not os.path.exists(input_directory):
        print(f"Erro: O diretório de entrada '{input_directory}' não existe.")
        sys.exit(1)

    if not os.path.exists(output_directory):
        print(f"Criando diretório de saída '{output_directory}'...")
        os.makedirs(output_directory)

    for filename in os.listdir(input_directory):
        if filename.endswith(".pdf"):
            input_path = os.path.join(input_directory, filename)
            output_filename = os.path.splitext(filename)[0] + "-extracted.pdf"
            output_path = os.path.join(output_directory, output_filename)
            
            print(f"Processando {filename}...")
            process_pdf(input_path, output_path, threshold)

if __name__ == "__main__":
    main()