import asyncio
import csv
import os
import logging

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from models import Base, Filme, Usuario, Avaliacao

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://movieuser:moviepass@localhost:5432/moviedb")
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

async def load_movies(session):
    with open(os.path.join(DATA_DIR, "movies.csv"), encoding="utf-8") as f:
        reader = csv.DictReader(f)
        async with session.begin():
            for row in reader:
                try:
                    movie = Filme(
                        id=int(row["id"]),
                        titulo=row["titulo"],
                        genero=row["genero"]
                    )
                    session.add(movie)
                except Exception as e:
                    logger.exception("Ignorando linha de filme devido ao erro: %s", e)

async def load_users(session):
    with open(os.path.join(DATA_DIR, "users.csv"), encoding="utf-8") as f:
        reader = csv.DictReader(f)
        async with session.begin():
            for row in reader:
                try:
                    user = Usuario(
                        id=int(row["id"]),
                        nome=row["nome"],
                        idade=int(row["idade"]),
                        pais=row["pais"]
                    )
                    session.add(user)
                except Exception as e:
                    logger.exception("Ignorando linha de usuário devido ao erro: %s", e)

async def load_ratings(session):
    with open(os.path.join(DATA_DIR, "ratings.csv"), encoding="utf-8") as f:
        reader = csv.DictReader(f)
        async with session.begin():
            for row in reader:
                try:
                    rating = Avaliacao(
                        id=int(row["id"]),
                        filme_id=int(row["filme_id"]),
                        usuario_id=int(row["usuario_id"]),
                        nota=float(row["nota"]),
                        comentario=row.get("comentario")
                    )
                    session.add(rating)
                except IntegrityError as ie:
                    logger.warning("Ignorando avaliação devido a erro de integridade: %s", ie)
                except Exception as e:
                    logger.exception("Ignorando linha de avaliação devido ao erro: %s", e)

async def main():
    view_names = [
        'top10_filmes_crime',
        'top10_filmes_acao',
        'top10_filmes_animacao',
        'media_nota_por_faixa_etaria',
        'quantidade_avaliacoes_por_pais'
    ]
    async with engine.begin() as conn:
        for view in view_names:
            try:
                await conn.execute(text(f"DROP VIEW IF EXISTS {view} CASCADE;"))
            except Exception as e:
                logger.warning("Não foi possível remover a view %s: %s", view, e)
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as session:
        logger.info("Carregando filmes...")
        await load_movies(session)
        logger.info("Carregando usuários...")
        await load_users(session)
        logger.info("Carregando avaliações...")
        await load_ratings(session)
        try:
            await session.execute(text("SELECT setval(pg_get_serial_sequence('movies','id'), COALESCE((SELECT MAX(id) FROM movies), 1), true);"))
            await session.execute(text("SELECT setval(pg_get_serial_sequence('users','id'), COALESCE((SELECT MAX(id) FROM users), 1), true);"))
            await session.execute(text("SELECT setval(pg_get_serial_sequence('ratings','id'), COALESCE((SELECT MAX(id) FROM ratings), 1), true);"))
        except Exception:
            logger.exception("Falha ao resetar sequências; se você não usou IDs explícitos isso pode ser desnecessário.")
        await session.execute(text('''
            CREATE OR REPLACE VIEW top10_filmes_crime AS
            SELECT f.titulo, f.genero, AVG(a.nota) AS media_nota
            FROM movies f
            JOIN ratings a ON a.filme_id = f.id
            WHERE f.genero = 'Crime'
            GROUP BY f.id, f.titulo, f.genero
            ORDER BY media_nota DESC
            LIMIT 10;
        '''))
        await session.execute(text('''
            CREATE OR REPLACE VIEW top10_filmes_acao AS
            SELECT f.titulo, f.genero, AVG(a.nota) AS media_nota
            FROM movies f
            JOIN ratings a ON a.filme_id = f.id
            WHERE f.genero = 'Ação'
            GROUP BY f.id, f.titulo, f.genero
            ORDER BY media_nota DESC
            LIMIT 10;
        '''))
        await session.execute(text('''
            CREATE OR REPLACE VIEW top10_filmes_animacao AS
            SELECT f.titulo, f.genero, AVG(a.nota) AS media_nota
            FROM movies f
            JOIN ratings a ON a.filme_id = f.id
            WHERE f.genero = 'Animação'
            GROUP BY f.id, f.titulo, f.genero
            ORDER BY media_nota DESC
            LIMIT 10;
        '''))
        await session.execute(text('''
            CREATE OR REPLACE VIEW media_nota_por_faixa_etaria AS
            SELECT
                CASE
                    WHEN u.idade BETWEEN 18 AND 20 THEN '18-20'
                    WHEN u.idade BETWEEN 21 AND 30 THEN '21-30'
                    WHEN u.idade BETWEEN 31 AND 40 THEN '31-40'
                    WHEN u.idade BETWEEN 41 AND 50 THEN '41-50'
                    WHEN u.idade BETWEEN 51 AND 60 THEN '51-60'
                    ELSE '61+'
                END AS faixa_etaria,
                AVG(a.nota) AS media_nota
            FROM users u
            JOIN ratings a ON a.usuario_id = u.id
            GROUP BY faixa_etaria
            ORDER BY faixa_etaria;
        '''))
        await session.execute(text('''
            CREATE OR REPLACE VIEW quantidade_avaliacoes_por_pais AS
            SELECT u.pais, COUNT(a.id) AS quantidade_avaliacoes
            FROM users u
            JOIN ratings a ON a.usuario_id = u.id
            GROUP BY u.pais
            ORDER BY quantidade_avaliacoes DESC;
        '''))
        await session.commit()

if __name__ == "__main__":
    asyncio.run(main())
