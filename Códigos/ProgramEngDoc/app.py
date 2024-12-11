#app.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from file_operations import processar_documentos
import sys
import shutil
import os
import re
import json
from tkinter import simpledialog
from PIL import Image, ImageTk
from mesc import mesclar_pdfs, gerar_imagem_thumbnail  # Importando funções de mesc.py
from config import carregar_configuracoes, salvar_configuracoes, obter_palavras_chave, obter_novos_nomes, carregar_configuracoes_acuracia
import config_manager
import logging
import PyPDF2
from fuzzywuzzy import process

class RedirectToText:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

    def write(self, message):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, message)
        self.text_widget.config(state=tk.DISABLED)
        self.text_widget.yview(tk.END)

    def flush(self):
        pass

    def reset(self):
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr

    def redirect(self):
        sys.stdout = self
        sys.stderr = self

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Documentos")
        self.root.geometry("1900x1080")  # Tamanho inicial maior para melhor visibilidade
        self.root.minsize(700, 500)  # Definir um tamanho mínimo
      

        # Configuração de estilo
        style = ttk.Style()
        style.configure("TButton", background="#007bff", foreground="black", font=("Arial", 12))
        style.configure("TLabel", background="#e9ecef", foreground="#343a40", font=("Arial", 12))
        style.configure("TFrame", background="#e9ecef")
        style.configure("TNotebook", background="#e9ecef")
        style.configure("TNotebook.Tab", background="#0056b3", foreground="black", padding=[10, 5], font=("Arial", 12, "bold"))
        style.map("TNotebook.Tab", background=[('selected', '#004085')], foreground=[('selected', 'blue')])

        # Frame principal
        self.frame_main = ttk.Frame(self.root, padding="15")
        self.frame_main.pack(fill="both", expand=True)

        # Notebook para interface com abas
        self.notebook = ttk.Notebook(self.frame_main)
        self.notebook.pack(fill="both", expand=True)

        # Abas
        self.tab_home = ttk.Frame(self.notebook, padding="15")
        self.tab_diretorio = ttk.Frame(self.notebook, padding="15")
        self.tab_mesclagem = ttk.Frame(self.notebook, padding="15")
        self.tab_log = ttk.Frame(self.notebook, padding="15")  # Aba de Log
        self.tab_configuracoes = ttk.Frame(self.notebook, padding="15")  # Aba de Configurações
        self.tab_sobre = ttk.Frame(self.notebook, padding="15") # aba sobre
        self.notebook.add(self.tab_home, text="Home")
        self.notebook.add(self.tab_diretorio, text="Diretório")
        self.notebook.add(self.tab_mesclagem, text="Mesclagem")
        self.notebook.add(self.tab_log, text="Log")  # Adicionando a aba de log
        self.notebook.add(self.tab_configuracoes, text="Configurações")  # Adicionando a nova aba de configurações
        self.notebook.add(self.tab_sobre, text="Sobre") #adicionando a aba sobre
        

        # Widgets da Aba Home
        self.label_origem = ttk.Label(self.tab_home, text="Diretório de Origem:")
        self.label_origem.grid(row=0, column=0, sticky="w", pady=5)
        self.botao_origem = ttk.Button(self.tab_home, text="Selecionar Diretório de Origem", command=self.selecionar_diretorio_origem)
        self.botao_origem.grid(row=1, column=0, sticky="ew", pady=5)

        self.label_destino = ttk.Label(self.tab_home, text="Diretório de Destino:")
        self.label_destino.grid(row=2, column=0, sticky="w", pady=5)
        self.botao_destino = ttk.Button(self.tab_home, text="Selecionar Diretório de Destino", command=self.selecionar_diretorio_destino)
        self.botao_destino.grid(row=3, column=0, sticky="ew", pady=5)

        self.botao_gerar = ttk.Button(self.tab_home, text="Gerar Documentos", command=self.gerar_documentos)
        self.botao_gerar.grid(row=4, column=0, sticky="ew", pady=10)

        # Label de Instruções
        self.texto_instrucoes = ttk.Label(self.tab_home, text=(\
            "Instruções:\n\n"
            "1. Veja a Acurácia na Aba Log. \n"
            "2. Faça backup dos arquivos antes de rodar o programa. \n"
            "3. Selecione o diretório de origem e destino.\n"
            "4. Clique em 'Gerar Documentos' para iniciar o processo.\n"
            "5. Use 'Diretório' para apagar ou abrir o diretório de destino. \n"
            "6. Aperte Esc para sair da tela cheia"
        ), wraplength=650, justify="left")
        self.texto_instrucoes.grid(row=5, column=0, pady=15, sticky="w")

        

        # Widgets da Aba Diretório
        self.botao_abrir_pasta = ttk.Button(self.tab_diretorio, text="Abrir Pasta Gerada", command=self.abrir_pasta_destino)
        self.botao_abrir_pasta.pack(pady=10)

        self.botao_apagar_pasta = ttk.Button(self.tab_diretorio, text="Apagar Pasta de Destino", command=self.apagar_pasta)
        self.botao_apagar_pasta.pack(pady=10)

        # Widgets da Aba Mesclagem
        self.botao_selecionar_pdfs = ttk.Button(self.tab_mesclagem, text="Selecionar PDFs", command=self.selecionar_pdfs)
        self.botao_selecionar_pdfs.pack(pady=10)

        self.label_nome_arquivo = ttk.Label(self.tab_mesclagem, text="Nome do Arquivo Mesclado:")
        self.label_nome_arquivo.pack(pady=5)

        self.entrada_nome_arquivo = ttk.Entry(self.tab_mesclagem, width=50)
        self.entrada_nome_arquivo.pack(pady=5)

        self.botao_mesclar = ttk.Button(self.tab_mesclagem, text="Mesclar PDFs", command=self.mesclar_pdfs)
        self.botao_mesclar.pack(pady=10)

        # Adicionando o botão de auto mesclagem
        self.botao_auto_mesclar = ttk.Button(self.tab_mesclagem, text="Auto Mesclar PDFs", command=self.auto_mesclar_pdfs)
        self.botao_auto_mesclar.pack(pady=10)
        # Personalizar o botão para ter fundo vermelho e texto branco
        self.botao_auto_mesclar.configure(style='Red.TButton')
        
        # Criar o estilo para o botão
        style = ttk.Style()
        style.configure('Red.TButton', background='red', foreground='black', borderwidth=1, relief='solid')

      

        # Label para exibir nomes dos arquivos selecionados
        self.label_arquivos_selecionados = ttk.Label(self.tab_mesclagem, text="Arquivos Selecionados:")
        self.label_arquivos_selecionados.pack(pady=5)

        self.texto_arquivos_selecionados = tk.Text(self.tab_mesclagem, height=10, wrap="word", state=tk.DISABLED)
        self.texto_arquivos_selecionados.pack(pady=5, fill="both", expand=True)

        self.frame_preview = ttk.Frame(self.tab_mesclagem)
        self.frame_preview.pack(pady=10, fill="both", expand=True)

        self.label_preview = ttk.Label(self.frame_preview, text="Visualização do PDF Selecionado:")
        self.label_preview.pack()

        self.canvas_preview = tk.Canvas(self.frame_preview, bg='white')
        self.canvas_preview.pack(fill="both", expand=True)

        self.scroll_x = tk.Scrollbar(self.frame_preview, orient="horizontal", command=self.canvas_preview.xview)
        self.scroll_x.pack(side="bottom", fill="x")
        self.scroll_y = tk.Scrollbar(self.frame_preview, orient="vertical", command=self.canvas_preview.yview)
        self.scroll_y.pack(side="right", fill="y")

        self.canvas_preview.config(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)

        self.canvas_preview.bind("<MouseWheel>", self.zoom)  # Binding para zoom com a roda do mouse

        # Campo de Log na Aba Log
        # Adiciona o botão para limpar o log
        self.clear_button = tk.Button(self.tab_log, text="Limpar Log", command=self.clear_log)
        self.clear_button.pack(pady=10, fill="x")
        self.texto_log = tk.Text(self.tab_log, height=25, wrap="word")
        self.texto_log.pack(pady=15, fill="both", expand=True)
        self.texto_log.insert(tk.END, "Logs:\n")
        self.texto_log.config(state=tk.DISABLED)  # Inicialmente, o campo é somente leitura

        # Adiciona o botão para limpar o log
        self.clear_button = tk.Button(self.tab_log, text="Limpar Log", command=self.clear_log)
        self.clear_button.pack(pady=10, fill="x")

        # Redirecionar stdout e stderr para o widget de texto na aba de log
        self.redirector = RedirectToText(self.texto_log)
        self.redirector.redirect()

        # Configure a expansão do widget de log
        self.tab_log.grid_rowconfigure(0, weight=1)
        self.tab_log.grid_columnconfigure(0, weight=1)


        # Adiciona título
        titulo = ttk.Label(self.tab_sobre, text="Sobre o Programa", font=("Helvetica", 16))
        titulo.pack(pady=10)

        # Texto de descrição
        descricao = ttk.Label(self.tab_sobre, text=("Este software foi desenvolvido para controlar e nomear múltiplos arquivos PDF."
                                                    "Utiliza a biblioteca fuzzywuzzy, que emprega IA para calcular a probabilidade de acerto em relação a uma lista de nomes pré-definidos."
                                                    "Além disso, oferece a função de mesclagem, onde voce pode fazer manualmente ou através de um método automático."
                                                    "Você pode incluir palavras-chave para reconhecer e corrigir automaticamente erros nos nomes."), wraplength=500)
        descricao.pack(pady=10)

        # Tabela sobre acurácia
        frame_tabela_acuracia = ttk.Frame(self.tab_sobre)
        frame_tabela_acuracia.pack(pady=10, fill="x")
        ttk.Label(frame_tabela_acuracia, text="Como Funciona a Acurácia").pack(pady=5)
        
        tree = ttk.Treeview(frame_tabela_acuracia, columns=("Coluna1", "Coluna2"), show='headings')
        tree.heading("Coluna1", text="Aspecto")
        tree.heading("Coluna2", text="Descrição")
        
        tree.insert("", "end", values=("Acurácia", "Limite de precisão do modelo. Limite de Percentual de acertos."))
        tree.insert("", "end", values=("Valores Indicados", "Entre 40% e 55% é considerado excelente."))
        tree.insert("", "end", values=("Mesclagem", "Voce pode mesclar antes de definir nomes, fica melhor de apurar, mas pode depois também."))
        tree.insert("", "end", values=("Não aconselho", "Usar mais de uma vez o programa na mesma pasta."))
        tree.insert("", "end", values=("Cópia", "O programa muda também o arquivo Original então tome cuidado, faça um backup antes."))
        tree.insert("", "end", values=("Log", "Use o Log para ver o comportamento do programa e a acurácia que esta salvo no programa."))
        tree.insert("", "end", values=("Mesclagem Automática", "Essa opção identifica os arquivos pelo número, então antes de usar essa opção verifique se os números estão certos"))

        tree.pack(pady=5, fill="x")

        descricao = ttk.Label(self.tab_sobre, text=("O programa calcula a porcentagem de cada palavra ser igual a palavra que se deseja renomear, cada palavra tem um score de porcentagem"
                                                    "Se o limite do score for muito alto significa que o programa e só aceita renomear palavras com score muito alto"
                                                    "e isso acaba cortando o renome de alguns documentos."
                                                    "Se for muita baixo a acuracia, o score fica muito literal e erra com mais facilidade"
                                                    "O ideal é manter os nomes dos arquivos parecidos com aquilo que eles devem ser realmente, o programa não vai ler algo que é 100% errado"
                                                    "A imagem do pdf é somente do primeiro documento escolhido. \n\n\n"), wraplength=800)
        descricao.pack(pady=10)

        # Créditos
        creditos = ttk.Label(self.tab_sobre, text=("Créditos:\nDesenvolvedor: Gabriel André\n"
                                                   "Versão: 1.0"), font=("Helvetica", 12))
        creditos.pack(pady=10)

        # Adicionando imagem
        image_path = os.path.join(os.path.dirname(__file__), 'C:/Users/biela/OneDrive/Documentos/Python/programaeng/th.jpg')  # Substitua pelo caminho da sua imagem
        if os.path.exists(image_path):
            image = Image.open(image_path)
            image = image.resize((200, 200))  # Define o tamanho desejado
            photo = ImageTk.PhotoImage(image)
            image_label = tk.Label(self.tab_sobre, image=photo)
            image_label.image = photo  # Manter referência da imagem
            image_label.pack(pady=4)




         # Widgets da Aba Configurações
        self.frame_palavras_chave = ttk.Frame(self.tab_configuracoes)
        self.frame_palavras_chave.pack(pady=10, fill="x")

        self.label_palavras_chave = ttk.Label(self.frame_palavras_chave, text="Palavras-Chave Carregadas:")
        self.label_palavras_chave.pack(pady=5)

        self.texto_palavras_chave = tk.Text(self.frame_palavras_chave, height=10, wrap="word", state=tk.DISABLED)
        self.texto_palavras_chave.pack(pady=5, fill="both", expand=True)

        self.frame_novas_palavras = ttk.Frame(self.tab_configuracoes)
        self.frame_novas_palavras.pack(pady=10, fill="x")

        self.label_chave_nova = ttk.Label(self.frame_novas_palavras, text="Nova Chave:")
        self.label_chave_nova.grid(row=0, column=0, padx=5, pady=5)
        self.entrada_chave_nova = ttk.Entry(self.frame_novas_palavras, width=30)
        self.entrada_chave_nova.grid(row=0, column=1, padx=5, pady=5)

        self.label_palavras_novas = ttk.Label(self.frame_novas_palavras, text="Palavras (separadas por vírgulas):")
        self.label_palavras_novas.grid(row=1, column=0, padx=5, pady=5)
        self.entrada_palavras_novas = ttk.Entry(self.frame_novas_palavras, width=30)
        self.entrada_palavras_novas.grid(row=1, column=1, padx=5, pady=5)

        self.botao_adicionar_palavras = ttk.Button(self.frame_novas_palavras, text="Adicionar Palavras", command=self.adicionar_palavras_chave)
        self.botao_adicionar_palavras.grid(row=2, column=0, columnspan=2, pady=10)

        self.botao_remover_palavras = ttk.Button(self.frame_novas_palavras, text="Remover Palavra-Chave", command=self.remover_palavras_chave)
        self.botao_remover_palavras.grid(row=3, column=0, columnspan=2, pady=10)

        self.botao_atualizar_palavras = ttk.Button(self.tab_configuracoes, text="Atualizar Visualização Palavras", command=self.atualizar_exibicao_palavras_chave)
        self.botao_atualizar_palavras.pack(pady=10)

        self.frame_nomes = ttk.Frame(self.tab_configuracoes)
        self.frame_nomes.pack(pady=10, fill="x")

        self.label_nomes = ttk.Label(self.frame_nomes, text="Nomes Carregados:")
        self.label_nomes.pack(pady=5)

        self.texto_nomes = tk.Text(self.frame_nomes, height=10, wrap="word", state=tk.DISABLED)
        self.texto_nomes.pack(pady=5, fill="both", expand=True)

        self.frame_novo_nome = ttk.Frame(self.tab_configuracoes)
        self.frame_novo_nome.pack(pady=10, fill="x")

        self.label_nome_novo = ttk.Label(self.frame_novo_nome, text="Novo Nome:")
        self.label_nome_novo.grid(row=0, column=0, padx=5, pady=5)
        self.entrada_nome_novo = ttk.Entry(self.frame_novo_nome, width=30)
        self.entrada_nome_novo.grid(row=0, column=1, padx=5, pady=5)

        self.botao_adicionar_nome = ttk.Button(self.frame_novo_nome, text="Adicionar Nome", command=self.adicionar_nome)
        self.botao_adicionar_nome.grid(row=1, column=0, columnspan=2, pady=10)

        self.botao_remover_nome = ttk.Button(self.frame_novo_nome, text="Remover Nome", command=self.remover_nome)
        self.botao_remover_nome.grid(row=2, column=0, columnspan=2, pady=10)

        self.botao_atualizar_nomes = ttk.Button(self.tab_configuracoes, text="Atualizar Visualização Nomes", command=self.atualizar_exibicao_nomes)
        self.botao_atualizar_nomes.pack(pady=10)

         # Adicionando widgets Acurácia
        self.frame_slider_acuracia = ttk.Frame(self.tab_configuracoes)
        self.frame_slider_acuracia.pack(pady=10, fill="x")

        self.label_acuracia = ttk.Label(self.frame_slider_acuracia, text="Acurácia:")
        self.label_acuracia.pack(side="left", padx=5)

        self.slider_acuracia = tk.Scale(self.frame_slider_acuracia, from_=0, to=100, orient="horizontal", length=300)
        self.slider_acuracia.pack(side="left", fill="x", expand=True, padx=5)

        self.botao_atualizar = ttk.Button(self.frame_slider_acuracia, text="Atualizar", command=self.atualizar_acuracia)
        self.botao_atualizar.pack(side="left", padx=5)

        self.label_acuracia_atual = ttk.Label(self.frame_slider_acuracia, text="Acurácia Atual: 0")
        self.label_acuracia_atual.pack(side="left", padx=5)


        # Defina o caminho do arquivo JSON
        self.config_file = os.path.join(os.path.dirname(__file__), 'config.json')

        # Carregar os dados
        self.dados_configuracao = carregar_configuracoes(self.config_file)

        # Exibir os dados
        self.atualizar_exibicao_palavras_chave()
        self.atualizar_exibicao_nomes()


        if 'palavras_chave' not in self.dados_configuracao:
            self.dados_configuracao['palavras_chave'] = {}
        if 'novos_nomes' not in self.dados_configuracao:
            self.dados_configuracao['novos_nomes'] = []

        logging.basicConfig(level=logging.INFO)

    def atualizar_acuracia(self):
        try:
            acuracia = self.slider_acuracia.get()
            self.label_acuracia_atual.config(text=f"Acurácia Atual: {acuracia}")
            print(f"Acurácia Atual: {acuracia}")

            # Atualiza a configuração
            self.dados_configuracao["acuracia"] = acuracia

            # Salva as configurações
            self.salvar_configuracoes()

            messagebox.showinfo("Atualização", f"Acurácia atualizada para {acuracia}.")
        except Exception as e:
            print(f"Erro ao atualizar acurácia: {e}")
            messagebox.showerror("Erro", f"Erro ao atualizar acurácia: {e}")

    def atualizar_valor_slider(self, event):
        acuracia = self.slider_acuracia.get()
        self.label_slider_valor.config(text=f"{acuracia}")
        self.label_acuracia_atual.config(text=f"Acurácia Atual: {acuracia}")  # Atualiza o novo label


    def carregar_configuracoes(self):
        if os.path.exists(self.config_file):
            self.dados_configuracao = carregar_configuracoes(self.config_file)
            self.dados_configuracao = json.load(self.config_file)
        else:
            self.dados_configuracao = obter_palavras_chave()
            self.dados_configuracao.update(obter_novos_nomes())  # Combine os dados padrão
            self.dados_configuracao = {"acuracia": 50}
            salvar_configuracoes(self.config_file, self.dados_configuracao)


    # Inicialize o slider e o label com a acurácia carregada
        acuracia = self.dados_configuracao.get("acuracia", 50)
        self.slider_acuracia.set(acuracia)
        self.label_slider_valor.config(text=f"{acuracia}")
        self.label_acuracia_atual.config(text=f"Acurácia Atual: {acuracia}")


    def salvar_configuracoes(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.dados_configuracao, f, indent=4)


    def atualizar_exibicao_palavras_chave(self):
        self.texto_palavras_chave.config(state=tk.NORMAL)
        self.texto_palavras_chave.delete(1.0, tk.END)
    
        # Certifique-se de que 'palavras_chave' é a chave certa no dicionário
        print("Estrutura de dados para palavras-chave:", self.dados_configuracao)  # Para depuração
    
        palavras_chave = self.dados_configuracao.get('palavras_chave', {})
        for chave, palavras in palavras_chave.items():
            self.texto_palavras_chave.insert(tk.END, f"{chave}: {', '.join(palavras)}\n")
    
        self.texto_palavras_chave.config(state=tk.DISABLED)

    def atualizar_exibicao_nomes(self):
        self.texto_nomes.config(state=tk.NORMAL)
        self.texto_nomes.delete(1.0, tk.END)
    
        # Certifique-se de que 'novos_nomes' é a chave certa no dicionário
        print("Estrutura de dados para nomes:", self.dados_configuracao)  # Para depuração
    
        nomes = self.dados_configuracao.get('novos_nomes', [])
        for nome in nomes:
            self.texto_nomes.insert(tk.END, f"{nome}\n")
    
        self.texto_nomes.config(state=tk.DISABLED)


    def adicionar_palavras_chave(self):
        try:
            chave = self.entrada_chave_nova.get().strip()
            palavras = self.entrada_palavras_novas.get().strip().split(',')

            if chave and palavras:
                palavras = [p.strip() for p in palavras if p.strip()]  # Remover espaços e palavras vazias
                if chave in self.dados_configuracao["palavras_chave"]:
                    # Atualiza palavras se a chave já existe
                    palavras_existentes = set(self.dados_configuracao["palavras_chave"][chave])
                    novas_palavras = set(palavras) - palavras_existentes
                    self.dados_configuracao["palavras_chave"][chave].extend(novas_palavras)
                else:
                    # Adiciona nova chave com as palavras
                    self.dados_configuracao["palavras_chave"][chave] = palavras
                self.salvar_configuracoes()
                self.atualizar_exibicao_palavras_chave()
                messagebox.showinfo("Sucesso", "Palavras-chave adicionadas com sucesso.")
            else:
                messagebox.showwarning("Atenção", "Por favor, insira uma chave e palavras.")
        except Exception as e:
            print(f"Erro ao adicionar palavras-chave: {e}")


    def remover_palavras_chave(self):
        try:
            chave = simpledialog.askstring("Remover Palavra-Chave", "Digite a chave para remover:")
            if chave:
                if chave in self.dados_configuracao["palavras_chave"]:
                    del self.dados_configuracao["palavras_chave"][chave]
                    self.salvar_configuracoes()
                    self.atualizar_exibicao_palavras_chave()
                    messagebox.showinfo("Sucesso", "Palavra-chave removida com sucesso.")
                else:
                    messagebox.showerror("Erro", "Palavra-chave não encontrada.")
        except Exception as e:
            print(f"Erro ao remover palavras-chave: {e}")


    def adicionar_nome(self):
        try:
            nome = self.entrada_nome_novo.get().strip()
            if nome:
                nomes = self.dados_configuracao.get('novos_nomes', [])
                if nome not in nomes:
                    nomes.append(nome)
                    self.dados_configuracao['novos_nomes'] = nomes
                    self.salvar_configuracoes()
                    self.atualizar_exibicao_nomes()
                    messagebox.showinfo("Sucesso", "Nome adicionado com sucesso.")
                else:
                    messagebox.showwarning("Atenção", "Nome já existe.")
            else:
                messagebox.showwarning("Atenção", "Por favor, insira um nome.")
        except Exception as e:
            print(f"Erro ao adicionar nome: {e}")

    def remover_nome(self):
        try:
            nome = simpledialog.askstring("Remover Nome", "Digite o nome para remover:")
            if nome:
                nomes = self.dados_configuracao.get('novos_nomes', [])
                if nome in nomes:
                    nomes.remove(nome)
                    self.dados_configuracao['novos_nomes'] = nomes
                    self.salvar_configuracoes()
                    self.atualizar_exibicao_nomes()
                    messagebox.showinfo("Sucesso", "Nome removido com sucesso.")
                else:
                    messagebox.showerror("Erro", "Nome não encontrado.")
        except Exception as e:
            print(f"Erro ao remover nome: {e}")

    def selecionar_diretorio_origem(self):
        self.diretorio_origem = filedialog.askdirectory()
        if self.diretorio_origem:
            self.label_origem.config(text=f"Diretório de Origem: {self.diretorio_origem}")

    def selecionar_diretorio_destino(self):
        self.diretorio_destino = filedialog.askdirectory()
        if self.diretorio_destino:
            self.label_destino.config(text=f"Diretório de Destino: {self.diretorio_destino}")

    def gerar_documentos(self):
        if not hasattr(self, 'diretorio_origem') or not hasattr(self, 'diretorio_destino'):
            messagebox.showerror("Erro", "Por favor, selecione os diretórios de origem e destino.")
            return

        try:
            print("Iniciando o processo de geração dos documentos...")
            processar_documentos(self.diretorio_origem, self.diretorio_destino)
            print("Documentos gerados e copiados com sucesso.")
            messagebox.showinfo("Sucesso", "Documentos gerados e copiados com sucesso.")
        except Exception as e:
            print(f"Erro: {e}")
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

    def apagar_pasta(self):
        if not hasattr(self, 'diretorio_destino') or not os.path.isdir(self.diretorio_destino):
            messagebox.showerror("Erro", "Diretório de destino não selecionado.")
            return

        resposta = messagebox.askyesno("Confirmar", "Você realmente deseja apagar a pasta de destino e seu conteúdo?")
        if resposta:
            try:
                shutil.rmtree(self.diretorio_destino)
                print("Pasta apagada com sucesso.")
                messagebox.showinfo("Sucesso", "Pasta apagada com sucesso.")
                self.label_destino.config(text="Diretório de Destino:")
            except Exception as e:
                print(f"Erro: {e}")
                messagebox.showerror("Erro", f"Não foi possível apagar a pasta: {e}")

    def abrir_pasta_destino(self):
        if hasattr(self, 'diretorio_destino') and os.path.isdir(self.diretorio_destino):
            os.startfile(self.diretorio_destino)  # Nota: funciona apenas em Windows
        else:
            messagebox.showerror("Erro", "Diretório de destino não selecionado ou não encontrado.")

    def selecionar_pdfs(self):
        self.pdfs_selecionados = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        if self.pdfs_selecionados:
            # Exibir quais arquivos foram selecionados
            self.texto_arquivos_selecionados.config(state=tk.NORMAL)
            self.texto_arquivos_selecionados.delete(1.0, tk.END)  # Limpar texto existente
            for pdf in self.pdfs_selecionados:
                self.texto_arquivos_selecionados.insert(tk.END, f"{pdf}\n")
            self.texto_arquivos_selecionados.config(state=tk.DISABLED)
            self.texto_arquivos_selecionados.yview(tk.END)
            
            self.atualizar_visualizacao()  # Tentar exibir os PDFs selecionados

    def atualizar_visualizacao(self):
        if not hasattr(self, 'pdfs_selecionados') or not self.pdfs_selecionados:
            return
        
        try:
            self.canvas_preview.delete("all")  # Limpar o canvas antes de adicionar novas imagens
            for pdf_path in self.pdfs_selecionados:
                imagem_thumbnail = gerar_imagem_thumbnail(pdf_path)
                if imagem_thumbnail:
                    tk_image = ImageTk.PhotoImage(imagem_thumbnail)
                    self.canvas_preview.create_image(0, 0, anchor="nw", image=tk_image)
                    self.canvas_preview.image = tk_image  # Manter uma referência à imagem
                    self.canvas_preview.config(scrollregion=self.canvas_preview.bbox("all"))  # Ajustar a área de rolagem
                else:
                    messagebox.showerror("Erro", "Não foi possível gerar a visualização do PDF.")
        except Exception as e:
            print(f"Erro ao atualizar a visualização: {e}")
            messagebox.showerror("Erro", f"Ocorreu um erro ao tentar atualizar a visualização: {e}")

    def mesclar_pdfs(self):
        nome_arquivo = self.entrada_nome_arquivo.get().strip()
        if not nome_arquivo:
            messagebox.showerror("Erro", "Por favor, insira o nome do arquivo mesclado.")
            return
        if not hasattr(self, 'pdfs_selecionados') or not self.pdfs_selecionados:
            messagebox.showerror("Erro", "Nenhum PDF selecionado.")
            return

        try:
            caminho_destino = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], initialfile=nome_arquivo)
            if caminho_destino:
                mesclar_pdfs(self.pdfs_selecionados, caminho_destino)
                messagebox.showinfo("Concluído", "PDFs mesclados com sucesso.")
        except Exception as e:
            print(f"Erro: {e}")
            messagebox.showerror("Erro", f"Ocorreu um erro durante a mesclagem dos PDFs: {e}")

    def zoom(self, event):
        # Zoom usando a roda do mouse
        scale = 1.1
        if event.delta < 0:  # Scroll down
            scale = 1 / scale

        self.canvas_preview.scale("all", event.x, event.y, scale, scale)
        self.canvas_preview.config(scrollregion=self.canvas_preview.bbox("all"))

    def clear_log(self):
        self.texto_log.config(state=tk.NORMAL)
        self.texto_log.delete(1.0, tk.END)
        self.texto_log.config(state=tk.DISABLED)


    def auto_mesclar_pdfs(self):
        # Mensagem explicativa para o usuário
        messagebox.showinfo("Instruções", 
            "O botão 'Auto Mesclar PDFs' irá processar os documentos PDF da seguinte forma:\n\n"
            "1. Primeiramente, os arquivos serão agrupados com base no número presente no início do nome do arquivo.\n"
            "2. Caso o número não esteja presente, o sistema tentará agrupar os arquivos com base no nome do documento usando palavras-chave.\n\n"
            "3. Acurácia padrão definida pode verificar na aba log, para modificar a acurácia mova o slide na aba Configurações.\n\n"
            "Certifique-se de que o número no nome do arquivo está correto e que os documentos estejam corretamente nomeados antes de prosseguir."
        )

        # Mensagem informativa antes de escolher o diretório de origem
        messagebox.showinfo("Escolha do Diretório", "Por favor, escolha o diretório de origem onde estão os arquivos PDF.")

        # Abrir diálogo para selecionar o diretório de origem
        self.diretorio_origem = filedialog.askdirectory(title="Selecione o Diretório de Origem")
        if not self.diretorio_origem:
            messagebox.showerror("Erro", "Diretório de origem não selecionado.")
            return

        # Mensagem informativa antes de escolher o diretório de destino
        messagebox.showinfo("Escolha do Diretório", "Agora, por favor, escolha o diretório de destino onde os arquivos mesclados serão salvos.")

        # Abrir diálogo para selecionar o diretório de destino
        self.diretorio_destino = filedialog.askdirectory(title="Selecione o Diretório de Destino")
        if not self.diretorio_destino:
            messagebox.showerror("Erro", "Diretório de destino não selecionado.")
            return

        # Usar o caminho absoluto para o arquivo JSON
        caminho_json = os.path.join(os.path.dirname(__file__), 'automesc.json')
        print(f"Procurando arquivo de configuração em: {caminho_json}")

        if not os.path.isfile(caminho_json):
            messagebox.showerror("Erro", f"Arquivo de configuração '{caminho_json}' não encontrado.")
            return

        try:
            with open(caminho_json, 'r', encoding='utf-8') as f:
                configuracao = json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("Erro", "Erro ao ler o arquivo de configuração.")
            return

        palavras_chave = configuracao.get('palavras_chave', {})
        novos_nomes = configuracao.get('novos_nomes', [])

        if not isinstance(palavras_chave, dict) or not isinstance(novos_nomes, list):
            messagebox.showerror("Erro", "Formato de configuração inválido.")
            return

        # Obtendo o valor de acurácia
        acuracia = self.dados_configuracao.get("acuracia", 60)
        print(f"Acurácia utilizada: {acuracia}")

        arquivos_pdf = [f for f in os.listdir(self.diretorio_origem) if f.lower().endswith('.pdf')]

        grupos = {key: [] for key in palavras_chave.keys()}

        print(f"Arquivos PDF encontrados: {arquivos_pdf}")

        for arquivo in arquivos_pdf:
            # Extrair o número do grupo do nome do arquivo
            match = re.match(r'(\d+)\.', arquivo)
            if match:
                numero_grupo = match.group(1)
                if numero_grupo in grupos:
                    grupos[numero_grupo].append(arquivo)
                    continue
            
            # Se o número do grupo não for encontrado, tentar a correspondência por palavras-chave
            arquivo_lower = arquivo.lower()
            adicionado = False
            for grupo, nomes in palavras_chave.items():
                melhor_correspondencia, pontuacao = process.extractOne(arquivo_lower, [nome.lower() for nome in nomes])
                if pontuacao >= acuracia:  # Usar o valor de acurácia aqui
                    grupos[grupo].append(arquivo)
                    adicionado = True
                    break
            if not adicionado:
                print(f"Arquivo '{arquivo}' não corresponde a nenhum grupo.")

        print(f"Grupos criados: {grupos}")

        for grupo, arquivos in grupos.items():
            if not arquivos:
                print(f"Nenhum arquivo encontrado para o grupo '{grupo}'.")
                continue

            pdf_writer = PyPDF2.PdfWriter()

            for arquivo in arquivos:
                caminho_arquivo = os.path.join(self.diretorio_origem, arquivo)
                try:
                    pdf_reader = PyPDF2.PdfReader(caminho_arquivo)
                    for pagina in range(len(pdf_reader.pages)):
                        pdf_writer.add_page(pdf_reader.pages[pagina])
                    print(f"Adicionado arquivo '{arquivo}' ao grupo '{grupo}'.")
                except Exception as e:
                    print(f"Erro ao processar o arquivo '{arquivo}': {e}")
                    messagebox.showerror("Erro", f"Erro ao processar o arquivo '{arquivo}': {e}")
                    continue

            if pdf_writer.pages:
                novo_nome = novos_nomes[int(grupo) - 1] if int(grupo) - 1 < len(novos_nomes) else f"{grupo}.pdf"
                
                # Remover caracteres inválidos do nome do arquivo
                novo_nome = re.sub(r'[<>:"/\\|?*]', '', novo_nome)
                
                caminho_saida = os.path.join(self.diretorio_destino, novo_nome)
                try:
                    with open(caminho_saida, 'wb') as f_out:
                        pdf_writer.write(f_out)
                    print(f"Arquivo mesclado salvo como '{caminho_saida}'.")
                except Exception as e:
                    print(f"Erro ao salvar o arquivo '{novo_nome}': {e}")
                    messagebox.showerror("Erro", f"Erro ao salvar o arquivo '{novo_nome}': {e}")
                    continue

        messagebox.showinfo("Sucesso", "Mesclagem automática concluída.")



if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
