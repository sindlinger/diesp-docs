from dsnotebooks.settings import ProjectNotebookSettings
import os
import json
import pandas as pd
import deepsearch as ds
from pathlib import Path
from zipfile import ZipFile
from deepsearch.documents.core.export import export_to_markdown
from IPython.display import display, Markdown, HTML, display_html
from deepsearch_glm.utils.load_pretrained_models import load_pretrained_nlp_models
from deepsearch_glm.nlp_utils import init_nlp_model
from deepsearch_glm.glm_utils import create_glm_from_docs, expand_terms, read_nodes_in_dataframe
from deepsearch.cps.client import CPSClient

# Configurações do DeepSearch
DS_HOST = "https://deepsearch-experience.res.ibm.com/"
PROJECT_ID = "1234567890abcdefghijklmnopqrstvwyz123456"
API_KEY = "C-0p36z58BOwJatg9_oKHo28G5SvKGbG2whOFZ9wERg"

# Inicialização do cliente DeepSearch
client = CPSClient(DS_HOST, project_id=PROJECT_ID, api_key=API_KEY)

def process_document(file_path):
    output_dir = Path("./converted_docs")
    output_dir.mkdir(exist_ok=True)

    documents = ds.convert_documents(
        api=client,
        proj_key=PROJECT_ID,
        source_path=file_path,
        progress_bar=True,
    )
    documents.download_all(result_dir=output_dir)
    info = documents.generate_report(result_dir=output_dir)
    print(info)

    # Processar o arquivo JSON convertido
    for output_file in output_dir.rglob("json*.zip"):
        with ZipFile(output_file) as archive:
            json_files = [name for name in archive.namelist() if name.endswith(".json")]
            for json_file in json_files:
                doc_json = json.loads(archive.read(json_file))
                
                # Salvar o JSON
                json_path = output_dir / json_file
                with json_path.open("w") as fw:
                    json.dump(doc_json, fw, indent=2)
                
                # Converter para Markdown
                doc_md = export_to_markdown(doc_json)
                md_path = output_dir / json_file.replace(".json", ".md")
                with md_path.open("w") as fw:
                    fw.write(doc_md)
                
    return json_path  # Retorna o caminho do arquivo JSON para análise posterior

def analyze_document(json_path):
    # Carregar modelos NLP
    models = load_pretrained_nlp_models()
    nlp_model = init_nlp_model("language;term")

    # Carregar o documento JSON
    with open(json_path) as fr:
        doc = json.load(fr)

    # Analisar o documento
    res = nlp_model.apply_on_doc(doc)
    df = pd.DataFrame(res["instances"]["data"], columns=res["instances"]["headers"])
    terms = df[df["type"] == "term"][["type", "name", "subj_path"]]

    print("Termos encontrados no documento:")
    print(terms)

    # Criar GLM
    glm_dir = "./glm"
    os.makedirs(glm_dir, exist_ok=True)
    _, glm = create_glm_from_docs(glm_dir, [str(json_path)], "spm;term")

    # Analisar termos mais frequentes
    nodes = read_nodes_in_dataframe(f"{glm_dir}/nodes.csv")
    frequent_terms = nodes[nodes["name"] == "term"].sort_values("total-count", ascending=False).head(20)
    print("\nTermos mais frequentes no documento:")
    print(frequent_terms[["nodes-text", "total-count"]])

    # Expandir termos relevantes
    relevant_terms = ["processo", "administrativo", "honorários", "juízo"]
    for term in relevant_terms:
        print(f"\nExpansão do termo '{term}':")
        res = expand_terms(glm, term)
        if res["result"]:
            expanded = pd.DataFrame(res["result"][-1]["nodes"]["data"], 
                                    columns=res["result"][-1]["nodes"]["headers"])
            print(expanded[["text", "count"]].head())

    return terms, frequent_terms

def identify_relevant_pages(terms, keywords):
    relevant_pages = {}
    for keyword in keywords:
        pages = terms[terms["name"].str.contains(keyword, case=False)]["subj_path"].unique()
        relevant_pages[keyword] = [p.split('/')[-1] for p in pages]
    return relevant_pages

# Uso das funções
file_path = "./pdf/processo_completo_2024070692.pdf"  # Ajuste para o caminho do seu documento
json_path = process_document(file_path)
terms, frequent_terms = analyze_document(json_path)

keywords = ["processo administrativo", "honorários periciais", "expediente do juízo"]
relevant_pages = identify_relevant_pages(terms, keywords)

print("\nPáginas relevantes identificadas:")
for keyword, pages in relevant_pages.items():
    print(f"{keyword}: {pages}")