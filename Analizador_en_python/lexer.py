"""
Analizador léxico para sistemas de ecuaciones lineales 2x2.

Define los tokens reconocidos y las reglas para convertir
una cadena de texto en una secuencia de tokens.

Tokens definidos:
    NUMBER   → números enteros
    VARIABLE → letras que representan incógnitas (x, y)
    PLUS     → operador suma (+)
    MINUS    → operador resta (-)
    EQUALS   → operador de igualdad (=)
"""

import ply.lex as lex

tokens = (
    'NUMBER',
    'VARIABLE',
    'PLUS',
    'MINUS',
    'EQUALS',
)

# Reglas simples: expresiones regulares directas
t_PLUS   = r'\+'
t_MINUS  = r'-'
t_EQUALS = r'='


def t_VARIABLE(t):
    r'[a-zA-Z]'
    return t


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


# Caracteres ignorados (espacios, tabs, saltos de línea)
t_ignore = ' \t\r\n'


def t_error(t):
    """Manejo de errores léxicos: lanza excepción con el carácter ilegal."""
    raise Exception(
        f"Símbolo no válido o carácter ilegal: '{t.value[0]}'"
    )


lexer = lex.lex()
