from pydantic import BaseModel

class BaseConfig(BaseModel):
    
    _EMOJIS = {
        "GASTO_CRIADO":     "📥",
        "GASTO_ATUALIZADO": "✏️ ",
        "GASTO_REMOVIDO":   "🗑️ ",
    }

configs = BaseConfig()
