from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Base, Filme, Usuario, Avaliacao
from schemas import (
    FilmeCriar, UsuarioCriar, AvaliacaoCriar, FilmeLer, UsuarioLer, AvaliacaoLer, AvaliacaoLerDetalhada
)
from database import motor, SessaoLocal
import asyncio
from sqlalchemy.exc import OperationalError

app = FastAPI()

async def obter_sessao():
    async with SessaoLocal() as sessao:
        yield sessao

@app.on_event("startup")
async def ao_iniciar():
    # Try to create tables, but wait for the DB to be reachable first.
    retries = 12
    for attempt in range(1, retries + 1):
        try:
            async with motor.begin() as conexao:
                await conexao.run_sync(Base.metadata.create_all)
            break
        except Exception as exc:
            # asyncpg raises connection errors that may not be OperationalError
            if attempt == retries:
                raise
            print(f"Database not ready ({exc!r}), retrying ({attempt}/{retries})...")
            await asyncio.sleep(2)


@app.get("/health")
async def health():
    return {"status": "ok"}

# Movies endpoints
@app.post("/movies/", response_model=FilmeLer, status_code=201)
async def criar_filme(filme: FilmeCriar, db: AsyncSession = Depends(obter_sessao)):
    novo_filme = Filme(**filme.dict())
    db.add(novo_filme)
    await db.commit()
    await db.refresh(novo_filme)
    return novo_filme

@app.get("/movies/", response_model=list[FilmeLer])
async def listar_filmes(db: AsyncSession = Depends(obter_sessao)):
    result = await db.execute(Filme.__table__.select())
    filmes = result.fetchall()
    return [FilmeLer.model_validate(row._mapping) for row in filmes]

# Users endpoints
@app.post("/users/", response_model=UsuarioLer, status_code=201)
async def criar_usuario(usuario: UsuarioCriar, db: AsyncSession = Depends(obter_sessao)):
    novo_usuario = Usuario(**usuario.dict())
    db.add(novo_usuario)
    await db.commit()
    await db.refresh(novo_usuario)
    return novo_usuario

@app.get("/users/", response_model=list[UsuarioLer])
async def listar_usuarios(db: AsyncSession = Depends(obter_sessao)):
    result = await db.execute(Usuario.__table__.select())
    usuarios = result.fetchall()
    return [UsuarioLer.model_validate(row._mapping) for row in usuarios]

# Ratings endpoints
@app.post("/ratings/", response_model=AvaliacaoLer, status_code=201)
async def criar_avaliacao(avaliacao: AvaliacaoCriar, db: AsyncSession = Depends(obter_sessao)):
    nova_avaliacao = Avaliacao(**avaliacao.dict())
    db.add(nova_avaliacao)
    await db.commit()
    await db.refresh(nova_avaliacao)
    return nova_avaliacao


@app.get("/ratings/", response_model=list[AvaliacaoLerDetalhada])
async def listar_avaliacoes(db: AsyncSession = Depends(obter_sessao)):
    stmt = (
        select(Avaliacao, Filme.titulo, Usuario.nome, Usuario.idade)
        .join(Filme, Avaliacao.filme_id == Filme.id)
        .join(Usuario, Avaliacao.usuario_id == Usuario.id)
    )
    result = await db.execute(stmt)
    avaliacoes = result.fetchall()
    return [
        AvaliacaoLerDetalhada(
            id=row.Avaliacao.id,
            filme_id=row.Avaliacao.filme_id,
            usuario_id=row.Avaliacao.usuario_id,
            nota=row.Avaliacao.nota,
            comentario=row.Avaliacao.comentario,
            nome_filme=row.titulo,
            nome_usuario=row.nome,
            idade_usuario=row.idade
        )
        for row in avaliacoes
    ]
