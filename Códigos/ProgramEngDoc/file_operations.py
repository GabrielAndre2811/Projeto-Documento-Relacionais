import json
import os
import shutil
from fuzzywuzzy import process, fuzz
from fpdf import FPDF

def carregar_configuracoes(caminho_config):
    """Carrega as configurações do arquivo JSON e garante que os tipos estejam corretos."""
    with open(caminho_config, 'r', encoding='utf-8') as file:
        config = json.load(file)

    acuracia = int(config.get("acuracia", 80))  # Valor padrão de 80 se não definido
    config["acuracia"] = acuracia
    return config

def listar_arquivos(diretorio):
    """Lista todos os arquivos em um diretório especificado."""
    return [os.path.join(diretorio, arq) for arq in os.listdir(diretorio) if os.path.isfile(os.path.join(diretorio, arq))]

def filtrar_por_palavras_chave(arquivos, palavras_chave):
    """Filtra arquivos por palavras-chave e retorna arquivos filtrados e palavras-chave correspondentes."""
    arquivos_filtrados = {k: [] for k in palavras_chave}
    palavras_correspondentes = set()
    
    for arquivo in arquivos:
        arquivo_lower = os.path.basename(arquivo).lower()
        for palavra_chave, palavras in palavras_chave.items():
            if any(palavra.lower() in arquivo_lower for palavra in palavras):
                arquivos_filtrados[palavra_chave].append(arquivo)
                palavras_correspondentes.add(palavra_chave)
                break

    return arquivos_filtrados, palavras_correspondentes

def criar_pdf_em_branco(caminho):
    """Cria um arquivo PDF em branco no caminho especificado.""" 
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Arquivo em branco", ln=True, align='C')
    pdf.output(caminho)

def criar_arquivos_em_branco(diretorio, palavras_chave, palavras_correspondentes):
    """Cria arquivos em branco para palavras-chave não encontradas e registra em um arquivo de texto.""" 
    arquivos_em_branco = []
    lista_faltantes_path = os.path.join(diretorio, "lista_de_documentos_faltantes.txt")

    with open(lista_faltantes_path, 'w') as lista_faltantes:
        for palavra in palavras_chave:
            if palavra not in palavras_correspondentes:
                caminho = os.path.join(diretorio, f"{palavra}_vazio.pdf")
                if not os.path.exists(caminho):
                    try:
                        criar_pdf_em_branco(caminho)
                        arquivos_em_branco.append(caminho)
                        lista_faltantes.write(f"{palavra}_vazio.pdf\n")
                        print(f'Arquivo criado: {caminho}')
                    except Exception as e:
                        print(f"Erro ao criar PDF em branco: {e}")

    print(f"Arquivo de lista de documentos faltantes criado: {lista_faltantes_path}")
    return arquivos_em_branco

def criar_mapeamento(diretorio, arquivos_filtrados, novos_nomes, acuracia):
    """Cria um mapeamento de arquivos filtrados para novos nomes usando correspondência exata e fuzzy.""" 
    mapeamento = {}
    novos_nomes_dict = {os.path.basename(nome).lower(): nome for nome in novos_nomes}
    usados = set()
    mapeados = set()

    for palavra_chave, arquivos in arquivos_filtrados.items():
        if not arquivos:
            continue

        for arquivo in arquivos:
            nome_arquivo = os.path.basename(arquivo).lower()
            if nome_arquivo in mapeados:
                continue

            if nome_arquivo in novos_nomes_dict:
                caminho_novo = novos_nomes_dict[nome_arquivo]
                if caminho_novo not in usados:
                    caminho_novo_completo = os.path.join(diretorio, caminho_novo)
                    if not os.path.exists(caminho_novo_completo):
                        mapeamento[arquivo] = caminho_novo_completo
                        usados.add(caminho_novo)
                        mapeados.add(nome_arquivo)
                        print(f"Correspondência exata encontrada para '{nome_arquivo}': {caminho_novo_completo}")
                        continue

            correspondencias_usadas = set()
            correspondencias = process.extract(nome_arquivo, list(novos_nomes_dict.keys()), scorer=fuzz.partial_ratio)
            correspondencias = sorted(correspondencias, key=lambda x: x[1], reverse=True)
            print(f"Palavra-chave '{palavra_chave}': Arquivo '{nome_arquivo}', Correspondências fuzzy: {correspondencias}")

            for melhor_correspondencia, score in correspondencias:
                if score >= acuracia:
                    caminho_novo = novos_nomes_dict.get(melhor_correspondencia)
                    if caminho_novo and caminho_novo not in usados and caminho_novo not in correspondencias_usadas:
                        caminho_novo_completo = os.path.join(diretorio, caminho_novo)
                        if not os.path.exists(caminho_novo_completo):
                            mapeamento[arquivo] = caminho_novo_completo
                            usados.add(caminho_novo)
                            correspondencias_usadas.add(caminho_novo)
                            mapeados.add(nome_arquivo)
                            print(f"Correspondência fuzzy encontrada para '{nome_arquivo}': {caminho_novo_completo}")
                            break
                else:
                    print(f"Baixo score de correspondência para '{nome_arquivo}': {score}")

    return mapeamento

def renomear_arquivos(diretorio, mapeamento_nomes):
    """Renomeia arquivos com base no mapeamento fornecido.""" 
    arquivos_renomeados = []
    for caminho_antigo, caminho_novo in mapeamento_nomes.items():
        caminho_antigo_completo = os.path.join(diretorio, caminho_antigo)
        if os.path.exists(caminho_antigo_completo):
            if os.path.exists(caminho_novo):
                print(f'Arquivo já existe: {caminho_novo}. Não será renomeado.')
            else:
                try:
                    os.rename(caminho_antigo_completo, caminho_novo)
                    arquivos_renomeados.append(caminho_novo)
                    print(f'Renomeado: {caminho_antigo_completo} -> {caminho_novo}')
                except Exception as e:
                    print(f"Erro ao renomear o arquivo {caminho_antigo_completo}: {e}")
        else:
            print(f'Arquivo não encontrado: {caminho_antigo_completo}')
    return arquivos_renomeados

def copiar_arquivos_para_destino(arquivos, destino):
    """Copia arquivos renomeados para o diretório de destino.""" 
    if not os.path.exists(destino):
        os.makedirs(destino)  # Cria o diretório de destino se não existir
    for arquivo in arquivos:
        nome_arquivo = os.path.basename(arquivo)
        caminho_destino = os.path.join(destino, nome_arquivo)
        try:
            shutil.copy2(arquivo, caminho_destino)
            print(f'Arquivo copiado para o destino: {caminho_destino}')
        except Exception as e:
            print(f"Erro ao copiar o arquivo {arquivo} para o destino: {e}")

def processar_documentos(diretorio_origem, diretorio_destino):
    """Coordena o processamento de documentos incluindo listagem, filtragem, criação de arquivos em branco, mapeamento, renomeação e cópia.""" 
    # Caminho do arquivo de configuração
    caminho_config = os.path.join(os.path.dirname(__file__), 'config.json')

    # Carregar as configurações do arquivo JSON
    config = carregar_configuracoes(caminho_config)
    palavras_chave = config.get("palavras_chave", {})
    novos_nomes = config.get("novos_nomes", [])
    acuracia = config.get("acuracia", 80)  # Valor padrão de 80 se não definido

    print(f"Acurácia carregada: {acuracia}")  # Verifique se o valor da acurácia está correto

    # Passo 1: Liste todos os arquivos no diretório de origem
    arquivos = listar_arquivos(diretorio_origem)

    # Passo 2: Filtre arquivos existentes por palavras-chave e registre palavras-chave com correspondências
    arquivos_filtrados, palavras_correspondentes = filtrar_por_palavras_chave(arquivos, palavras_chave)

    print("Arquivos filtrados por palavras-chave:")
    for palavra, arquivos in arquivos_filtrados.items():
        print(f"Palavra-chave '{palavra}': {arquivos}")

    # Passo 3: Crie arquivos em branco necessários e registre no arquivo de texto
    criar_arquivos_em_branco(diretorio_origem, palavras_chave, palavras_correspondentes)

    # Passo 4: Refiltre arquivos após a criação dos arquivos em branco
    arquivos = listar_arquivos(diretorio_origem)
    arquivos_filtrados, palavras_correspondentes = filtrar_por_palavras_chave(arquivos, palavras_chave)

    # Passo 5: Recrie o mapeamento de nomes antigos para novos nomes
    mapeamento_nomes = criar_mapeamento(diretorio_origem, arquivos_filtrados, novos_nomes, acuracia)

    # Exibe o mapeamento para verificação
    print("Mapeamento para renomeação:")
    for nome_antigo, nome_novo in mapeamento_nomes.items():
        print(f"{nome_antigo} -> {nome_novo}")

    # Passo 6: Renomeie os arquivos de acordo com o mapeamento
    arquivos_renomeados = renomear_arquivos(diretorio_origem, mapeamento_nomes)

    # Passo 7: Copie os arquivos renomeados para o diretório de destino
    copiar_arquivos_para_destino(arquivos_renomeados, diretorio_destino)
