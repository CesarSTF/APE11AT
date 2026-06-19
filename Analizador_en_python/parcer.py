"""
Analizador sintáctico (parser) para sistemas de 2 ecuaciones lineales
con 2 incógnitas (x, y).

Gramática:
    sistema   → ecuacion ecuacion
    ecuacion  → expresion = NUMBER
    expresion → termino_x termino_y | termino_y termino_x
              | termino_x | termino_y
    termino_x → VARIABLE | + VARIABLE | - VARIABLE
    termino_y → + VARIABLE | - VARIABLE

Semántica:
    Cada ecuación se representa como {x, y, c}. Al parsear un sistema
    completo se resuelve por determinantes (regla de Cramer).
"""

import ply.yacc as yacc
from lexer import tokens


def p_sistema(p):
    """
    sistema : ecuacion ecuacion
    """
    # Punto de entrada: procesa dos ecuaciones y las resuelve
    p[0] = resolver_sistema(p[1], p[2])


def p_ecuacion(p):
    """
    ecuacion : expresion EQUALS NUMBER
    """
    # Una ecuación: expresión algebraica + '=' + término independiente
    p[0] = {
        'x': p[1].get('x', 0),
        'y': p[1].get('y', 0),
        'c': p[3],
    }


def p_expresion_comb(p):
    """
    expresion : termino_x termino_y
             | termino_y termino_x
    """
    # Expresión con dos términos (x e y), se fusionan coeficientes
    result = {}
    result.update(p[1])
    result.update(p[2])
    p[0] = result


def p_expresion_single(p):
    """
    expresion : termino_x
             | termino_y
    """
    # Expresión de un solo término
    p[0] = p[1]


def p_termino_x_pos(p):
    """
    termino_x : VARIABLE
              | PLUS VARIABLE
    """
    # Término positivo de x (con + explícito o implícito)
    v = p[1] if len(p) == 2 else p[2]
    p[0] = {'x': 1} if v.lower() == 'x' else {'y': 1}


def p_termino_x_neg(p):
    """
    termino_x : MINUS VARIABLE
    """
    # Término negativo de x
    p[0] = {'x': -1} if p[2].lower() == 'x' else {'y': -1}


def p_termino_y_pos(p):
    """
    termino_y : PLUS VARIABLE
    """
    # Término positivo de y
    p[0] = {'y': 1} if p[2].lower() == 'y' else {'x': 1}


def p_termino_y_neg(p):
    """
    termino_y : MINUS VARIABLE
    """
    # Término negativo de y
    p[0] = {'y': -1} if p[2].lower() == 'y' else {'x': -1}


def p_error(p):
    """
    Manejo de errores sintácticos.
    Se invoca ante un token inesperado o entrada incompleta.
    """
    if p:
        raise Exception(
            f"Error de sintaxis cerca del token '{p.value}'"
        )
    raise Exception(
        "Error de sintaxis: Las ecuaciones están incompletas "
        "o mal estructuradas."
    )


def resolver_sistema(eq1, eq2):
    """
    Resuelve un sistema de 2 ecuaciones lineales con 2 incógnitas
    mediante el método de determinantes (regla de Cramer).

    Parámetros
    ----------
    eq1 : dict
        Coeficientes de la primera ecuación: {x, y, c}.
    eq2 : dict
        Coeficientes de la segunda ecuación: {x, y, c}.

    Retorna
    -------
    dict
        Si tiene solución única:
            {"status": "success", "x": ..., "y": ..., "pasos": [...]}
        Si el determinante es cero:
            {"status": "error", "msg": "..."}
    """
    a1, b1, c1 = eq1.get('x', 0), eq1.get('y', 0), eq1.get('c', 0)
    a2, b2, c2 = eq2.get('x', 0), eq2.get('y', 0), eq2.get('c', 0)

    det = a1 * b2 - b1 * a2

    if det == 0:
        if (a1 * c2 - c1 * a2) == 0:
            return {
                "status": "error",
                "msg": "El sistema tiene infinitas soluciones.",
            }
        return {
            "status": "error",
            "msg": "El sistema no tiene solución (es inconsistente).",
        }

    x = (c1 * b2 - b1 * c2) / det
    y = (a1 * c2 - c1 * a2) / det

    pasos = []
    pasos.append(
        f"Ecuación 1 compilada con éxito: {a1}x + ({b1}y) = {c1}"
    )
    pasos.append(
        f"Ecuación 2 compilada con éxito: {a2}x + ({b2}y) = {c2}"
    )

    # Si b1 + b2 == 0 los coeficientes de y se cancelan al sumar
    if b1 + b2 == 0 and a1 + a2 != 0:
        pasos.append(
            "Reducción detectada: Se suman ambas ecuaciones directamente:"
        )
        pasos.append(
            f"({a1}x + {a2}x) = {c1} + {c2}  =>  {a1 + a2}x = {c1 + c2}"
        )
        pasos.append(
            f"Despejando x = {c1 + c2} / {a1 + a2} = {int(x)}"
        )
        pasos.append(
            f"Sustituyendo x = {int(x)} en la Ecuación 1:"
        )
        pasos.append(
            f"{a1}({int(x)}) + ({b1}y) = {c1}  =>  "
            f"{b1}y = {c1 - a1 * int(x)}"
        )
        pasos.append(f"Despejando y = {int(y)}")
    else:
        pasos.append(
            "Aplicando resolución general por determinantes:"
        )
        pasos.append(
            f"Determinante del Sistema (Δ) = {det}"
        )
        pasos.append(
            f"x = {c1 * b2 - b1 * c2} / {det} = {x}"
        )
        pasos.append(
            f"y = {a1 * c2 - c1 * a2} / {det} = {y}"
        )

    return {
        "status": "success",
        "x": int(x) if x.is_integer() else round(x, 2),
        "y": int(y) if y.is_integer() else round(y, 2),
        "pasos": pasos,
    }


parser = yacc.yacc()
