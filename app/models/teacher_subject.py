"""Tabela associativa simples para Teacher <-> Subject (N:N).

Utiliza db.Table porque não possui campos extras além das chaves.
A primary key composta (teacher_id, subject_id) impede duplicação automaticamente.
"""
from app.extensions import db

teacher_subjects = db.Table(
    'teacher_subjects',
    db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id'), primary_key=True)
)
