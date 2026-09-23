# Importação de todos os modelos para que o Flask-Migrate os detecte.
# A ordem de importação respeita as dependências entre tabelas.

from app.models.base import TimestampMixin
from app.models.role import Role
from app.models.permission import Permission, role_permissions
from app.models.user import User
from app.models.student import Student
from app.models.guardian import Guardian
from app.models.student_guardian import StudentGuardian
from app.models.teacher import Teacher
from app.models.employee import Employee
from app.models.school_year import SchoolYear
from app.models.period import Period
from app.models.subject import Subject
from app.models.teacher_subject import teacher_subjects
from app.models.school_class import SchoolClass
from app.models.class_subject import ClassSubject
from app.models.class_teacher import ClassTeacher
from app.models.enrollment import Enrollment
from app.models.assessment import Assessment
from app.models.grade import Grade
from app.models.attendance import Attendance
from app.models.activity import Activity
from app.models.schedule import Schedule
from app.models.calendar_event import CalendarEvent
from app.models.announcement import Announcement, AnnouncementRecipient, AnnouncementRead
from app.models.notification import Notification
from app.models.system_config import SystemConfig
from app.models.password_reset import PasswordResetToken
from app.models.audit_log import AuditLog

__all__ = [
    'TimestampMixin',
    'Role', 'Permission', 'role_permissions',
    'User',
    'Student', 'Guardian', 'StudentGuardian',
    'Teacher', 'Employee',
    'SchoolYear', 'Period',
    'Subject', 'teacher_subjects',
    'SchoolClass', 'ClassSubject', 'ClassTeacher',
    'Enrollment',
    'Assessment', 'Grade', 'Attendance',
    'Activity', 'Schedule',
    'CalendarEvent',
    'Announcement', 'AnnouncementRecipient', 'AnnouncementRead',
    'Notification',
    'SystemConfig',
    'PasswordResetToken', 'AuditLog',
]
