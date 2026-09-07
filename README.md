# Sistema Completo de Gestão Escolar (SGE)

## Descrição

O Sistema Completo de Gestão Escolar é uma plataforma projetada para digitalizar, organizar e automatizar o cotidiano de instituições de ensino. O objetivo principal do sistema é oferecer uma solução robusta e integrada para o gerenciamento de alunos, responsáveis, professores, funcionários, matrículas, histórico acadêmico, notas, frequências, atividades, cronograma e relatórios.

O SGE atende a cinco tipos de perfis de usuário, cada um com visões e acessos restritos por RBAC (Role-Based Access Control) e OLA (Object-Level Authorization):
- **Administrador**: Gestão total da escola.
- **Secretaria**: Operações acadêmicas e documentais diárias.
- **Professor**: Lançamento de notas, frequências, comunicados de turmas ativas.
- **Responsável**: Acompanhamento do desempenho e vida acadêmica dos alunos vinculados.
- **Aluno**: Consulta de sua frequência, notas e agenda.

O sistema foi desenhado em uma arquitetura limpa (MVC) utilizando Application Factories, Blueprints modulares, serviços isolados e camadas de segurança transacional.

## Tecnologias

- Python 3
- Flask
- SQLAlchemy
- Flask-Migrate
- Flask-Login
- Flask-WTF
- Bootstrap 5
- HTML5
- CSS3
- JavaScript
- SQLite (para desenvolvimento/testes locais)
- MySQL (preparado para produção)
- Pytest (com pytest-cov)
- Git e GitHub

## Requisitos

- **Python 3.10+** (Testado no 3.12)
- **Git**
- Navegador atualizado (Chrome, Firefox, Safari)
- **(Para Produção)** Banco MySQL 8.0+ ou MariaDB

## Instalação

**1. Clonar o repositório**
```bash
git clone https://github.com/seu-usuario/sistema-escolar.git
cd sistema-escolar
```

**2. Criar ambiente virtual**
```bash
python -m venv venv
```

**3. Ativar o ambiente virtual**
- Windows (PowerShell):
  ```powershell
  venv\Scripts\activate
  ```
- Linux/macOS:
  ```bash
  source venv/bin/activate
  ```

**4. Instalar as dependências**
```bash
pip install -r requirements.txt
```

**5. Configurar o ambiente**
```bash
# Copie o arquivo de configuração de exemplo
cp .env.example .env
```
Edite o arquivo `.env` gerado e insira uma `SECRET_KEY` forte (recomendado: `python -c "import secrets; print(secrets.token_hex(32))"`).

**6. Executar as migrações**
```bash
flask db upgrade
```

**7. Iniciar o servidor de desenvolvimento**
```bash
flask run
# ou
python run.py
```
Acesse em: `http://localhost:5000`

## Banco de Dados e Migrações

O banco de dados é mapeado via SQLAlchemy ORM e manipulado pelo Flask-Migrate (Alembic).

- **Criar uma nova migração (após alterar models):**
  ```bash
  flask db migrate -m "descricao-da-mudanca"
  ```
- **Aplicar as migrações no banco (deploy/desenvolvimento):**
  ```bash
  flask db upgrade
  ```
> **Nota:** Não execute migrações destrutivas (ex: `flask db downgrade`) em produção sem antes verificar rigorosamente o estado do banco e realizar um backup de segurança.

## Testes

A aplicação utiliza o `pytest` para testes unitários, testes de regressão sistêmica, fluxos de acesso e segurança (IDOR/Auth). O banco de testes (`sqlite:///:memory:`) é recriado de forma isolada a cada execução.

**Executar os testes padrão:**
```bash
pytest
```

**Com verbosidade (detalhes e output estendido):**
```bash
pytest -v
```

**Gerar relatório de cobertura (requer pytest-cov):**
```bash
pytest --cov=app --cov-report=term-missing
```

## Estrutura de Branches

Utilizamos o seguinte modelo simplificado de branches para manter o versionamento do repositório organizado:

- `main`: Branch principal do projeto. Deve estar sempre estável e pronta para deploy em produção.
- `feature/nome-da-funcionalidade`: Para o desenvolvimento de novos recursos.
- `fix/nome-do-problema`: Para a correção de bugs de aplicação.
- `security/nome-da-correcao`: Para correções imediatas de segurança ou patches urgentes.
- `docs/nome-da-documentacao`: Atualizações de documentação, manuais e READMEs.
- `test/nome-do-teste`: Para elaboração e validação de suítes de testes complexas.

## Proteção da Branch Main

Boas práticas essenciais para proteção da branch principal (`main`):
1. **Evitar commits experimentais**: Não faça push direto (commit direto) para a `main`.
2. **Uso de PRs (Pull Requests)**: Todo código deve ser validado através de um PR.
3. **Continuous Integration (CI)**: O CI deve rodar e garantir que `pytest` e os *linters* passaram antes do Merge.
4. **Sem Credenciais**: A branch main nunca deverá conter nenhum dado do arquivo `.env` pessoal, arquivos do tipo `*.db` preenchidos ou `.pem`/`chaves SSH` que pertençam aos desenvolvedores.

## Padrão de Commits

Todo commit deve representar uma mudança lógica, clara e independente. Este projeto utiliza o padrão de *Conventional Commits*:

- `feat:` adiciona ou introduz uma nova funcionalidade no sistema.
- `fix:` corrige um bug ou comportamento incorreto.
- `refactor:` reorganiza o código sem adicionar *features* nem consertar falhas (ex: limpeza, Otimização de importações).
- `test:` adiciona ou ajusta os testes automatizados da aplicação.
- `docs:` trata especificamente de arquivos de documentação do projeto.
- `security:` aplica correções de segurança em rotas e serviços.
- `chore:` tarefas rotineiras, atualizações de dependências (`requirements.txt`), configuração de lint, etc.

*Evite mensagens genéricas como "alterações", "versão final" ou "correção rápida".*

## Backup

A política básica de Backup para este Sistema Escolar prevê separações lógicas essenciais:
1. **Código-Fonte**: 100% versionado e com backup no Git/GitHub.
2. **Banco de Dados (Produção)**: Deve possuir estratégia própria do provedor de infraestrutura (ex: *mysqldump* automatizado para S3, Snapshots da RDS). **Não mande o banco via Git**.
3. **Uploads / Arquivos (exports/uploads)**: O diretório de arquivos gerados (boletins PDF, arquivos anexados de alunos) deve ter backups periódicos assíncronos. Eles estão listados no `.gitignore` e não fazem parte do repositório remoto.
4. **Variáveis de Ambiente**: Mantenha um backup seguro de seus arquivos `.env` e senhas do MySQL através de um Gerenciador de Segredos/Vault.

## Licença

Projeto desenvolvido para fins educacionais e administrativos. A definição de licença (ex: MIT, GPL) deverá ser documentada posteriormente conforme o caso de uso.
