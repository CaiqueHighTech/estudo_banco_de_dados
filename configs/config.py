from pydantic import BaseModel, Field

class BaseConfig(BaseModel):
    
    _EMOJIS = {
        "GASTO_CRIADO":     "📥",
        "GASTO_ATUALIZADO": "✏️ ",
        "GASTO_REMOVIDO":   "🗑️ ",
    }
    largura: int = Field(default=54, gt=0,description="Largura da tabela de exibição.")

    MAX_LEN: str = Field(default="", max_length=255, description="Descrição não pode exceder 255 caracteres.")

configs = BaseConfig()
