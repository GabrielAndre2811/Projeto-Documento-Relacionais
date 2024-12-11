# config.py
import json
import os
import sys
import shutil
import os


def obter_palavras_chave():
    return {
    'capa': ['capa', 'capafatura', 'capa fatura'],
    'check': ['check'],
    'nf': ['nota fiscal', 'notafiscal', 'nf'],
    'descriminativa': ['descriminativa','discriminativa','fatura discriminativa'],
    'empenho': ['empenho', 'nota empenho'],
    'certificação': ['certificação', 'certificação de serviços', 'cert'],
    'contrato': ['contrato', 'contratos'],
    'ordem': ['ordem', 'ordem de serviço', 'ordem de serviços'],
    'nomeação' : ['nomeação', 'portaria de nomeação'],
    'apostilhamento' : ['apostilhamento', 'termo'],
    'cronograma' : ['cronograma', 'cronograma vigente'],
    'rvo' : ['RVO', 'relatório de visita', 'visita', 'obra'],
    'justificativa' : ['justificativa', 'justificativa contratada', 'da contratada'],
    'folha resumo mediação' : ['resumo', 'resumo mediação', 'folha resumo'],
    'planilha' : ['planilha', 'planilhas', 'planilha de mediação', 'planilhas de mediação'],
    'diário' : ['diário', 'diario', 'diário de obra', 'diario de obra'],
    'relação' : ['relação', 'relação de funcionários', 'relacao de funcionarios', 'relação de trabalhadores', 'relacao de trabalhadores', 'empregados', 'relação de empregados', 'colaboradores', 'relacao de empregados'],
    'comprovante' : ['comprovante', 'comprovantes', 'comprovante pagamento', 'pagamento', 'pgt', 'comprovante pgt', 'recibos', 'recibo'],
    'dctfweb' : ['dctfweb', 'declaracao', 'declaração', 'declaracao completa', 'declaração completa', 'declaraçaocompleta'],
    'fgts' : ['fgts', 'guia recolhimento', 'guia fgts', 'cnd fgts'],
    'inss' : ['inss', 'guia inss', 'guia recolhimento inss'],
    'cndtrabalhista' : ['cnd trabalhista', 'cndtrabalhista'],
    'federais' : ['federais', 'cnd federais'],
    'estaduais' : ['estaduais', 'cnd estaduais'],
    'municipais' : ['municipais', 'cnd municipais', 'cnd municipal', 'cnd municipio']
    }

def obter_novos_nomes():
    return [
    '1.1 - Capa Fatura.pdf',
    '2.1 - Nota Fiscal.pdf',
    '2.2 - Fatura Discriminativa.pdf',
    '2.3 - Nota Empenho.pdf',
    '2.4 - Certificação de Serviços.pdf',
    '3.1 - Contrato.pdf',
    '3.2 - Ordem de Serviço.pdf',
    '3.3 - Portaria de Nomeação do Fiscal e Gestor do Contr.pdf',
    '3.4 - Termo Aditivo Apostilamento.pdf',
    '4.1 - Cronograma Contratado Vigente.pdf',
    '5.1 - RVO - Relatório Visita de Obra.pdf',
    '5.2 - Justificativa da Contratada.pdf',
    '6.1 - Folha Resumo da Mediação.pdf',
    '6.2 - Planilhas de Mediação - Parcela e Acumulado.pdf',
    '7.1 - Livro Diário de Obra do Periodo.pdf',
    '8.1 - Relação dos Trabalhadores do Mês da Mediação.pdf',
    '8.2 - Comprovantes de Pagamento do Pessoal.pdf',
    '9.1 - DCTFWeb (GFIP-SFIP).pdf',
    '10.1 - Guia de Recolhimento do FGTS.pdf',
    '10.2 - Guia de Recolhimento do INSS - GPS.pdf',
    '11.1 - CND - Trabalhistas.pdf',
    '11.2 - CND - FGTS.pdf',
    '11.3 - CND - TRIBUTOS FEDERAIS.pdf',
    '11.4 - CND - TRIBUTOS ESTADUAIS.pdf',
    '11.5 - CND - TRIBUTOS MUNICIPAIS.pdf',
    '12.1 - CND - MATRÍCULA NO INSS - CEI/CNO.pdf'
    ]



def obter_diretório_origem():
    return 'Caminho'

def carregar_configuracoes(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {caminho_arquivo}")
        return {}
    except json.JSONDecodeError:
        print(f"Erro ao decodificar o arquivo JSON: {caminho_arquivo}")
        return {}
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return {}

def salvar_configuracoes(caminho_arquivo, dados):
    try:
        with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=4)
    except IOError:
        print(f"Erro ao salvar o arquivo: {caminho_arquivo}")
    except Exception as e:
        print(f"Erro inesperado: {e}")


    # Defina o caminho do arquivo JSON
config_file = os.path.join(os.path.dirname(__file__), 'config.json')

    # Carregar os dados
dados_configuracao = carregar_configuracoes(config_file)



def carregar_configuracoes_acuracia(self):
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            dados_configuracao = json.load(f)
    else:
        dados_configuracao = {"acuracia": 50}  # Valor padrão
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(dados_configuracao, f, indent=4)
