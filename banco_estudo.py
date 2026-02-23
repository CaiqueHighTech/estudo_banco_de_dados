"""
Sistema de Gerenciamento de Gastos
Arquitetura: MVC + Repository Pattern + Strategy Pattern
"""

import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Callable
from abc import ABC, abstractmethod
import os

class Gasto:
    """Modelo de domínio representando um gasto"""

    def __init__(self, id: Optional[int] = None, descricao: str = "",
                 gasto: float = 0.0, data_gasto: str = ""):
        self.id = id
        self.descricao = descricao
        self.gasto = gasto
        self.data_gasto = data_gasto
    
    def __str__(self):
        return f"ID: {self.id} | {self.descricao} | R$ {self.gasto:.2f} | {self.data_gasto}"
    
    @classmethod
    def from_tuple(cls, data: Tuple) -> 'Gasto':
        """Factory method para criar Gasto a partir de tupla do banco"""
        return cls(id=data[0], descricao=data[1], gasto=data[2], data_gasto=data[3])
    
# ==================== CAMADA DE CONEXÃO ====================

class DatabaseConnection:
    """Singleton para gerenciar conexão com o banco de dados"""

    _instance = None

    def __new__(cls, db_name: str = "estudo.db"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_name: str = "estudo_db"):
        if self._initialized:
            return
        
        self.db_name = db_name
        self.conexao = sqlite3.connect(db_name)
        self.cursor = self.conexao.cursor()
        self._criar_tabela()
        self._initialized = True
        print(f"✓ Conectado ao banco '{db_name}'")

    def _criar_tabela(self) -> None:
        """Cria a tabela se não existir"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS controle_de_gastos(
                id INTEGER PRIMARY KEY,
                descricao TEXT NOT NULL,
                gasto REAL NOT NULL CHECK (gasto > 0),
                data_gasto DATE NOT NULL
            )
        ''')
        self.conexao.commit()

    def commit(self) -> None:
        self.conexao.commit()
    
    def close(self) -> None:
        if self.conexao:
            self.conexao.close()
            print("✓ Conexão encerrada.")

# ==================== CAMADA DE REPOSITÓRIO ====================

class GastoRepository:
    """Padrão Repository - centraliza operações de banco de dados"""

    def __init__(self, db: DatabaseConnection):
        self.db = db

    def inserir(self, gasto: Gasto) -> int:
        """INSERT - Adiciona novo gasto"""
        self.db.cursor.execute('''
            INSERT INTO controle_de_gastos (descricao, gasto, data_gasto)
            VALUES (?, ?, ?)
        ''', (gasto.descricao, gasto.gasto, gasto.data_gasto))
        self.db.commit()
        return self.db.cursor.lastrowid
    
    def buscar_todos(self) -> List[Gasto]:
        """SELECT - Retorna todos os gastos"""
        self.db.cursor.execute('''
            SELECT id, descricao, gasto, data_gasto
            FROM controle_de_gastos
            ORDER BY data_gasto DESC
        ''')
        return [Gasto.from_tuple(row) for row in self.db.cursor.fetchall()]
    
    def buscar_por_id(self, id: int) -> Optional[Gasto]:
        """SELECT com WHERE - Busca gasto por ID"""
        self.db.cursor.execute(
            'SELECT id, descricao, gasto, data_gasto FROM controle_de_gastos WHERE id = ?',
            (id,)
        )
        row = self.db.cursor.fetchone()
        return Gasto.from_tuple(row) if row else None

    def atualizar(self, gasto: Gasto) -> None:
        """UPDATE - Atualiza gasto existente"""
        self.db.cursor.execute('''
            UPDATE controle_de_gastos
            SET descricao = ?, gasto = ?, data_gasto = ?
            WHERE id = ?
        ''', (gasto.descricao, gasto.gasto, gasto.data_gasto, gasto.id))
        self.db.commit()

    def deletar(self, id: int) -> None:
        """DELETE - Remove gasto"""
        self.db.cursor.execute('DELETE FROM controle_de_gastos WHERE id = ?',
            (id,))
        self.db.commit()

    def buscar_por_criterio(self, filtro: str, params: Tuple) -> List[Gasto]:
        """SELECT com WHERE dinâmico"""
        query = f'''
            SELECT id, descricao, gasto, data_gasto
            FROM controle_de_gastos
            WHERE {filtro}
            ORDER BY data_gasto DESC
        '''
        self.db.cursor.execute(query, params)
        return [Gasto.from_tuple(row) for row in self.db.cursor.fetchall()]

    def obter_estatisticas(self) -> Dict:
        """Agregações - Retorna estatísticas dos gastos"""
        stats = {}

        # Total de registros
        stats['total_registros'] = self.db.cursor.fetchone()[0]

        if stats['total_registros'] == 0:
            return stats
        
        # Soma total
        self.db.cursor.execute('SELECT SUM(gasto) FROM controle_de_gastos')
        stats['soma_total'] = self.db.cursor.fetchone()[0]

        # Média
        self.db.cursor.execute('SELECT AVG(gasto) FROM controle_de_gastos')
        stats['media'] = self.db.cursor.fetchone()[0]

        # Maior gasto
        self.db.cursor.execute('SELECT MAX(gasto) FROM controle_de_gastos')
        maior = self.db.cursor.fetchone()
        stats['maior_gasto'] = {'valor': maior[0], 'descricao': maior[1]}

        # Menor gasto
        self.db.cursor.execute('SELECT MIN(gasto) FROM controle_de_gastos')
        menor = self.db.cursor.fetchone()
        stats['menor_gasto'] = {'valor': menor[0], 'descricao': menor[1]}

        # Por mês
        self.db.cursor.execute('''
            SELECT strftime('%Y-%m', data_gasto) as mes,
                   COUNT(*) as quantidade,
                   SUM(gasto) as total
            FROM controle_de_gastos
            GROUP BY mes
            ORDER BY mes DESC
        ''')
        stats['por_mes'] = self.db.cursor.fetchall()

        return stats
    
# ==================== ESTRATÉGIAS DE BUSCA (Strategy Pattern) ====================

class BuscaStrategy(ABC):
    """Interface para estratégias de busca"""

    @abstractmethod
    def executar(self, repo: GastoRepository) -> List[Gasto]:
        pass
        
class BuscaPorDescricao(BuscaStrategy):
    def __init__(self, termo: str):
        self.termo = termo

    def executar(self, repo: GastoRepository) -> List[Gasto]:
        return repo.buscar_por_criterio(
            'descricao LIKE ?',
            (f'%{self.termo}%',)
        )
class BuscaPorValorMinimo(BuscaStrategy):
    def __init__(self, valor_min: float):
        self.valor_min = valor_min
    
    def executar(self, repo: GastoRepository) -> List[Gasto]:
        return repo.buscar_por_criterio(
            'gasto >= ?',
            (self.valor_min,)
        )
    
class BuscaPorValorMaximo(BuscaStrategy):
    def __init__(self, valor_max: float):
        self.valor_max = valor_max
    
    def executar(self, repo: GastoRepository) -> List[Gasto]:
        return repo.buscar_por_criterio(
            'gasto <= ?',
            (self.valor_max,)
        )
    
class BuscaPorPeriodo(BuscaStrategy):
    def __init__(self, data_inicio: str, data_fim: str):
        self.data_inicio = data_inicio
        self.data_fim = data_fim

    def executar(self, repo: GastoRepository) -> List[Gasto]:
        return repo.buscar_por_criterio(
            'data_gasto BETWEEN ? AND ?',
            (self.data_inicio, self.data_fim)
        )
    
class BuscaPorMesAno(BuscaStrategy):
    def __init__(self, mes_ano: str):
        self.mes_ano = mes_ano

    def executar(self, repo: GastoRepository) -> List[Gasto]:
        return repo.buscar_por_criterio(
            "strftime('%Y-%m', data_gasto) = ?",
            (self.mes_ano,)
        )
    
# ==================== CAMADA DE VISUALIZAÇÃO ====================

class GastoView:
    """Responsável pela apresentação dos dados"""

    @staticmethod
    def limpar_tela() -> None:
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def exibir_cabecalho(titulo: str) -> None:
        print("\n" + "="*50)
        print(titulo)
        print("="*50)

    @staticmethod
    def exibir_lista_gastos(gastos: List[Gasto]) -> None:
        if not gastos:
            print("Nenhum gasto registrado.")
            return
        
        print(f"\n{'ID':<5} {'Descrição':<30} {'Valor':<12} {'Data'}")
        print("-" * 70)
       
        total = sum(g.gasto for g in gastos)
    
        for gasto in gastos:
            print(f"{gasto.id:<5} {gasto.descricao:<30} R$ {gasto.gasto:>8.2f} {gasto.data_gasto}")
        
        print("-" * 70)
        print(f"{'TOTAL:':<37} R$ {total:>8.2f}\n")

    @staticmethod
    def exibir_estatisticas(stats: Dict) -> None:
        if stats.get('total_registros', 0) == 0:
            print("📭 Nenhum gasto cadastrado para calcular estatísticas.")
            return
        
        print(f"\n📊 Total de gastos: {stats['total_registros']}")
        print(f"💰 Soma total: R$ {stats['soma_total']:.2f}")
        print(f"📈 Média: R$ {stats['media']:.2f}")
        print(f"⬆️  Maior: R$ {stats['maior_gasto']['valor']:.2f} ({stats['maior_gasto']['descricao']})")
        print(f"⬇️  Menor: R$ {stats['menor_gasto']['valor']:.2f} ({stats['menor_gasto']['descricao']})")
        
        print("\n📅 Gastos por mês:")
        print(f"{'Mês':<10} {'Quantidade':<12} {'Total'}")
        print("-" * 40)

        for mes in stats['por_mes']:
            print(f"{mes[0]:<10} {mes[1]:<12} R$ {mes[2]:>8.2f}")
    
    @staticmethod
    def solicitar_input(mensagem: str) -> str:
        return input(mensagem).strip()
    
    @staticmethod
    def aguardar_continuar() -> None:
        input("\nPressione Enter para continuar...")

# ==================== COMANDOS (Command Pattern) ====================

class Command(ABC):
    """Interface para comandos do menu"""

    @abstractmethod
    def executar(self) -> None:
        pass

class InserirGastoCommand(Command):
    def __init__(self, repo: GastoRepository, view: GastoView):
        self.repo = repo
        self.view = view

    def executar(self) -> None:
        self.view.exibir_cabecalho("INSERIR NOVO GASTO")

        descricao = self.view.solicitar_input("Descrição: ")
        if not descricao:
            print("❌ Descrição não pode estar vazia!")
            return
        
        try:
            gasto_valor = float(self.view.solicitar_input("Valor (R$): "))
            if gasto_valor <= 0:
                print("❌ O valor deve ser maior que zero!")
                return
        except ValueError:
            print("❌ Valor inválido!")
            return
        
        data_gasto = self.view.solicitar_input("Data (YYYY-MM-DD) ou Enter para hoje: ")
        if not data_gasto:
            data_gasto = datetime.now().strftime("%Y-%m-%d")
        
        try:
            datetime.strptime(data_gasto, '%Y-%m-%d')
            gasto = Gasto(descricao=descricao, gasto=gasto_valor, data_gasto=data_gasto)
            novo_id = self.repo.inserir(gasto)
            print(f"✓ Gasto inserido com sucesso! ID: {novo_id}")
        except ValueError:
            print("❌ Formato de data inválido! Use YYYY-MM-DD")
        except sqlite3.Error as e:
            print(f"❌ Erro ao inserir: {e}")

class ListarGastosCommand(Command):
    def __init__(self, repo: GastoRepository, view: GastoView):
        self.repo = repo
        self.view = view

    def executar(self):
        self.view.exibir_cabecalho("LISTA DE GASTOS")
        gastos = self.repo.buscar_todos()
        self.view.exibir_lista_gastos(gastos)

class BuscarGastosCommand(Command):
    def __init__(self, repo: GastoRepository, view: GastoView):
        self.repo = repo
        self.view = view

        # Mapeamento de opções para estratégias
        self.estrategias: Dict[str, Callable[[], BuscaStrategy]] = {
            '1': self.criar_busca_descricao,
            '2': self.criar_busca_valor_minimo,
            '3': self.criar_busca_valor_maximo,
            '4': self.criar_busca_periodo,
            '5': self.criar_busca_mes_ano
        }
    
    def executar(self) -> None:
        self.view.exibir_cabecalho("BUSCAR GASTOS")
        print("1. Por descrição")
        print("2. Por valor mínimo")
        print("3. Por valor máximo")
        print("4. Por período")
        print("5. Por mês/ano")

        opcao = self.view.solicitar_input("\nEscolha: ")

        estrategia_factory = self.estrategias.get(opcao)
        if not estrategia_factory:
            print("❌ Opção inválida!")
            return
        
        try:
            estrategia = estrategia_factory()
            gastos = estrategia.executar(self.repo)
            self.view.exibir_lista_gastos(gastos)
        except Exception as e:
            print(f"❌ Erro na busca: {e}")
    
    def criar_busca_descricao(self) -> BuscaStrategy:
        termo = self.view.solicitar_input("Digite parte da descrição: ")
        return BuscaPorDescricao(termo)
    
    def criar_busca_valor_minimo(self) -> BuscaStrategy:
        valor = float(self.view.solicitar_input("Valor mínimo (R$): "))
        return BuscaPorValorMinimo(valor)
    
    def criar_busca_valor_maximo(self) -> BuscaStrategy:
        valor = float(self.view.solicitar_input("Valor máximo (R$): "))
        return BuscaPorValorMaximo(valor)
    
    def criar_busca_periodo(self) -> BuscaStrategy:
        inicio = self.view.solicitar_input("Data inicial (YYYY-MM-DD): ")
        fim = self.view.solicitar_input("Data final (YYYY-MM-DD): ")
        return BuscaPorPeriodo(inicio, fim)
    
    def criar_busca_mes_ano(self) -> BuscaStrategy:
        mes_ano = self.view.solicitar_input("Mês/Ano (YYYY-MM): ")
        return BuscaPorMesAno(mes_ano)
    
class AtualizarGastoCommand(Command):
    def __init__(self, repo: GastoRepository, view: GastoView):
        self.repo = repo
        self.view = view

        # Mapeamento de opções para métodos de atualização
        self.atualizadores: Dict[str, Callable[[Gasto], None]] = {
            '1': self.atualizar_descricao,
            '2': self.atualizar_valor,
            '3': self.atualizar_data,
            '4': self.atualizar_tudo
        }
    

    def executar(self) -> None:
        self.view.exibir_cabecalho("ATUALIZAR GASTO")

        try:
            id_gasto = int(self.view.solicitar_input("ID do gasto: "))
            gasto = self.repo.buscar_por_id(id_gasto)
            if not gasto:
                print(f"❌ Gasto ID {id_gasto} não encontrado!")
                return
            
            print(f"\nGasto atual: {gasto}")
            print("\nO que atualizar?")
            print("1. Descrição")
            print("2. Valor")
            print("3. Data")
            print("4. Todos os campos")

            opcao = self.view.solicitar_input("\nEscolha: ")
        


