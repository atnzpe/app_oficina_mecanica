# =================================================================================
# MÓDULO DO VIEWMODEL DE DADOS DA OFICINA (dados_oficina_viewmodel.py)
#
# ATUALIZAÇÃO (Issue #30):
#   - Adicionada a lógica de upload de logo (FilePicker, cópia de arquivo
#     e atualização do banco).
# =================================================================================
import flet as ft
import logging
import shutil  # Importa a biblioteca para cópia de arquivos
from src.database import queries
from src.models.models import Estabelecimento
from typing import Optional

logger = logging.getLogger(__name__)


class DadosOficinaViewModel:
    def __init__(self, page: ft.Page):
        self.page = page
        self._view: 'DadosOficinaView' | None = None
        self.usuario_logado = self.page.session.get("usuario_logado")
        self.estabelecimento: Optional[Estabelecimento] = None

        # --- Lógica do FilePicker ---
        # 1. Instancia o FilePicker
        self._file_picker = ft.FilePicker(on_result=self._on_logo_selecionada)

        logger.debug("DadosOficinaViewModel inicializado.")

    def vincular_view(self, view: 'DadosOficinaView'):
        """Vincula a View ao ViewModel."""
        self._view = view
        # 2. Adiciona o FilePicker à overlay da página (NECESSÁRIO)
        if self._file_picker not in self.page.overlay:
            self.page.overlay.append(self._file_picker)
            self.page.update()

    def carregar_dados(self):
        """Busca os dados do estabelecimento e comanda a View para preencher o formulário."""
        if not self._view or not self.usuario_logado:
            return

        try:
            logger.info(
                f"ViewModel: buscando dados do estabelecimento para o usuário ID {self.usuario_logado.id}")
            self.estabelecimento = queries.obter_estabelecimento_por_id_usuario(
                self.usuario_logado.id)

            if self.estabelecimento:
                self._view.preencher_formulario(self.estabelecimento)
                # Comanda a view para exibir a logo que está no banco
                if self.estabelecimento.logo_path:
                    self._view.atualizar_logo_exibida(
                        self.estabelecimento.logo_path)
            else:
                self._view.mostrar_dialogo_feedback(
                    "Erro", "Nenhum estabelecimento encontrado.")
        except Exception as e:
            logger.error(
                f"Erro crítico ao carregar dados do estabelecimento: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback(
                    "Erro Crítico", f"Não foi possível carregar os dados.\nErro: {e}")

    def salvar_alteracoes(self):
        """Valida e salva as alterações de *texto* no banco de dados."""
        # (Lógica de salvar os campos de texto permanece a mesma)
        if not self._view or not self.estabelecimento:
            return
        try:
            dados = self._view.obter_dados_formulario()
            if not dados.get("nome", "").strip():
                self._view.mostrar_dialogo_feedback(
                    "Erro de Validação", "O campo 'Nome da Oficina' é obrigatório.")
                return
            logger.info(
                f"ViewModel: salvando alterações de texto para o ID {self.estabelecimento.id}")
            sucesso = queries.atualizar_estabelecimento(
                self.estabelecimento.id, dados)

            def acao_navegacao(): return self.page.go("/dashboard")
            if sucesso:
                self._view.mostrar_dialogo_feedback(
                    "Sucesso!", "Dados da oficina atualizados com sucesso!", acao_navegacao)
            else:
                self._view.mostrar_dialogo_feedback(
                    "Atenção", "Nenhuma alteração foi salva.", acao_navegacao)
        except Exception as e:
            logger.error(
                f"Erro crítico ao salvar alterações: {e}", exc_info=True)
            if self._view:
                self._view.mostrar_dialogo_feedback(
                    "Erro Crítico", f"Não foi possível salvar as alterações.\nErro: {e}")

    # --- NOVOS MÉTODOS PARA UPLOAD DA LOGO ---

    def abrir_seletor_logo(self, e):
        """Comanda a View (FilePicker) para abrir o seletor de arquivos."""
        logger.debug("ViewModel: Abrindo seletor de arquivos para logo.")
        self._file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["png", "jpg", "jpeg"],
            dialog_title="Selecione a logo da oficina"
        )

    def _on_logo_selecionada(self, e: ft.FilePickerResultEvent):
        """Callback executado quando o usuário seleciona um arquivo."""
        if not self._view or not self.estabelecimento:
            return

        # 1. Verifica se um arquivo foi realmente selecionado
        if e.files and len(e.files) > 0:
            arquivo_selecionado = e.files[0]
            caminho_origem = arquivo_selecionado.path
            nome_arquivo = f"logo_oficina_{self.estabelecimento.id}.{arquivo_selecionado.name.split('.')[-1]}"

            # 2. Define o caminho de destino (dentro do projeto)
            caminho_destino = f"assets/uploads/{nome_arquivo}"

            logger.info(
                f"ViewModel: Logo selecionada. Copiando de '{caminho_origem}' para '{caminho_destino}'.")

            try:
                # 3. Copia o arquivo
                shutil.copy(caminho_origem, caminho_destino)

                # 4. Atualiza o banco de dados com o NOVO caminho
                queries.atualizar_logo_estabelecimento(
                    self.estabelecimento.id, caminho_destino)

                # 5. Comanda a View para exibir a nova imagem
                self._view.atualizar_logo_exibida(caminho_destino)
                self._view.mostrar_dialogo_feedback(
                    "Sucesso!", "Logo atualizada com sucesso.")

            except Exception as ex:
                logger.error(
                    f"Falha ao copiar ou salvar o arquivo da logo: {ex}", exc_info=True)
                self._view.mostrar_dialogo_feedback(
                    "Erro de Upload", f"Não foi possível salvar a imagem.\nErro: {ex}")
        else:
            logger.debug("ViewModel: Seletor de arquivos fechado sem seleção.")
