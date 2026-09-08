# Documentação Git e GitHub

## Estratégia de Branches
- `main`: Ambiente de produção.
- `feature/*`: Desenvolvimento de features.
- `fix/*`: Correções de bugs.
- `security/*`: Correções de vulnerabilidades.

## Comandos Comuns
```bash
git status
git add .
git commit -m "feat: adiciona dashboard do professor"
git push origin feature/dashboard-prof
```

## Pull Requests (PRs) e CI
A branch `main` é protegida conceitualmente. O CI (GitHub Actions) está configurado em `.github/workflows/tests.yml` e rodará o `pytest` obrigatoriamente a cada push ou PR aberto.
