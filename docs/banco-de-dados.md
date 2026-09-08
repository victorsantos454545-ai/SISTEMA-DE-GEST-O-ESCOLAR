# Banco de Dados

O banco mapeado via SQLAlchemy possui as seguintes tabelas principais:

- **User**: Credenciais e controle de acesso.
- **Role & Permission**: Controle de Acesso Baseado em Perfis (RBAC).
- **Student**: Dados cadastrais do aluno (CPF, nome).
- **Guardian**: Responsáveis legais.
- **StudentGuardian**: Tabela associativa n:n entre alunos e responsáveis.
- **Teacher & Employee**: Corpo docente e administrativo.
- **SchoolYear & Period**: Anos letivos e bimestres/trimestres.
- **Subject**: Disciplinas oferecidas.
- **SchoolClass**: Turmas vinculadas a um ano letivo.
- **ClassTeacher**: Vínculo n:n entre professor e turma.
- **Enrollment**: Matrícula do aluno na turma.
- **Assessment & Grade**: Avaliações criadas por professores e notas dos alunos.
- **Attendance**: Registros de presença/falta e justificativas.
- **Announcement & Notification**: Comunicados internos.
- **SystemConfig**: Configurações dinâmicas injetadas na base.

O ORM encarrega-se das restrições de chave estrangeira e deleções em cascata.
