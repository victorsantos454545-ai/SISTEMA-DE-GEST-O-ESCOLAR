# Documentação de Manutenção

## Atualizar Dependências
```bash
pip install -r requirements.txt
```
*(Cuidado: bibliotecas travadas no arquivo não devem ser atualizadas às cegas para evitar quebras).*

## Migrações (Evolução do Banco)
Se você adicionou um campo novo num Model:
```bash
flask db migrate -m "Adiciona campo de observacao"
flask db upgrade
```

## Revisão de Segurança
Mantenha os pacotes auditados rotineiramente e monitore a criação desenfreada de administradores no painel. O banco de produção deve realizar backups em S3 ou similar conforme o Cloud Provider.
