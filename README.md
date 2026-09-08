# Sistema Completo de Gestão Escolar (SGE)

## Sobre o projeto
O Sistema Completo de Gestão Escolar é uma plataforma projetada para digitalizar, organizar e automatizar o cotidiano de instituições de ensino. O objetivo principal do sistema é oferecer uma solução robusta e integrada para o gerenciamento de alunos, responsáveis, professores, funcionários, matrículas, histórico acadêmico, notas, frequências, atividades, cronograma e relatórios.

## Funcionalidades
- **Gestão de Usuários e Vínculos Acadêmicos**
- **Controle de Matrículas, Turmas e Disciplinas**
- **Lançamento em Lote de Faltas e Avaliações**
- **Boletins e Relatórios de Desempenho (PDF/CSV)**
- **Mural de Comunicados Internos e Notificações**

## Tecnologias
- Python 3, Flask, SQLAlchemy, Flask-Migrate, Flask-Login, Flask-WTF
- Bootstrap 5, HTML5, CSS3, JavaScript
- SQLite (Dev) / MySQL (Produção)
- Pytest, GitHub Actions (CI)

## Arquitetura
Application Factory com Blueprints isolados (MVC), onde a persistência relacional é gerida pelo SQLAlchemy ORM e os templates consumidos via Jinja2 de modo assíncrono.

## Perfis de Usuário
O SGE atende a 5 perfis sob as mais estritas regras RBAC e OLA (Object Level Authorization):
1. **Administrador**
2. **Secretaria**
3. **Professor**
4. **Responsável**
5. **Aluno**

## Requisitos
- Python 3.10+
- Git
- Navegador Atualizado

## Instalação e Configuração
```bash
git clone https://github.com/usuario/sistema-gestao-escolar.git
cd sistema-gestao-escolar
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements.txt
cp .env.example .env
# Defina o SECRET_KEY no seu .env
flask db upgrade
```

## Banco de Dados
A manipulação local padrão do `sqlite` (pasta `instance/`) é recomendada. Modificações na estrutura devem ser refletidas usando `flask db migrate -m "descrição"`.

## Testes
Rode `pytest` na raiz do projeto para realizar a varredura completa E2E, validação de RBAC e Auth Flow.

## Git e GitHub
O repositório está protegido pela automação (GitHub Actions), que invalida *Pull Requests* com testes quebrados. O modelo recomendado é feature-branch.

## Segurança
A arquitetura contempla de fábrica: CSRF Protection, HTTP Secure Headers, isolamento via Object-Level Authorization (Prevenção a IDOR em lotes de notas e acessos diretos de URL) e *rate-limiting* (Bloqueio contra Brute Force).

## Documentação
Toda a documentação técnica, manuais de usuário e regras de negócio está alocada na pasta `/docs`. Navegue pelos arquivos *.md* gerados para detalhes arquiteturais profundos.

## Estrutura do projeto
- `app/`: Aplicação web central (Blueprints, Models, Forms, Services).
- `docs/`: Manuais e Arquitetura do sistema.
- `migrations/`: Histórico do Alembic (SQL).
- `tests/`: Suíte Pytest abrangente.
- `.github/`: CI Pipelines.

## Roadmap
**Concluído:**
- Fases 1 a 18 (Arquitetura, BD, Módulos Acadêmicos, Matrículas, Lançamentos em Lote, Dashboard, Auditoria, Manuais, Versionamento).

**Futuras possibilidades (Backlog):**
- Aplicativo Mobile (API REST).
- Integração de disparos via WhatsApp API.
- Portal Financeiro Público (Boleto/PIX).
- Gestão Múlti-Unidades (Fator Polo).

## Licença
Desenvolvido para finalidade administrativa educacional. Consulte o repositório organizacional para regras de redistribuição (A definir).
