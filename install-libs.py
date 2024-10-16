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