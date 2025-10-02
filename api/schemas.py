from pydantic import BaseModel, Field

class FilmeCriar(BaseModel):
    titulo: str = Field(..., max_length=200)
    genero: str = Field(..., max_length=100)

class UsuarioCriar(BaseModel):
    nome: str = Field(..., max_length=100)
    idade: int = Field(..., ge=0, le=120)
    pais: str = Field(..., max_length=100)

class AvaliacaoCriar(BaseModel):
    filme_id: int
    usuario_id: int
    nota: float = Field(..., ge=0, le=10)
    comentario: str | None = None

class FilmeLer(BaseModel):
    id: int
    titulo: str
    genero: str
    class Config:
        from_attributes = True

class UsuarioLer(BaseModel):
    id: int
    nome: str
    idade: int
    pais: str
    class Config:
        from_attributes = True

class AvaliacaoLer(BaseModel):
    id: int
    filme_id: int
    usuario_id: int
    nota: float
    comentario: str | None = None
    class Config:
        from_attributes = True

class AvaliacaoLerDetalhada(BaseModel):
    id: int
    filme_id: int
    usuario_id: int
    nota: float
    comentario: str | None = None
    nome_filme: str
    nome_usuario: str
    idade_usuario: int