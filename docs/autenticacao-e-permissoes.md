# Autenticação e Permissões

## Autenticação
Gerida por `Flask-Login` com criptografia de senhas usando `Werkzeug`.

## Perfis (RBAC e OLA)
O acesso não depende apenas da `Role`, mas também do contexto do Objeto (Object-Level Authorization).

- **Administrador**: Acesso total a todas as rotas e permissões, relatórios e auditoria.
- **Secretaria**: Gerenciamento acadêmico, matrículas, edição de turmas e criação de usuários (exceto remoção de administradores).
- **Professor**: Acesso restrito às **suas turmas atribuídas**. Pode lançar notas e faltas para alunos matriculados nas suas turmas.
- **Responsável**: Pode visualizar o dashboard, notas, frequências e comunicados estritamente dos **alunos vinculados** a ele.
- **Aluno**: Pode visualizar o dashboard, seu próprio boletim e faltas.
