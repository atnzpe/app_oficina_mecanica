# -*- coding: utf-8 -*-

# =================================================================================
# MÓDULO DO VIEWMODEL DO FORMULÁRIO DE OS (os_formulario_viewmodel.py)
#
# OBJETIVO: Conter a lógica de negócio e o estado do formulário de Ordem de Serviço.
#
# CORREÇÃO (BUG FIX):
#   - Corrigido o caminho de importação da 'fila_db'. A fila é definida em
#     'database.py' e deve ser importada diretamente de lá, que é sua
#     "fonte da verdade".
# =================================================================================
import flet as ft
import logging
from typing import List
from src.models.models import Cliente, Carro, Peca
from src.database.database import fila_db
from src.database import queries



class OrdemServicoFormularioViewModel:
    """
    O ViewModel para a OrdemServicoFormularioView.
    """
    def __init__(self, page: ft.Page):
        self.page = page
        
        self._view: 'OrdemServicoFormularioView' | None = None

        # --- Estado do Componente ---
        self.pecas_selecionadas: List[dict] = []
        self.lista_clientes: List[Cliente] = []
        self.lista_pecas: List[Peca] = []

    def vincular_view(self, view: 'OrdemServicoFormularioView'):
        """Estabelece a conexão de duas vias entre o ViewModel e a View."""
        self._view = view

    def carregar_dados_iniciais(self):
        """Carrega clientes e peças do banco para o estado do ViewModel."""
        logging.info("ViewModel-OS: Carregando dados iniciais.")
        # O ViewModel usa sua própria conexão para operações de leitura síncronas.
        self.lista_clientes = queries.obter_clientes()
        self.lista_pecas = queries.obter_pecas()
        if self._view:
            self._view.popular_dropdowns_iniciais(self.lista_clientes, self.lista_pecas)

    def cliente_selecionado(self, cliente_id: int):
        """Lógica acionada quando um cliente é selecionado na View."""
        logging.info(f"ViewModel-OS: Cliente ID {cliente_id} selecionado.")
        carros = []
        if cliente_id:
            carros = queries.obter_carros_por_cliente(int(cliente_id))
        if self._view:
            self._view.popular_dropdown_carros(carros)

    def adicionar_peca_a_lista(self, peca_id: int, quantidade: int):
        """Valida e adiciona uma peça à lista da OS."""
        peca_obj = next((p for p in self.lista_pecas if p.id == int(peca_id)), None)
        if peca_obj and quantidade > 0:
            self.pecas_selecionadas.append({
                "peca_obj": peca_obj,
                "quantidade": quantidade,
                "valor_unitario": peca_obj.preco_venda,
                "valor_total": peca_obj.preco_venda * quantidade
            })
            logging.info(f"ViewModel-OS: Peça '{peca_obj.nome}' adicionada.")
            self._atualizar_view()
        elif self._view:
            self._view.mostrar_feedback("Seleção de peça ou quantidade inválida.", False)

    def remover_peca_da_lista(self, index: int):
        """Remove uma peça da lista da OS."""
        if 0 <= index < len(self.pecas_selecionadas):
            peca_removida = self.pecas_selecionadas.pop(index)
            logging.info(f"ViewModel-OS: Peça '{peca_removida['peca_obj'].nome}' removida.")
            self._atualizar_view()

    def processar_criacao_os(self, cliente_id: int, carro_id: int, mao_de_obra_str: str):
        """Valida os dados finais e envia a OS para a fila de processamento."""
        if not all([cliente_id, carro_id, self.pecas_selecionadas]):
            if self._view: self._view.mostrar_feedback("Cliente, Carro e ao menos uma Peça são obrigatórios.", False)
            return

        try:
            mao_de_obra = float(mao_de_obra_str or 0)
        except (ValueError, TypeError):
            mao_de_obra = 0.0

        total_pecas = sum(item['valor_total'] for item in self.pecas_selecionadas)
        dados_os = {
            "cliente_id": int(cliente_id),
            "carro_id": int(carro_id),
            "pecas_quantidades": {item['peca_obj'].id: item['quantidade'] for item in self.pecas_selecionadas},
            "valor_total": total_pecas + mao_de_obra,
            "mao_de_obra": mao_de_obra,
        }

        logging.info("ViewModel-OS: OS validada. Enviando para processamento na fila do DB...")
        # Adiciona a tarefa de 'criar_ordem_servico' na fila para ser processada pela thread.
        fila_db.put(("criar_ordem_servico", dados_os))
        
        if self._view:
            self._view.fechar_modal()
            self._view.mostrar_feedback("Ordem de Serviço enviada para criação!", True)

    def _atualizar_view(self):
        """Comanda a View para se redesenhar com os dados atualizados."""
        if self._view:
            self._view.atualizar_visualizacao_pecas(self.pecas_selecionadas)
            self._view.atualizar_valor_total(self.pecas_selecionadas)