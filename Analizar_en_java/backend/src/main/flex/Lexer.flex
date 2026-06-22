import java_cup.runtime.Symbol;

%%

%class Lexer
%cup
%unicode
%line
%column

/* Expresiones regulares */
WhiteSpace = [ \t\r\n]+
Number     = [0-9]+
Identifier = [a-zA-Z_][a-zA-Z0-9_]*

%%

/* Reglas lexicas */
{WhiteSpace} { /* Ignorar espacios en blanco */ }

"+"          { System.out.println("[TOKEN]MAS|+|IDENTIFICADO"); return new Symbol(sym.MAS, yyline, yycolumn); }
"-"          { System.out.println("[TOKEN]MENOS|-|IDENTIFICADO"); return new Symbol(sym.MENOS, yyline, yycolumn); }
"="          { System.out.println("[TOKEN]ASIGNACION|=|IDENTIFICADO"); return new Symbol(sym.ASIGNACION, yyline, yycolumn); }

{Number}     { System.out.println("[TOKEN]NUMERO|" + yytext() + "|IDENTIFICADO"); return new Symbol(sym.NUMBER, yyline, yycolumn, yytext()); }
{Identifier} { System.out.println("[TOKEN]IDENTIFICADOR|" + yytext() + "|IDENTIFICADO"); return new Symbol(sym.ID, yyline, yycolumn, yytext()); }

/* Manejo de errores */
.            { String c = yytext(); System.out.println("[TOKEN]ERROR|" + c + "|NO IDENTIFICADO"); System.out.println("Error lexico en la linea " + (yyline+1) + ", columna " + (yycolumn+1) + ": Caracter no reconocido '" + c + "'"); }
