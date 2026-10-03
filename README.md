# DinoBase — pronto para hospedagem

Este projeto usa Flask + SQLite e permite cadastrar, editar, excluir e listar dinossauros com fotos.

## Estrutura

- `app.py` — rotas do site e upload das imagens.
- `banco.py` — operações SQLite.
- `dinossauros.db` — banco inicial.
- `templates/` — páginas HTML/Jinja.
- `static/style.css` — estilos.
- `requirements.txt` — dependências.
- `.python-version` — versão Python usada na hospedagem.
- `render.yaml` — configuração básica do Web Service no Render.

## Rodar localmente

```powershell
python -m pip install -r requirements.txt
python app.py
```

Abra `http://127.0.0.1:5000`.

## Publicar no Render

1. Envie esta pasta para um repositório GitHub.
2. No Render, crie um **Web Service** ligado ao repositório.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:app`
5. Defina `DATA_DIR=/var/data`.
6. Para manter SQLite e fotos depois de reinícios/deploys, anexe um **Persistent Disk** montado em `/var/data`.

Sem Persistent Disk, o sistema pode funcionar como demonstração, mas os dados e uploads gravados no filesystem do serviço podem ser perdidos quando o serviço reiniciar/redeployar.

## Fotos

As fotos são salvas em `uploads/` dentro do diretório de dados. Em produção, com `DATA_DIR=/var/data`, elas ficam em `/var/data/uploads`.

O banco inicial é copiado para `/var/data/dinossauros.db` na primeira inicialização caso ele ainda não exista.
