# Manual de Instalação

## Requisitos
- Python 3.10 ou superior
- Git
- Banco de dados (SQLite nativo para dev, MySQL para produção)
- Navegador de internet moderno

## Passo a Passo

1. **Clone**
```bash
git clone https://github.com/usuario/sistema-gestao-escolar.git
cd sistema-gestao-escolar
```

2. **Ambiente Virtual**
Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```
Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Dependências**
```bash
pip install -r requirements.txt
```

4. **Configuração**
Copie o exemplo para gerar o seu `.env`:
```bash
cp .env.example .env
```
Gere uma SECRET_KEY forte e atualize no arquivo `.env`.

5. **Banco e Migrações**
```bash
flask db upgrade
```

6. **Testes**
```bash
pytest
```

7. **Execução**
```bash
flask run
```
Acesse `http://localhost:5000`.
