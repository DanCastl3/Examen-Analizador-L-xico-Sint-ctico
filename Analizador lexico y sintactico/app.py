import ply.lex as lex
import ply.yacc as yacc
from flask import Flask, render_template, request

app = Flask(__name__)

# Definición de tokens reservados
reserved = {
    'include': 'INCLUDE',
    'iostream': 'IOSTREAM',
    'using': 'USING',
    'namespace': 'NAMESPACE',
    'return': 'RETURN',
}

# Definición de tokens
tokens = [
    'PABIERTO', 'PCERRADO', 'LLAVE_ABIERTA', 'LLAVE_CERRADA',
    'OPERADOR', 'SIMBOLO', 'ID', 'CADENA', 'NUMERO', 'COMA',
    'MAS', 'MENOS', 'POR', 'DIVIDIDO', 'INT', 'COUT', 'COUNT', 'IGNORENAME'
] + list(reserved.values())

# Definiciones de expresiones regulares para los tokens
t_PABIERTO = r'\('
t_PCERRADO = r'\)'
t_LLAVE_ABIERTA = r'\{'
t_LLAVE_CERRADA = r'\}'
t_COMA = r','
t_SIMBOLO = r';'
t_CADENA = r'"[^"]*"'
t_OPERADOR = r'='
t_MAS = r'\+'
t_MENOS = r'-'
t_POR = r'\*'
t_DIVIDIDO = r'/'
t_INT = r'int'
t_COUT = r'cout'
t_COUNT = r'count'
t_IGNORENAME = r'usingname'
t_ignore = ' \t'

# Manejo de líneas
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)  

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_NUMERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_error(t):
    print(f"Carácter ilegal '{t.value[0]}' en la línea {t.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()

# Reglas gramaticales
def p_declaraciones(p):
    '''declaraciones : declaracion declaraciones
                     | operacion declaraciones
                     | imprimir declaraciones
                     | empty'''
    pass

def p_declaracion(p):
    'declaracion : INT ID SIMBOLO'
    pass

def p_expresion(p):
    '''expresion : NUMERO
                  | ID
                  | expresion MAS expresion
                  | expresion MENOS expresion
                  | expresion POR expresion
                  | expresion DIVIDIDO expresion'''
    pass

def p_operacion(p):
    'operacion : expresion SIMBOLO'
    pass

def p_imprimir(p):
    '''imprimir : COUNT PABIERTO CADENA PCERRADO SIMBOLO
                 | COUT PABIERTO CADENA PCERRADO SIMBOLO'''
    pass

def p_empty(p):
    '''empty :'''
    pass

def p_error(p):
    if p:
        print(f"Error de sintaxis en el token '{p.type}' en la línea {p.lineno}")
    else:
        print("Error de sintaxis al final del archivo")

parser = yacc.yacc()

# Función para analizar el código y reportar errores
def analizar_codigo(codigo):
    lexer.input(codigo)
    for tok in lexer:
        print(f"Token: {tok.type}, Valor: {tok.value}, Línea: {tok.lineno}")
    result = parser.parse(codigo)
    if result is None:
        print("Análisis sintáctico completado")

# Estructura base esperada
estructura_base = """#include <iostream>
usingname namespace std;
int main() {
   count << "Hello, World!";
   return 0;
}"""

# Función para obtener tokens de un código
def obtener_tokens(codigo):
    lexer.input(codigo)
    tokens = []
    while True:
        token = lexer.token()
        if not token:
            break
        tokens.append((token.type, token.value, token.lineno))
    return tokens

def comparar_tokens(tokens_esperados, tokens_entrada):
    errores = []
    len_tokens_esperados = len(tokens_esperados)
    len_tokens_entrada = len(tokens_entrada)

    for i in range(min(len_tokens_esperados, len_tokens_entrada)):
        if tokens_esperados[i][0] != tokens_entrada[i][0]:
            # Ajuste para mostrar la línea del token que realmente se está analizando
            errores.append(f"Error: Se esperaba el token '{tokens_esperados[i][1]}' en la línea {tokens_entrada[i][2]}")
            return errores

    if len_tokens_entrada < len_tokens_esperados:
        # Ajuste para la línea correcta cuando falta un token
        errores.append(f"Error: Falta el token '{tokens_esperados[len_tokens_entrada][1]}' en la línea {tokens_esperados[len_tokens_entrada][2]}")
        return errores

    if len_tokens_entrada > len_tokens_esperados:
        # Ajuste para la línea correcta cuando hay un token inesperado
        errores.append(f"Error: El token '{tokens_entrada[len_tokens_esperados][1]}' en la línea {tokens_entrada[len_tokens_esperados][2]} no es esperado")
        return errores

    return []


def analizar_sintaxis(expresion):
    try:
        result = parser.parse(expresion, lexer=lexer)
    except Exception as e:
        return str(e)

    tokens_entrada = obtener_tokens(expresion)
    tokens_esperados = obtener_tokens(estructura_base)

    errores = comparar_tokens(tokens_esperados, tokens_entrada)
    
    if errores:
        return errores[0]
    
    return "Análisis sintáctico completado."

# Ruta principal para la aplicación Flask
@app.route('/', methods=['GET', 'POST'])
def index():
    contador = {
        'RESERVADO': 0,
        'IDENTIFICADOR': 0,
        'PARENTESIS': 0,
        'DELIMITADOR': 0,
        'OPERADOR': 0,
        'SIMBOLO': 0,
        'NUMERO': 0,
        'CADENA': 0
    }
    
    result_lexema = []
    mensaje_sintaxis = ""

    if request.method == 'POST':
        expresion = request.form.get('Expresion')
        lexer.lineno = 1
        
        mensaje_sintaxis = analizar_sintaxis(expresion)

        lexer.input(expresion)
        
        for token in lexer:
            if token.type in reserved.values():
                result_lexema.append(("RESERVADO", token.value, token.lineno))
                contador['RESERVADO'] += 1
            elif token.type == "ID":
                result_lexema.append(("IDENTIFICADOR", token.value, token.lineno))
                contador['IDENTIFICADOR'] += 1
            elif token.type in ["PABIERTO", "PCERRADO"]:
                result_lexema.append(("PARENTESIS", token.value, token.lineno))
                contador['PARENTESIS'] += 1
            elif token.type in ["LLAVE_ABIERTA", "LLAVE_CERRADA"]:
                result_lexema.append(("DELIMITADOR", token.value, token.lineno))
                contador['DELIMITADOR'] += 1
            elif token.type in ["MAS", "MENOS", "POR", "DIVIDIDO"]:
                result_lexema.append(("OPERADOR", token.value, token.lineno))
                contador['OPERADOR'] += 1
            elif token.type == "SIMBOLO":
                result_lexema.append(("SIMBOLO", token.value, token.lineno))
                contador['SIMBOLO'] += 1
            elif token.type == "NUMERO":
                result_lexema.append(("NUMERO", token.value, token.lineno))
                contador['NUMERO'] += 1
            elif token.type == "CADENA":
                result_lexema.append(("CADENA", token.value, token.lineno))
                contador['CADENA'] += 1
        
        return render_template('index.html', tokens=result_lexema, contador=contador, expresion=expresion, mensaje_sintaxis=mensaje_sintaxis)
    
    return render_template('index.html', tokens=[], contador=contador, expresion=None, mensaje_sintaxis="")

if __name__ == '__main__':
    app.run(debug=True)


