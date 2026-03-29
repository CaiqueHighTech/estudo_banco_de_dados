gastos_system/
│
├── domain/                               # Núcleo de negócio (sem dependências externas)
│   ├── value_objects.py                  # Valor, DataGasto, Descricao (imutáveis, auto-validantes)
│   ├── entities.py                       # Entidade Gasto com invariantes protegidas
│   └── exceptions.py                     # GastoNaoEncontradoError, RepositorioError
│
├── application/                          # Casos de uso e contratos
│   ├── dtos.py                           # CriarGastoDTO, AtualizarGastoDTO, GastoDTO, EstatisticasDTO
│   ├── interfaces/
│   │   └── i_gasto_repository.py         # IGastoRepository — contrato de persistência
│   └── services/
│       └── gasto_service.py              # GastoService — orquestra casos de uso (Facade)
│
├── infrastructure/                       # Implementações concretas (SQLAlchemy)
│   ├── orm/
│   │   ├── models.py                     # _GastoORM — modelo PRIVADO (prefixo _)
│   │   └── database.py                   # DatabaseSession — Singleton + context manager
│   └── repositories/
│       └── sqlalchemy_gasto_repository.py # Implementa IGastoRepository
│
├── presentation/                         # Interface com o usuário
│   ├── strategies/
│   │   └── busca_strategies.py           # IBuscaStrategy + 5 estratégias concretas
│   └── cli/
│       ├── view.py                       # GastoView — renderização (só recebe DTOs)
│       ├── commands.py                   # ICommand + 7 comandos concretos
│       └── controller.py                 # MenuController — loop principal
│
├── shared/
│   └── event_bus.py                      # EventBus (Observer) + LoggingHandler + AuditHandler
│
└── main.py                               # Composition Root — único ponto de wiring