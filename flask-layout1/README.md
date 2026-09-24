# Atividade Flask - Autenticação, Hash e SQLite

## Executar

```bash
pip install -r requirements.txt
python app.py
```

Abra no navegador: http://127.0.0.1:5000

## Login da atividade

Usuário: `felipe`

Senha: `1234`

A senha é salva no SQLite usando hash com `generate_password_hash`.

## Páginas

- `/` - página inicial
- `/sobre` - página pessoal
- `/login` - autenticação
- `/boletim` - página restrita com notas vindas do SQLite
- `/informacoes` - página restrita com dados pessoais vindos do SQLite
- `/logout` - encerra a sessão

O arquivo `dados.db` é criado automaticamente na primeira execução.
