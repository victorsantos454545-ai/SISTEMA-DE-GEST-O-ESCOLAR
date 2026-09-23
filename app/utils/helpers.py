from datetime import datetime


def format_date(date, fmt='%d/%m/%Y'):
    """Formata uma data para exibição."""
    if isinstance(date, datetime):
        return date.strftime(fmt)
    return ''


def format_datetime(dt, fmt='%d/%m/%Y %H:%M'):
    """Formata data e hora para exibição."""
    if isinstance(dt, datetime):
        return dt.strftime(fmt)
    return ''


def format_cpf(cpf):
    """Formata CPF: 123.456.789-01"""
    if cpf and len(cpf) == 11:
        return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'
    return cpf or ''


def format_phone(phone):
    """Formata telefone: (11) 91234-5678"""
    if phone and len(phone) == 11:
        return f'({phone[:2]}) {phone[2:7]}-{phone[7:]}'
    elif phone and len(phone) == 10:
        return f'({phone[:2]}) {phone[2:6]}-{phone[6:]}'
    return phone or ''


def format_cep(cep):
    """Formata CEP: 12345-678"""
    if cep and len(cep) == 8:
        return f'{cep[:5]}-{cep[5:]}'
    return cep or ''


def sanitize_digits(value):
    """Remove caracteres não numéricos."""
    if value:
        return ''.join(c for c in str(value) if c.isdigit())
    return ''
