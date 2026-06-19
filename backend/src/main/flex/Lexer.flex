import java_cup.runtime.Symbol;

%%

%class Lexer
%cup
%unicode
%line
%column

/* Expresiones regulares básicas */
WhiteSpace = [ \t\r\n]+
Number     = [0-9]+
Identifier = [a-zA-Z_][a-zA-Z0-9_]*

%%

/* Reglas léxicas */
{WhiteSpace} { /* Ignorar espacios en blanco */ }

"+"          { System.out.println("[TOKEN] +"); return new Symbol(sym.PLUS, yyline, yycolumn); }
"-"          { System.out.println("[TOKEN] -"); return new Symbol(sym.MINUS, yyline, yycolumn); }
"="          { System.out.println("[TOKEN] ="); return new Symbol(sym.ASSIGN, yyline, yycolumn); }

{Number}     { System.out.println("[TOKEN] número: " + yytext()); return new Symbol(sym.NUMBER, yyline, yycolumn, yytext()); }
{Identifier} { System.out.println("[TOKEN] identificador: " + yytext()); return new Symbol(sym.ID, yyline, yycolumn, yytext()); }

/* Manejo de errores léxicos */
.            { System.out.println("Error léxico en la línea " + (yyline+1) + ", columna " + (yycolumn+1) + ": Carácter no reconocido '" + yytext() + "'"); }
