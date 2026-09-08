# Documentação das Funcionalidades

- **Gestão de Usuários**: CRUD de acessos e reset de senhas. Depende das permissões do Admin.
- **Gestão Acadêmica (Alunos, Professores, Responsáveis)**: Vínculos e cadastros.
- **Turmas e Disciplinas**: Criação de alocações (SchoolClass) ligando professores.
- **Matrículas**: Insere o aluno em uma turma. Valida vagas e status ativo.
- **Notas e Avaliações**: Professores criam avaliações e processam notas em lote (GradeBatch).
- **Frequência**: Chamada em lote processada transacionalmente. Valida se aluno pertence à turma.
- **Comunicados e Avisos**: Disparo com controle de leitura.
- **Relatórios**: Boletins individuais, relatórios por turma e exportações (CSV/PDF) com filtros avançados.
- **Dashboard**: Gráficos estatísticos que se adaptam automaticamente ao perfil (Admin vê escola toda, Aluno vê si mesmo).
