from sqlalchemy.orm import declarative_base, mapped_column, relationship
from sqlalchemy import Integer, String, Text, Float, ForeignKey

Base = declarative_base()

class Filme(Base):
    __tablename__ = "movies"
    id = mapped_column(Integer, primary_key=True, index=True)
    titulo = mapped_column(String(200), nullable=False, unique=True)
    genero = mapped_column(String(100), nullable=False)
    avaliacoes = relationship("Avaliacao", back_populates="filme")

class Usuario(Base):
    __tablename__ = "users"
    id = mapped_column(Integer, primary_key=True, index=True)
    nome = mapped_column(String(100), nullable=False, unique=True)
    idade = mapped_column(Integer, nullable=False)
    pais = mapped_column(String(100), nullable=False)
    avaliacoes = relationship("Avaliacao", back_populates="usuario")

class Avaliacao(Base):
    __tablename__ = "ratings"
    id = mapped_column(Integer, primary_key=True, index=True)
    filme_id = mapped_column(Integer, ForeignKey("movies.id"), nullable=False)
    usuario_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    nota = mapped_column(Float, nullable=False)
    comentario = mapped_column(Text, nullable=True)
    filme = relationship("Filme", back_populates="avaliacoes")
    usuario = relationship("Usuario", back_populates="avaliacoes")
