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
DEFAULT_THRESHOLD = 0.2  # Limiar padrão de probabilidade

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

def is_matching_page(text, page_number):
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
    
    return calculate_probability(text, case_patterns)

def generate_report(filename, page_probabilities, threshold):
    report = f"\nRelatório para {filename}:\n"
    report += "-" * 40 + "\n"
    
    for page_num, probs in enumerate(page_probabilities):
        report += f"Página {page_num + 1}:\n"
        for case, prob in enumerate(probs, start=1):
            percentage = prob * 100
            status = "Detectado" if prob >= threshold else "Não detectado"
            report += f"  Caso {case}: {percentage:.2f}% ({status})\n"
        report += "\n"
    
    report += "-" * 40 + "\n"
    return report

def process_pdf(input_path, output_path, threshold):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    page_probabilities = []
    pages_extracted = 0
    
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text = extract_text_from_page(page)
        
        probabilities = is_matching_page(text, page_num)
        page_probabilities.append(probabilities)
        
        if any(prob >= threshold for prob in probabilities):
            writer.add_page(page)
            pages_extracted += 1
    
    if pages_extracted > 0:
        try:
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            print(f"Páginas extraídas salvas em {output_path}")
        except PermissionError:
            print(f"Erro de permissão ao salvar em {output_path}. Verifique as permissões do diretório.")
    else:
        print(f"Nenhuma página correspondente encontrada em {input_path}")
    
    return page_probabilities, pages_extracted

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

    total_files = 0
    files_with_extractions = 0
    total_pages_extracted = 0

    for filename in os.listdir(input_directory):
        if filename.endswith(".pdf"):
            total_files += 1
            input_path = os.path.join(input_directory, filename)
            output_filename = os.path.splitext(filename)[0] + "-extracted.pdf"
            output_path = os.path.join(output_directory, output_filename)
            
            print(f"Processando {filename}...")
            page_probabilities, pages_extracted = process_pdf(input_path, output_path, threshold)
            
            report = generate_report(filename, page_probabilities, threshold)
            print(report)
            
            if pages_extracted > 0:
                files_with_extractions += 1
                total_pages_extracted += pages_extracted

    print("\nResumo do processamento:")
    print(f"Total de arquivos processados: {total_files}")
    print(f"Arquivos com páginas extraídas: {files_with_extractions}")
    print(f"Total de páginas extraídas: {total_pages_extracted}")

if __name__ == "__main__":
    main()