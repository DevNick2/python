# Guia de Implementação — Endpoint de Lançamentos (Transactions)

> Guia técnico de aprendizado Python para devs com background em PHP/Node.js.
> Cada tarefa tem o **código a escrever**, o **porquê** e os **conceitos Python** explicados.

---

## Visão Geral do que você vai construir

```
GET    /transactions          → lista lançamentos do usuário
POST   /transactions          → cria um novo lançamento
PATCH  /transactions/{code}/pay → marca como pago
PUT    /transactions/{code}   → atualiza um lançamento
DELETE /transactions/{code}   → remove (soft delete)
```

**Arquivos que você vai criar** (em ordem):

```
src/schemas/transactions.py                     ← Tarefa 1
db/migrations.py                                ← Tarefa 2 (editar)
src/repository/transaction_repository.py        ← Tarefa 3
src/modules/transactions/dtos.py                ← Tarefa 4
src/modules/transactions/transactions_service.py ← Tarefa 5
src/modules/transactions/transactions_controller.py ← Tarefa 6
src/modules/transactions/__init__.py            ← Tarefa 7
src/shared/services/di_services.py              ← Tarefa 8 (editar)
src/http/routes.py                              ← Tarefa 9 (editar)
main.py                                         ← Tarefa 10 (editar)
```

---

## Tarefa 1 — Schema ORM: `src/schemas/transactions.py`

> **O que é**: O "Model" do banco de dados. No Laravel seria um Eloquent Model; no Sequelize/TypeORM, uma Entity.

### Crie o arquivo `src/schemas/transactions.py`:

```python
from __future__ import annotations

from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, Numeric, Boolean, Date, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseSchema

if TYPE_CHECKING:
    from .users import UserSchema
    from .categories import CategorySchema


class TransactionType(PyEnum):
    INCOME = "income"
    EXPENSE = "expense"


class TransactionSchema(BaseSchema):
    __tablename__ = "transactions"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType, name="transaction_type", native_enum=True),
        nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[str] = mapped_column(Date, nullable=False)
    is_paid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Chaves estrangeiras
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )

    # Relacionamentos
    user: Mapped["UserSchema"] = relationship(back_populates="transactions")
    category: Mapped["CategorySchema | None"] = relationship(
        back_populates="transactions"
    )
```

### 📘 Conceitos Python desta tarefa

**`from __future__ import annotations`**
Permite usar tipos em strings (lazy evaluation) — necessário para referências circulares entre
arquivos. No Node.js você resolveria isso com `import type` do TypeScript.

**`from enum import Enum as PyEnum`**
Python tem Enum nativo. O `as PyEnum` é um alias — aqui evita conflito com o `Enum` do SQLAlchemy
que também é importado. É o equivalente a `import { Enum } from 'sqlalchemy'` e renomear.

**`class TransactionType(PyEnum):`**
Herança simples: `TransactionType` herda de `PyEnum`. Em Python, herança é declarada nos
parênteses da `class`. Equivale ao `extends` do JS/PHP.

**`TYPE_CHECKING` e `if TYPE_CHECKING:`**
Este bloco só é executado pelo type checker (ex: mypy/pyright), **nunca em runtime**.
Serve para importar tipos sem criar dependência circular em execução. É uma solução elegante
do Python para o problema de imports circulares entre schemas relacionados.

**`Mapped[str | None]`**
Type hint do SQLAlchemy 2.x. `str | None` é "union type" — o campo pode ser `str` ou `None`.
No TypeScript seria `string | null`. O `|` como union type foi introduzido no Python 3.10.

**`mapped_column(...)`**
Define as propriedades da coluna no banco. Equivale ao `@Column()` do TypeORM.

---

## Tarefa 2 — Migration: editar [db/migrations.py](file:///home/nick/projetos/projeto_financeiro/api/db/migrations.py)

> **O que é**: Cria as tabelas no banco. Aqui não é Alembic (migrations versionadas) — é um script simples que usa o SQLAlchemy para criar tudo que estiver mapeado.

### Adicione o import do novo schema (junto com os outros imports já existentes):

```python
from src.schemas.categories import CategorySchema
from src.schemas.users import UserSchema
from src.schemas.transactions import TransactionSchema  # ← adicionar esta linha
```

> O script já chama `Base.metadata.create_all(bind=engine)` que pega **todos** os schemas
> registrados automaticamente. Basta importar `TransactionSchema` para ele ser incluído.

### Também atualize [src/schemas/users.py](file:///home/nick/projetos/projeto_financeiro/api/src/schemas/users.py) — adicionar o relacionamento com transactions:

No final do arquivo [src/schemas/users.py](file:///home/nick/projetos/projeto_financeiro/api/src/schemas/users.py), adicione na lista de imports do `TYPE_CHECKING`:

```python
if TYPE_CHECKING:
    from .categories import CategorySchema
    from .transactions import TransactionSchema  # ← adicionar
```

E adicione o relacionamento dentro da classe [UserSchema](file:///home/nick/projetos/projeto_financeiro/api/src/schemas/users.py#18-42) (após `categories`):

```python
    # One(Users) to Many(Transactions)
    transactions: Mapped[List["TransactionSchema"]] = relationship(back_populates="user")
```

### Também atualize [src/schemas/categories.py](file:///home/nick/projetos/projeto_financeiro/api/src/schemas/categories.py) — adicionar o relacionamento:

No final do arquivo [src/schemas/categories.py](file:///home/nick/projetos/projeto_financeiro/api/src/schemas/categories.py), adicione o import:

```python
if TYPE_CHECKING:
    from .users import UserSchema
    from .transactions import TransactionSchema  # ← adicionar
```

E o relacionamento dentro de [CategorySchema](file:///home/nick/projetos/projeto_financeiro/api/src/schemas/categories.py#12-30):

```python
    # One(Category) to Many(Transactions)
    transactions: Mapped[List["TransactionSchema"]] = relationship(back_populates="category")
```

> Você precisará adicionar o import de `List` no topo: `from typing import TYPE_CHECKING, List`

### Para rodar a migration:

```bash
make run-migrations
```

### 📘 Conceitos Python desta tarefa

**Por que só importar já funciona?**
O `Base.metadata` do SQLAlchemy é um objeto global que rastreia todos os schemas que herdam
de [Base](file:///home/nick/projetos/projeto_financeiro/api/src/schemas/base.py#11-13). Quando você faz `from src.schemas.transactions import TransactionSchema`, o Python
executa o arquivo e a classe `TransactionSchema(BaseSchema)` se registra automaticamente no
`Base.metadata`. É um pattern de "registro automático por herança" — o `create_all()` depois
percorre todos os registrados.

**`List["TransactionSchema"]`**
As aspas em `"TransactionSchema"` fazem o tipo ser avaliado como string (forward reference).
Sem `from __future__ import annotations`, você precisaria das aspas sempre que referenciasse
um tipo ainda não definido no momento da leitura do arquivo.

---

## Tarefa 3 — Repository: `src/repository/transaction_repository.py`

> **O que é**: Camada de acesso ao banco. Só faz queries. Nada de regras de negócio aqui.
> Equivale ao Repository do Laravel ou ao DAO pattern.

### Crie o arquivo `src/repository/transaction_repository.py`:

```python
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from datetime import datetime, timezone

from src.schemas.transactions import TransactionSchema


class TransactionRepository:
    def __init__(self, db_session: Session):
        self.session = db_session()

    def find_all_by_user(self, user_id: int) -> list[TransactionSchema]:
        result = self.session.execute(
            select(TransactionSchema)
            .where(TransactionSchema.user_id == user_id)
            .where(TransactionSchema.deleted_at == None)  # noqa: E711
            .order_by(TransactionSchema.due_date.desc())
        ).scalars().all()
        return list(result)

    def find_by_code_and_user(
        self, code: UUID, user_id: int
    ) -> TransactionSchema | None:
        return self.session.execute(
            select(TransactionSchema)
            .where(TransactionSchema.code == code)
            .where(TransactionSchema.user_id == user_id)
            .where(TransactionSchema.deleted_at == None)  # noqa: E711
        ).scalar_one_or_none()

    def create(self, data: dict) -> TransactionSchema:
        transaction = TransactionSchema(**data)
        self.session.add(transaction)
        self.session.commit()
        self.session.refresh(transaction)
        return transaction

    def save(self, transaction: TransactionSchema) -> TransactionSchema:
        self.session.add(transaction)
        self.session.commit()
        self.session.refresh(transaction)
        return transaction

    def soft_delete(self, transaction: TransactionSchema) -> None:
        transaction.deleted_at = datetime.now(timezone.utc)
        self.session.commit()
```

### 📘 Conceitos Python desta tarefa

**`def __init__(self, db_session: Session):`**
O construtor da classe. `self` é o equivalente do `this` no JS/PHP — mas em Python é
**explícito** em todos os métodos. É uma característica marcante da linguagem.

**`-> list[TransactionSchema]`**
Return type annotation. É o equivalente do `: TransactionSchema[]` do TypeScript. Em Python,
os type hints são **opcionais em runtime** mas fundamentais para legibilidade e ferramentas.
`list[X]` (minúsculo) funciona a partir do Python 3.9. Antes usava-se `List[X]` do `typing`.

**`-> TransactionSchema | None`**
Union type como return type. Equivale a `TransactionSchema | null` do TypeScript. O
`scalar_one_or_none()` do SQLAlchemy retorna o objeto ou `None` se não encontrar — nunca lança
exceção. (Existe também `scalar_one()` que lança exceção se não encontrar, e `scalars().all()`
que retorna uma lista).

**`TransactionSchema(**data)`**
O `**` (double star / double splat) desempacota um dicionário como `keyword arguments`.
Se `data = {"title": "Aluguel", "amount": 1200.0}`, então
`TransactionSchema(**data)` equivale a `TransactionSchema(title="Aluguel", amount=1200.0)`.
No JS seria equivalente ao spread: `new TransactionSchema({...data})`.

**[list(result)](file:///home/nick/projetos/projeto_financeiro/api/src/modules/users/users_controller.py#11-21)**
`scalars().all()` retorna um objeto do tipo `ScalarResult` do SQLAlchemy, não uma [list](file:///home/nick/projetos/projeto_financeiro/api/src/modules/users/users_controller.py#11-21)
Python pura. Envolver com [list()](file:///home/nick/projetos/projeto_financeiro/api/src/modules/users/users_controller.py#11-21) converte para lista Python. É um padrão comum — em Python
muitas funções retornam "iterables" lazy que precisam ser materializados com [list()](file:///home/nick/projetos/projeto_financeiro/api/src/modules/users/users_controller.py#11-21).

**`# noqa: E711`**
Instrução para o `flake8` ignorar esse aviso específico nessa linha. O flake8 reclama de
comparações com `None` usando `==` (sugere `is None`), mas no SQLAlchemy a comparação com
`== None` tem semântica especial (gera `IS NULL` no SQL). O `noqa` suprime o falso positivo.

**`datetime.now(timezone.utc)`**
Gera datetime com timezone UTC. Sempre use `timezone.utc` ao criar datetimes — evita bugs
com horário local vs UTC. No JS seria `new Date()` (UTC por padrão).

---

## Tarefa 4 — DTOs: `src/modules/transactions/dtos.py`

> **O que é**: Define o "contrato" da API — o que entra e o que sai. O Pydantic valida
> automaticamente os dados. Equivale aos DTOs do NestJS ou Form Requests do Laravel.

### Crie o arquivo `src/modules/transactions/dtos.py`:

```python
from pydantic import BaseModel, field_validator
from uuid import UUID
from datetime import date, datetime
from enum import Enum


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


# ---------------------------------------------------------------------------
# DTOs de Input (Request)
# ---------------------------------------------------------------------------

class CreateTransactionDTO(BaseModel):
    title: str
    amount: float
    type: TransactionType
    due_date: date
    category_code: UUID | None = None
    description: str | None = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("O valor deve ser maior que zero")
        return value

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("O título não pode ser vazio")
        return value.strip()


class UpdateTransactionDTO(BaseModel):
    title: str | None = None
    amount: float | None = None
    type: TransactionType | None = None
    due_date: date | None = None
    category_code: UUID | None = None
    description: str | None = None

    @field_validator("amount", mode="before")
    @classmethod
    def amount_must_be_positive(cls, value: float | None) -> float | None:
        if value is not None and value <= 0:
            raise ValueError("O valor deve ser maior que zero")
        return value


# ---------------------------------------------------------------------------
# DTOs de Output (Response)
# ---------------------------------------------------------------------------

class TransactionResponse(BaseModel):
    code: UUID
    title: str
    amount: float
    type: TransactionType
    description: str | None
    due_date: date
    is_paid: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

### 📘 Conceitos Python desta tarefa

**`class TransactionType(str, Enum):`**
Herança múltipla — `TransactionType` herda de `str` E de `Enum` ao mesmo tempo. Isso faz com
que os valores do Enum sejam também strings (`"income"`, `"expense"`), permitindo serialização
direta em JSON sem conversão. Compare com o `Enum` do schema ORM que é `PyEnum` (não `str`).

**`= None` como valor padrão**
Campos com valor padrão são opcionais. Em Pydantic v2, `UUID | None = None` significa
"campo opcional, padrão None". Sem o `= None`, o campo seria obrigatório. Equivalente ao
`?` do TypeScript: `categoryCode?: string`.

**`@field_validator("amount")` e `@classmethod`**
São decorators — modificam o comportamento da função abaixo deles. `@field_validator` é
do Pydantic e registra uma função como validador de um campo. `@classmethod` é nativo do
Python e indica que o primeiro parâmetro é a classe (`cls`) em vez da instância (`self`).
Equivale ao método estático de validação no Laravel (`Rule::...`).

**`mode="before"`**
Executa o validator **antes** da conversão de tipo do Pydantic. Útil quando o campo pode
vir como `None` e você quer evitar que o validator rode nesse caso.

**`model_config = {"from_attributes": True}`**
Configuração do Pydantic v2 que permite criar um response model a partir de um objeto ORM
(que usa atributos Python) em vez de um dicionário. Sem isso, `TransactionResponse.model_validate(orm_object)` falharia. É o equivalente ao `plainToClass` do `class-transformer` do NestJS.

**`value.strip()`**
Remove espaços em branco do início e fim da string. Equivale ao `.trim()` do JS/PHP.

---

## Tarefa 5 — Service: `src/modules/transactions/transactions_service.py`

> **O que é**: As regras de negócio. Orquestra o repository. Não faz queries diretamente.

### Crie o arquivo `src/modules/transactions/transactions_service.py`:

```python
from uuid import UUID
from fastapi import HTTPException, status

from src.repository.transaction_repository import TransactionRepository
from src.repository.user_repository import UserRepository
from src.shared.utils.logger import logger
from src.schemas.transactions import TransactionType as SchemaTransactionType

from .dtos import CreateTransactionDTO, UpdateTransactionDTO, TransactionResponse


class TransactionsService:
    def __init__(self, repository: TransactionRepository, user_repository: UserRepository):
        self.repository = repository
        self.user_repository = user_repository

    def find_all(self, user_code: str) -> list[TransactionResponse]:
        user = self._get_user_or_404(user_code)
        transactions = self.repository.find_all_by_user(user.id)
        return [TransactionResponse.model_validate(t) for t in transactions]

    def create(self, user_code: str, data: CreateTransactionDTO) -> TransactionResponse:
        user = self._get_user_or_404(user_code)

        try:
            transaction = self.repository.create({
                "title": data.title,
                "amount": float(data.amount),
                "type": SchemaTransactionType(data.type.value),
                "due_date": data.due_date,
                "description": data.description,
                "user_id": user.id,
            })
            return TransactionResponse.model_validate(transaction)
        except Exception as e:
            logger.error(f"Erro ao criar transação: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao criar lançamento"
            )

    def mark_as_paid(self, user_code: str, transaction_code: UUID) -> TransactionResponse:
        user = self._get_user_or_404(user_code)
        transaction = self._get_transaction_or_404(transaction_code, user.id)

        transaction.is_paid = True
        updated = self.repository.save(transaction)
        return TransactionResponse.model_validate(updated)

    def update(
        self, user_code: str, transaction_code: UUID, data: UpdateTransactionDTO
    ) -> TransactionResponse:
        user = self._get_user_or_404(user_code)
        transaction = self._get_transaction_or_404(transaction_code, user.id)

        # Atualiza somente os campos enviados (partial update)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "type" and value is not None:
                value = SchemaTransactionType(value.value if hasattr(value, "value") else value)
            setattr(transaction, field, value)

        updated = self.repository.save(transaction)
        return TransactionResponse.model_validate(updated)

    def remove(self, user_code: str, transaction_code: UUID) -> None:
        user = self._get_user_or_404(user_code)
        transaction = self._get_transaction_or_404(transaction_code, user.id)
        self.repository.soft_delete(transaction)

    # ---------------------------------------------------------------------------
    # Métodos privados (convenção: prefixo _)
    # ---------------------------------------------------------------------------

    def _get_user_or_404(self, user_code: str):
        user = self.user_repository.find_by_code(user_code)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        return user

    def _get_transaction_or_404(self, code: UUID, user_id: int):
        transaction = self.repository.find_by_code_and_user(code, user_id)
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lançamento não encontrado"
            )
        return transaction
```

### 📘 Conceitos Python desta tarefa

**`[TransactionResponse.model_validate(t) for t in transactions]`**
List comprehension — cria uma nova lista aplicando uma transformação a cada item de um
iterável. Equivale ao `.map()` do JavaScript:
```js
// JS
transactions.map(t => TransactionResponse.from(t))
// Python
[TransactionResponse.model_validate(t) for t in transactions]
```
É uma das features mais usadas e idiomáticas do Python. Memorize esse padrão.

**`data.model_dump(exclude_unset=True)`**
Converte o DTO Pydantic em dicionário, **excluindo campos não enviados** na requisição.
Fundamental para PATCH parcial: se o cliente não enviou `title`, ele não aparece no dict
e não sobrescreve o valor existente. Equivale ao `...spread` condicional do JS ou ao
`array_filter` do PHP.

**`for field, value in update_data.items():`**
Itera sobre o dicionário obtendo chave e valor ao mesmo tempo. `.items()` retorna pares
[(chave, valor)](file:///home/nick/projetos/projeto_financeiro/api/src/modules/auth/auth_controller.py#39-50). O "unpacking" automático `field, value =` é chamado de **tuple unpacking**.
Equivale ao `Object.entries(obj).forEach(([field, value]) => ...)` do JS.

**`setattr(transaction, field, value)`**
Define dinamicamente um atributo de um objeto. Equivale ao `obj[field] = value` do JS
ou ao `$obj->$field = $value` do PHP. Em Python, acesso a atributos com nome dinâmico
requer `setattr`/`getattr` porque a notação de ponto (`obj.field`) não aceita variáveis.

**`def _get_user_or_404(self, ...):` — prefixo `_`**
Convenção Python para "método privado/interno". Não é privado de verdade (Python não tem
`private`), mas o underscore sinaliza para outros devs que o método é de uso interno. Equivale
ao `private` do PHP/Java como *convenção social*, não como regra do compilador.

**`SchemaTransactionType(data.type.value)`**
Converte o Enum do DTO (`dtos.TransactionType`) para o Enum do schema ORM
(`schemas.transactions.TransactionType`). São dois Enums diferentes com os mesmos valores —
o DTO é Pydantic, o Schema é SQLAlchemy. A conversão é necessária porque o SQLAlchemy espera
seu próprio tipo de Enum ao salvar no banco.

---

## Tarefa 6 — Controller: `src/modules/transactions/transactions_controller.py`

> **O que é**: Define as rotas HTTP. Recebe a requisição, chama o service, retorna a resposta.
> Equivale ao Controller do Laravel ou ao Controller do NestJS.

### Crie o arquivo `src/modules/transactions/transactions_controller.py`:

```python
from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import Provide, inject
from uuid import UUID

from src.shared.services.di_services import ContainerService
from src.shared.utils.auth import get_current_user
from src.modules.transactions.transactions_service import TransactionsService
from .dtos import CreateTransactionDTO, UpdateTransactionDTO, TransactionResponse

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get(
    "/",
    response_model=list[TransactionResponse],
    summary="Lista todos os lançamentos do usuário autenticado"
)
@inject
async def list_transactions(
    current_user: dict = Depends(get_current_user),
    service: TransactionsService = Depends(Provide[ContainerService.transactions_service])
):
    return service.find_all(current_user["sub"])


@router.post(
    "/",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um novo lançamento"
)
@inject
async def create_transaction(
    body: CreateTransactionDTO,
    current_user: dict = Depends(get_current_user),
    service: TransactionsService = Depends(Provide[ContainerService.transactions_service])
):
    return service.create(current_user["sub"], body)


@router.patch(
    "/{code}/pay",
    response_model=TransactionResponse,
    summary="Marca um lançamento como pago"
)
@inject
async def pay_transaction(
    code: UUID,
    current_user: dict = Depends(get_current_user),
    service: TransactionsService = Depends(Provide[ContainerService.transactions_service])
):
    return service.mark_as_paid(current_user["sub"], code)


@router.put(
    "/{code}",
    response_model=TransactionResponse,
    summary="Atualiza um lançamento"
)
@inject
async def update_transaction(
    code: UUID,
    body: UpdateTransactionDTO,
    current_user: dict = Depends(get_current_user),
    service: TransactionsService = Depends(Provide[ContainerService.transactions_service])
):
    return service.update(current_user["sub"], code, body)


@router.delete(
    "/{code}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove um lançamento (soft delete)"
)
@inject
async def delete_transaction(
    code: UUID,
    current_user: dict = Depends(get_current_user),
    service: TransactionsService = Depends(Provide[ContainerService.transactions_service])
):
    service.remove(current_user["sub"], code)
```

### 📘 Conceitos Python desta tarefa

**`@router.get("/", ...)` — Decorators**
Decorators são funções que "envolvem" outra função, adicionando comportamento. O `@router.get`
registra a função abaixo como handler da rota `GET /transactions/`. Em Python, decorators são
declarados com `@` acima da função — é mais limpo que o equivalente Node/Express:
```js
// Express
router.get('/', handler)

// FastAPI
@router.get('/')
async def handler():
```

**`async def` vs `def`**
Python suporta funções assíncronas com `async/await`, igual ao JavaScript. O FastAPI pode lidar
com ambas (`def` síncrono e `async def` assíncrono). Use `async def` quando fizer I/O (banco,
HTTP). Na prática, o FastAPI executa funções `def` em uma thread pool automática, então ambas
funcionam bem aqui.

**`code: UUID`** no parâmetro da rota
FastAPI converte automaticamente o path param `{code}` para o tipo anotado (`UUID`). Se o
cliente enviar um valor que não é UUID válido, o FastAPI retorna 422 automaticamente. Isso é
feito via Pydantic nos bastidores. Equivale ao `@Param('code', ParseUUIDPipe)` do NestJS.

**`Depends(get_current_user)`**
O sistema de Dependency Injection do FastAPI. Quando o FastAPI processa a rota, chama
[get_current_user](file:///home/nick/projetos/projeto_financeiro/api/src/shared/utils/auth.py#89-116) automaticamente e injeta o resultado como [current_user](file:///home/nick/projetos/projeto_financeiro/api/src/shared/utils/auth.py#89-116). Ao contrário
do NestJS (que usa decorators de classe), o FastAPI usa `Depends()` como valores padrão de
parâmetro — uma solução elegante e pythônica.

**`Depends(Provide[ContainerService.transactions_service])`**
Combinação de dois sistemas de DI: o `Provide` do `dependency-injector` e o `Depends` do
FastAPI. O `Provide` resolve a dependência do container IoC e o `Depends` injeta via FastAPI.
O decorator `@inject` (do `dependency-injector`) é necessário para o `Provide` funcionar.

**`status.HTTP_201_CREATED`**
`status` é um módulo do FastAPI com constantes HTTP nomeadas. Equivale ao `HttpStatus.CREATED`
do NestJS. Usar constantes nomeadas é uma boa prática — evita "magic numbers" no código.

---

## Tarefa 7 — [__init__.py](file:///home/nick/projetos/projeto_financeiro/api/src/repository/__init__.py): `src/modules/transactions/__init__.py`

> **O que é**: Marca o diretório como um "pacote Python" (package). Sem ele, outros arquivos
> não conseguem importar de dentro deste diretório.

### Crie o arquivo vazio `src/modules/transactions/__init__.py`:

```
(arquivo vazio)
```

### 📘 Conceitos Python desta tarefa

**[__init__.py](file:///home/nick/projetos/projeto_financeiro/api/src/repository/__init__.py)**
O equivalente ao `index.js` de um módulo Node.js, mas para marcar um diretório como importável.
Em Python, qualquer diretório com um [__init__.py](file:///home/nick/projetos/projeto_financeiro/api/src/repository/__init__.py) vira um "package" e pode ser importado.
Sem ele, `from src.modules.transactions.transactions_service import TransactionsService`
falharia com `ModuleNotFoundError`.

A partir do Python 3.3 existem "namespace packages" (sem [__init__.py](file:///home/nick/projetos/projeto_financeiro/api/src/repository/__init__.py)), mas é boa prática
sempre criar o arquivo — especialmente com ferramentas como `dependency-injector` que fazem
wiring de módulos por string.

---

## Tarefa 8 — DI Container: editar [src/shared/services/di_services.py](file:///home/nick/projetos/projeto_financeiro/api/src/shared/services/di_services.py)

> **O que é**: Registrar o novo repository e service no container de injeção de dependência.
> Equivale a registrar um Provider no módulo do NestJS.

### Adicione os imports e os novos providers:

```python
from dependency_injector import containers, providers
from sqlalchemy.orm import sessionmaker

from src.repository.user_repository import UserRepository
from src.repository.transaction_repository import TransactionRepository  # ← NOVO
from src.modules.auth.auth_service import AuthService
from src.modules.transactions.transactions_service import TransactionsService  # ← NOVO

from .postgres_services import PostgresServices


class ContainerService(containers.DeclarativeContainer):
    config = providers.Configuration()

    # ---------------------------------------------------------------------------
    # Banco de dados (não alterar)
    # ---------------------------------------------------------------------------
    db_service = providers.Singleton(
        PostgresServices,
        dbname=config.db.dbname,
        port=config.db.port,
        host=config.db.host,
        user=config.db.user,
        password=config.db.password
    )

    engine = providers.Singleton(
        lambda postgresService: postgresService.connection(), db_service
    )

    session_factory = providers.Singleton(
        sessionmaker,
        bind=engine,
        autoflush=True,
        expire_on_commit=False
    )

    db = providers.Factory(session_factory)

    # ---------------------------------------------------------------------------
    # Repositories
    # ---------------------------------------------------------------------------
    userRepository = providers.Singleton(UserRepository, dbSession=db)

    transaction_repository = providers.Singleton(  # ← NOVO
        TransactionRepository, db_session=db
    )

    # ---------------------------------------------------------------------------
    # Services
    # ---------------------------------------------------------------------------
    auth_service = providers.Singleton(AuthService, repository=userRepository)

    transactions_service = providers.Singleton(  # ← NOVO
        TransactionsService,
        repository=transaction_repository,
        user_repository=userRepository
    )
```

### 📘 Conceitos Python desta tarefa

**`providers.Singleton` vs `providers.Factory`**
- `Singleton`: cria **uma única instância** e reutiliza em todas as injeções. Ideal para
  services e repositories (stateless, criados uma vez).
- `Factory`: cria **uma nova instância** a cada injeção. O [db](file:///home/nick/projetos/projeto_financeiro/api/src/modules/health/health_controller.py#17-33) é Factory porque cada request
  deve ter sua própria Session de banco — diferente das outras dependências.

**Injeção por nome de parâmetro**
`providers.Singleton(TransactionsService, repository=transaction_repository, user_repository=userRepository)`
Os nomes `repository` e `user_repository` devem bater **exatamente** com os parâmetros do
[__init__](file:///home/nick/projetos/projeto_financeiro/api/src/modules/auth/auth_service.py#16-18) do `TransactionsService`. O container resolve automaticamente pela assinatura do
construtor. É o mesmo princípio do DI do Spring (Java) ou do Container do Laravel.

---

## Tarefa 9 — Aggregator: editar [src/http/routes.py](file:///home/nick/projetos/projeto_financeiro/api/src/http/routes.py)

### Adicione o import e o include do router de transactions:

```python
from fastapi import APIRouter

from src.modules.health.health_controller import router as health_router
from src.modules.users.users_controller import router as users_router
from src.modules.auth.auth_controller import router as auth_router
from src.modules.transactions.transactions_controller import router as transactions_router  # ← NOVO

router = APIRouter()

router.include_router(health_router)
router.include_router(users_router)
router.include_router(auth_router)
router.include_router(transactions_router)  # ← NOVO
```

---

## Tarefa 10 — Wiring: editar [main.py](file:///home/nick/projetos/projeto_financeiro/api/main.py)

### Adicione o módulo transactions no `container.wire()`:

```python
container.wire(modules=[
    "src.http.routes",
    "src.modules.health.health_controller",
    "src.modules.users.users_controller",
    "src.modules.auth.auth_controller",
    "src.modules.transactions.transactions_controller",  # ← NOVO
])
```

### 📘 Conceitos Python desta tarefa

**Por que o `wire()` é necessário?**
O `@inject` e o `Provide[...]` funcionam via **monkey patching** — o `dependency-injector`
modifica o comportamento das funções em runtime substituindo os valores `Provide[...]` pelas
instâncias reais. O `container.wire(modules=[...])` diz ao container quais arquivos ele deve
"inspecionar e patchar". Se você não listar o módulo aqui, o `@inject` não vai funcionar
mesmo que o provider esteja registrado no container.

---

## Tarefa 11 — Rodar a migration e testar

### Passo 1: Rodar a migration

```bash
make run-migrations
```

### Passo 2: Verificar os endpoints no Swagger

Abra `http://localhost:3000/docs` — você verá a seção **Transactions** com todos os endpoints.

### Passo 3: Testar com curl

```bash
# Criar um lançamento
curl -X POST http://localhost:3000/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Aluguel",
    "amount": 1500.00,
    "type": "expense",
    "due_date": "2026-03-10"
  }'

# Listar lançamentos
curl http://localhost:3000/transactions

# Marcar como pago (substitua o UUID real)
curl -X PATCH http://localhost:3000/transactions/SEU-UUID-AQUI/pay

# Atualizar
curl -X PUT http://localhost:3000/transactions/SEU-UUID-AQUI \
  -H "Content-Type: application/json" \
  -d '{"title": "Aluguel Atualizado"}'

# Remover
curl -X DELETE http://localhost:3000/transactions/SEU-UUID-AQUI
```

> **Nota**: As rotas estão sem autenticação JWT por enquanto (a Fase 2 implementará o JWT
> completo). O [get_current_user](file:///home/nick/projetos/projeto_financeiro/api/src/shared/utils/auth.py#89-116) lançará erro até o JWT estar implementado. Para testar
> agora, comente temporariamente o `Depends(get_current_user)` e hardcode um `user_code`.

---

## Resumo — O que você aprendeu

| Conceito Python | Equivalente JS/PHP | Onde usou |
|---|---|---|
| `class Foo(Bar):` | `class Foo extends Bar` | Herança em schemas e enums |
| `self` explícito | `this` implícito | Todos os métodos |
| `Mapped[str \| None]` | `string \| null` (TS) | Type hints do SQLAlchemy |
| `**data` (dict unpack) | `{...data}` spread | Criar instâncias ORM |
| `[f(x) for x in list]` | `.map(x => f(x))` | Serializar listas |
| `data.items()` | `Object.entries(data)` | Iterar dicionários |
| `setattr(obj, k, v)` | `obj[k] = v` | Update parcial |
| `@decorator` | `@Decorator()` (NestJS) | Rotas FastAPI |
| [__init__.py](file:///home/nick/projetos/projeto_financeiro/api/src/repository/__init__.py) | `index.js` | Marcar diretórios como pacote |
| `_metodo_privado` | `private metodo()` | Convenção de privacidade |
| `async def` / `await` | `async function` / `await` | Funções assíncronas |
