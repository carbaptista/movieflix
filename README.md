# Movieflix - Carlos Habib

Professora, não vou mentir, essas duas últimas semanas eu estive muito (MUITO) ocupado, e acabei tendo pouco tempo para fazer esse projeto e por isso tive que receber bastante ajuda do copilot pra conseguir entregar. Sei que é meio contra o objetivo, mas não teve jeito. 

## Como executar

1. Construa e inicie os serviços:
   ```sh
   docker-compose up --build
   ```
2. Às vezes, o script pra carregar o banco é executado antes do banco ficar disponível, quando isso aconteceu, recebi um erro 502. Rodar o build novamente geralmente resolve o problema. 
3. Como estou usando o nginx, a url é apenas [localhost](http://localhost)
4. Tem também o swagger em [http://localhost/docs](http://localhost/docs)

## Data Mart
A views são criadas no arquivo load_csv_data.py

## Consultas Analíticas
### 5 Filmes Mais Populares

```sql
SELECT f.titulo, f.genero, COUNT(a.id) AS total_avaliacoes
FROM movies f
JOIN ratings a ON a.filme_id = f.id
GROUP BY f.id, f.titulo, f.genero
ORDER BY total_avaliacoes DESC
LIMIT 5;
```

### Gênero com Maior Nota Média

```sql
SELECT genero, AVG(nota) AS media_nota
FROM movies m
JOIN ratings r ON r.filme_id = m.id
GROUP BY genero
ORDER BY media_nota DESC
LIMIT 1;
```

### País com Maior Quantidade de Avaliações

```sql
SELECT pais, COUNT(r.id) AS quantidade_avaliacoes
FROM users u
JOIN ratings r ON r.usuario_id = u.id
GROUP BY pais
ORDER BY quantidade_avaliacoes DESC
LIMIT 1;
```
## Entragáveis
- O código deste repositório
- Os dois Dockerfiles e docker-compose.yml
- Workflow em .github/docker.yml
- Script de carga load_csv_data.py