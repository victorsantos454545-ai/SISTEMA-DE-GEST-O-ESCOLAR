"""Servico de seed para roles, permissoes e dados iniciais."""
from app.extensions import db
from app.models.role import Role
from app.models.permission import Permission, role_permissions


# Definicao de todas as permissoes do sistema
ALL_PERMISSIONS = [
    # Dashboard
    ('dashboard.view', 'dashboard', 'view', 'Visualizar dashboard'),

    # Alunos
    ('students.view', 'students', 'view', 'Visualizar alunos'),
    ('students.create', 'students', 'create', 'Criar alunos'),
    ('students.edit', 'students', 'edit', 'Editar alunos'),
    ('students.delete', 'students', 'delete', 'Excluir alunos'),

    # Responsaveis
    ('guardians.view', 'guardians', 'view', 'Visualizar responsaveis'),
    ('guardians.create', 'guardians', 'create', 'Criar responsaveis'),
    ('guardians.edit', 'guardians', 'edit', 'Editar responsaveis'),
    ('guardians.delete', 'guardians', 'delete', 'Excluir responsaveis'),

    # Professores
    ('teachers.view', 'teachers', 'view', 'Visualizar professores'),
    ('teachers.create', 'teachers', 'create', 'Criar professores'),
    ('teachers.edit', 'teachers', 'edit', 'Editar professores'),
    ('teachers.delete', 'teachers', 'delete', 'Excluir professores'),

    # Funcionarios
    ('employees.view', 'employees', 'view', 'Visualizar funcionarios'),
    ('employees.create', 'employees', 'create', 'Criar funcionarios'),
    ('employees.edit', 'employees', 'edit', 'Editar funcionarios'),
    ('employees.delete', 'employees', 'delete', 'Excluir funcionarios'),

    # Turmas
    ('classes.view', 'classes', 'view', 'Visualizar turmas'),
    ('classes.create', 'classes', 'create', 'Criar turmas'),
    ('classes.edit', 'classes', 'edit', 'Editar turmas'),
    ('classes.delete', 'classes', 'delete', 'Excluir turmas'),

    # Disciplinas
    ('subjects.view', 'subjects', 'view', 'Visualizar disciplinas'),
    ('subjects.create', 'subjects', 'create', 'Criar disciplinas'),
    ('subjects.edit', 'subjects', 'edit', 'Editar disciplinas'),
    ('subjects.delete', 'subjects', 'delete', 'Excluir disciplinas'),

    # Matriculas
    ('enrollments.view', 'enrollments', 'view', 'Visualizar matriculas'),
    ('enrollments.create', 'enrollments', 'create', 'Criar matriculas'),
    ('enrollments.edit', 'enrollments', 'edit', 'Editar matriculas'),
    ('enrollments.delete', 'enrollments', 'delete', 'Excluir matriculas'),

    # Notas
    ('grades.view', 'grades', 'view', 'Visualizar notas'),
    ('grades.create', 'grades', 'create', 'Lancar notas'),
    ('grades.edit', 'grades', 'edit', 'Editar notas'),
    ('grades.delete', 'grades', 'delete', 'Excluir notas'),

    # Frequencia
    ('attendance.view', 'attendance', 'view', 'Visualizar frequencia'),
    ('attendance.create', 'attendance', 'create', 'Lancar frequencia'),
    ('attendance.edit', 'attendance', 'edit', 'Editar frequencia'),
    ('attendance.delete', 'attendance', 'delete', 'Excluir frequencia'),

    # Avaliacoes
    ('assessments.view', 'assessments', 'view', 'Visualizar avaliacoes'),
    ('assessments.create', 'assessments', 'create', 'Criar avaliacoes'),
    ('assessments.edit', 'assessments', 'edit', 'Editar avaliacoes'),
    ('assessments.delete', 'assessments', 'delete', 'Excluir avaliacoes'),

    # Atividades
    ('activities.view', 'activities', 'view', 'Visualizar atividades'),
    ('activities.create', 'activities', 'create', 'Criar atividades'),
    ('activities.edit', 'activities', 'edit', 'Editar atividades'),
    ('activities.delete', 'activities', 'delete', 'Excluir atividades'),

    # Calendario
    ('calendar.view', 'calendar', 'view', 'Visualizar calendario'),
    ('calendar.create', 'calendar', 'create', 'Criar eventos'),
    ('calendar.edit', 'calendar', 'edit', 'Editar eventos'),
    ('calendar.delete', 'calendar', 'delete', 'Excluir eventos'),

    # Horarios
    ('schedules.view', 'schedules', 'view', 'Visualizar horarios'),
    ('schedules.create', 'schedules', 'create', 'Criar horarios'),
    ('schedules.edit', 'schedules', 'edit', 'Editar horarios'),
    ('schedules.delete', 'schedules', 'delete', 'Excluir horarios'),

    # Comunicados
    ('announcements.view', 'announcements', 'view', 'Visualizar comunicados'),
    ('announcements.create', 'announcements', 'create', 'Criar comunicados'),
    ('announcements.edit', 'announcements', 'edit', 'Editar comunicados'),
    ('announcements.delete', 'announcements', 'delete', 'Excluir comunicados'),
    ('announcements.publish', 'announcements', 'publish', 'Publicar comunicados'),
    ('announcements.manage', 'announcements', 'manage', 'Gerenciar comunicados'),
    
    # Notificações
    ('notifications.view', 'notifications', 'view', 'Visualizar notificações'),
    ('notifications.manage', 'notifications', 'manage', 'Gerenciar notificações'),

    # Relatorios
    ('reports.view', 'reports', 'view', 'Visualizar relatorios'),
    ('reports.export', 'reports', 'export', 'Exportar relatorios'),

    # Usuarios
    ('users.view', 'users', 'view', 'Visualizar usuarios'),
    ('users.create', 'users', 'create', 'Criar usuarios'),
    ('users.edit', 'users', 'edit', 'Editar usuarios'),
    ('users.delete', 'users', 'delete', 'Excluir usuarios'),
    ('users.manage', 'users', 'manage', 'Gerenciar usuarios'),

    # Roles e Permissoes
    ('roles.view', 'roles', 'view', 'Visualizar papeis'),
    ('roles.manage', 'roles', 'manage', 'Gerenciar papeis'),
    ('permissions.view', 'permissions', 'view', 'Visualizar permissoes'),
    ('permissions.manage', 'permissions', 'manage', 'Gerenciar permissoes'),

    # Configuracoes
    ('settings.view', 'settings', 'view', 'Visualizar configuracoes'),
    ('settings.manage', 'settings', 'manage', 'Gerenciar configuracoes'),

    # Auditoria
    ('audit.view', 'audit', 'view', 'Visualizar auditoria'),
]

# Matriz de permissoes por role
ROLE_PERMISSIONS = {
    'admin': [p[0] for p in ALL_PERMISSIONS],
    'professor': [
        'dashboard.view',
        'students.view',
        'classes.view', 'subjects.view',
        'enrollments.view',
        'grades.view', 'grades.create', 'grades.edit', 'grades.delete',
        'attendance.view', 'attendance.create', 'attendance.edit', 'attendance.delete',
        'assessments.view', 'assessments.create', 'assessments.edit', 'assessments.delete',
        'activities.view', 'activities.create', 'activities.edit', 'activities.delete',
        'calendar.view',
        'schedules.view',
        'announcements.view', 'announcements.create',
        'reports.view',
        'notifications.view'
    ],
    'secretaria': [
        'dashboard.view',
        'students.view', 'students.create', 'students.edit',
        'guardians.view', 'guardians.create', 'guardians.edit',
        'teachers.view',
        'employees.view',
        'classes.view', 'subjects.view',
        'enrollments.view', 'enrollments.create', 'enrollments.edit',
        'grades.view',
        'attendance.view',
        'calendar.view', 'calendar.create', 'calendar.edit',
        'schedules.view', 'schedules.create', 'schedules.edit',
        'announcements.view', 'announcements.create', 'announcements.edit', 'announcements.publish',
        'notifications.view'
    ],
    'responsavel': [
        'dashboard.view',
        'students.view',
        'grades.view',
        'attendance.view',
        'assessments.view',
        'activities.view',
        'calendar.view',
        'schedules.view',
        'announcements.view',
        'notifications.view'
    ],
    'aluno': [
        'dashboard.view',
        'students.view',
        'grades.view',
        'attendance.view',
        'assessments.view',
        'activities.view',
        'calendar.view',
        'schedules.view',
        'announcements.view',
        'notifications.view'
    ],
}


def seed_permissions():
    """Cria todas as permissoes do sistema. Idempotente."""
    created = 0
    for name, module, action, description in ALL_PERMISSIONS:
        if not Permission.query.filter_by(name=name).first():
            db.session.add(Permission(
                name=name, module=module,
                action=action, description=description
            ))
            created += 1
    db.session.commit()
    print(f'  Permissoes criadas: {created}')
    return created


def seed_roles():
    """Cria as roles do sistema. Idempotente."""
    roles_data = [
        ('admin', 'Administrador do sistema'),
        ('professor', 'Professor'),
        ('secretaria', 'Secretaria'),
        ('responsavel', 'Responsavel'),
        ('aluno', 'Aluno'),
    ]
    created = 0
    for name, description in roles_data:
        if not Role.query.filter_by(name=name).first():
            db.session.add(Role(name=name, description=description))
            created += 1
    db.session.commit()
    print(f'  Roles criadas: {created}')
    return created


def seed_role_permissions():
    """Associa permissoes a roles. Idempotente."""
    all_perms = {p.name: p for p in Permission.query.all()}

    for role_name, perm_names in ROLE_PERMISSIONS.items():
        role = Role.query.filter_by(name=role_name).first()
        if role is None:
            continue

        if perm_names == '__all__':
            target_perms = set(all_perms.values())
        else:
            target_perms = {all_perms[n] for n in perm_names if n in all_perms}

        current_perms = set(role.permissions)
        to_add = target_perms - current_perms

        for perm in to_add:
            role.permissions.append(perm)

    db.session.commit()
    print('  Permissoes associadas as roles')


def seed_all_permissions():
    """Executa seed completa de roles + permissoes."""
    print('[1/3] Criando roles...')
    seed_roles()
    print('[2/3] Criando permissoes...')
    seed_permissions()
    print('[3/3] Associando permissoes as roles...')
    seed_role_permissions()
    print('Seed de permissoes concluida!')
