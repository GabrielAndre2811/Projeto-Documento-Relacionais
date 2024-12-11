# mesc.py

import fitz  # PyMuPDF
from PyPDF2 import PdfMerger
from PIL import Image, ImageTk
from PIL import Image, ImageDraw


def mesclar_pdfs(pdf_list, caminho_destino):
    try:
        merger = PdfMerger()
        for pdf in pdf_list:
            merger.append(pdf)
        merger.write(caminho_destino)
        merger.close()
        print(f"PDFs mesclados com sucesso em {caminho_destino}")
    except Exception as e:
        print(f"Erro ao mesclar PDFs: {e}")
        raise

from PIL import Image, ImageTk
import fitz  # PyMuPDF

def gerar_imagem_thumbnail(pdf_path, tamanho=(300, 400)):
    try:
        # Abrir o arquivo PDF
        pdf_document = fitz.open(pdf_path)
        # Obter a primeira página
        primeira_pagina = pdf_document.load_page(0)
        # Converter a página em uma imagem pixmap
        imagem_pixmap = primeira_pagina.get_pixmap()
        # Criar um objeto PIL Image a partir do pixmap
        imagem_pil = Image.frombytes("RGB", [imagem_pixmap.width, imagem_pixmap.height], imagem_pixmap.samples)
        # Redimensionar a imagem
        imagem_pil.thumbnail(tamanho)
        # Fechar o documento PDF
        pdf_document.close()
        return imagem_pil
    except Exception as e:
        print(f"Erro ao gerar thumbnail: {e}")
        return None