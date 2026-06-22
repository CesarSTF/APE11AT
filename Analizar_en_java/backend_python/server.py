import re
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys

# ============================================================
# LEXER
# ============================================================
TOKEN_SPEC = [
    ('MAS',           r'\+'),
    ('MENOS',         r'-'),
    ('ASIGNACION',    r'='),
    ('NUMBER',        r'[0-9]+'),
    ('IDENTIFICADOR', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('WHITESPACE',    r'[ \t\r\n]+'),
    ('ERROR',         r'.'),
]

TOKEN_RE = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC))


def lex(code):
    tokens = []
    for m in TOKEN_RE.finditer(code):
        kind = m.lastgroup
        lexeme = m.group()
        if kind == 'WHITESPACE':
            continue
        elif kind == 'ERROR':
            tokens.append({
                'token': 'ERROR',
                'lexema': lexeme,
                'identificado': 'NO IDENTIFICADO'
            })
            col = m.start()
            line_num = code[:m.start()].count('\n') + 1
            col_num = m.start() - code[:m.start()].rfind('\n')
            yield ('ERROR', lexeme, f"Error lexico en la linea {line_num}, columna {col_num}: Caracter no reconocido '{lexeme}'")
        else:
            yield (kind, lexeme, None)
    return tokens


# ============================================================
# PARSER (recursive descent, elimina left recursion)
# ============================================================
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self):
        t = self.tokens[self.pos]
        self.pos += 1
        return t

    def _expected(self):
        t = self.peek()
        if not t:
            return "fin de entrada"
        kind_map = {'MAS': '[+]', 'MENOS': '[-]', 'ASIGNACION': '[=]', 'NUMBER': '[numero]', 'IDENTIFICADOR': '[identificador]'}
        return kind_map.get(t[0], t[0])

    def parse(self):
        self.equation_list()

    def equation_list(self):
        while self.peek() is not None:
            self.equation()

    def equation(self):
        self.expression()
        t = self.peek()
        if t and t[0] == 'ASIGNACION':
            self.consume()
            self.expression()
        else:
            raise SyntaxError(f"Error de sintaxis: se esperaba [=], pero se encontro {self._expected()}")

    def expression(self):
        t = self.peek()
        if not t:
            raise SyntaxError("Error de sintaxis: expresion incompleta")
        if t[0] in ('IDENTIFICADOR', 'NUMBER'):
            self.consume()
        else:
            raise SyntaxError(f"Error de sintaxis: se esperaba [identificador] o [numero], pero se encontro '{t[1]}'")

        while self.peek() and self.peek()[0] in ('MAS', 'MENOS'):
            self.consume()
            t2 = self.peek()
            if t2 and t2[0] in ('IDENTIFICADOR', 'NUMBER'):
                self.consume()
            else:
                raise SyntaxError(f"Error de sintaxis: se esperaba [identificador] o [numero] despues del operador, pero se encontro '{self._expected()}'")


KIND_MAP = {'MAS': 'MAS', 'MENOS': 'MENOS', 'ASIGNACION': 'ASIGNACION', 'NUMBER': 'NUMERO', 'IDENTIFICADOR': 'IDENTIFICADOR'}

def analizar(code):
    tokens = []
    errores = []
    parser_tokens = []

    for kind, lexeme, error in lex(code):
        if kind == 'WHITESPACE':
            continue
        if kind == 'ERROR' and error:
            tokens.append({'token': 'ERROR', 'lexema': lexeme, 'identificado': 'NO IDENTIFICADO'})
            errores.append(error)
        else:
            display_name = KIND_MAP.get(kind, kind)
            tokens.append({'token': display_name, 'lexema': lexeme, 'identificado': 'IDENTIFICADO'})
            parser_tokens.append((kind, lexeme))

    try:
        parser = Parser(parser_tokens)
        parser.parse()
        status = 'ok'
        message = 'Analisis exitoso'
        diagnostico = '\n'.join(errores) if errores else None
    except SyntaxError as e:
        status = 'error'
        message = str(e)
        if errores:
            message += ' - ' + ' - '.join(errores)
        diagnostico = None

    return {
        'status': status,
        'message': message,
        'tokens': tokens,
        'diagnostico': diagnostico
    }


# ============================================================
# HTTP SERVER
# ============================================================
class ParseHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def do_POST(self):
        if self.path != '/api/parse':
            self.send_json(404, {'error': 'Ruta no encontrada'})
            return

        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')

        result = analizar(body)
        result['input'] = body

        if result['diagnostico'] is None:
            del result['diagnostico']

        self.send_json(200, result)

    def do_GET(self):
        if self.path == '/':
            self.send_error(404, 'Este es solo el backend API. Usa http://localhost:8080 para el frontend.')
            return
        self.send_error(404)

    def send_json(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        sys.stderr.write(f"[Python] {args[0]} {args[1]} {args[2]}\n")


if __name__ == '__main__':
    port = 8081
    server = HTTPServer(('0.0.0.0', port), ParseHandler)
    print(f"[Python] Servidor iniciado en http://localhost:{port}")
    server.serve_forever()
