# APE_11 — Analizador Sintáctico de Sistemas de Ecuaciones

Aplicación web con Flask que resuelve sistemas de **2 ecuaciones lineales con 2 incógnitas** (x, y) mediante un analizador léxico y sintáctico construido con **PLY** (Python Lex-Yacc).

## Estructura del proyecto

```
APE_11/
├── app.py              # Servidor Flask (rutas / y /solve)
├── lexer.py            # Analizador léxico — define tokens
├── parcer.py           # Analizador sintáctico + resolución
├── static/
│   ├── style.css       # Estilos de la interfaz
│   └── script.js       # Lógica del lado del cliente
├── templates/
│   └── index.html      # Interfaz web
└── env/                # Entorno virtual Python
```

## Tokens del lenguaje

| Token      | Patrón       | Descripción                     |
|------------|-------------|----------------------------------|
| `NUMBER`   | `\d+`       | Número entero (ej: 5, 12)       |
| `VARIABLE` | `[a-zA-Z]`  | Variable (x, y)                  |
| `PLUS`     | `\+`        | Operador suma                    |
| `MINUS`    | `-`         | Operador resta                   |
| `EQUALS`   | `=`         | Operador de igualdad             |

## Gramática

```
sistema   → ecuacion ecuacion
ecuacion  → expresion = NUMBER
expresion → termino_x termino_y | termino_y termino_x
           | termino_x | termino_y
termino_x → VARIABLE | + VARIABLE | - VARIABLE
termino_y → + VARIABLE | - VARIABLE
```

## Formato de entrada

Cada ecuación debe escribirse en una línea, combinando `x`, `y`, `+`, `-` y un número entero después de `=`.

**Ejemplos:**
```
x + y = 5
x - y = 1
```

```
2x + 3y = 10
x - y = 2
```

## Instalación y ejecución

```bash
# Activar entorno virtual
source env/bin/activate

# Ejecutar servidor
python app.py
```
Abrir en el navegador: `http://127.0.0.1:5000`

## Tecnologías

- Python 3
- Flask
- PLY (Python Lex-Yacc)
