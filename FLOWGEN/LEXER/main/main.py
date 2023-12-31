from ply.lex import lex
from ply.yacc import yacc
from code_generator import compile_to_c_code

keywords = {
    'program': 'PROGRAM',
    'var': 'VAR',
    'begin': 'BEGIN',
    'end': 'END',
    'int': 'INT',
    'real': 'REAL',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'while': 'WHILE',
    'do': 'DO',
    'print': 'PRINT',
    'and': 'AND',
    'or': 'OR',
    'mod': 'MOD',
    'not': 'NOT'
}
tokens = (
    # 'real' is commented
    'PROGRAM', 'VAR', 'INT', "REAL", 'BEGIN', 'END', 'IF', 'THEN', 'ELSE', 'WHILE', 'PRINT',
    'AND', 'OR',
    'MOD', 'NOT', 'ASSIGN', 'PLUS', 'MINUS', 'MULT', 'DIVIDE', 'GT', 'LT', 'EQ', 'NEQ', 'GTEQ', 'LTEQ',
    'IDENTIFIER', 'INTEGERCONSTANT','REALCONSTANT', 'SEMICOLON', 'COLON', 'COMMA', 'LPAREN', 'RPAREN', 'DO')
# Ignored characters
t_ignore = ' \t'

# Token matching rules are written as regexs
t_PROGRAM = r'program'
t_VAR = r'var'
t_INT = r'int'
t_REAL = r'real'
t_BEGIN = r'begin'
t_END = r'end'
t_IF = r'if'
t_THEN = r'then'
t_ELSE = r'else'
t_WHILE = r'while'
t_PRINT = r'print'
t_AND = r'and'
t_OR = r'or'
t_MOD = r'mod'
t_NOT = r'not'
t_DO = r'do'
t_ASSIGN = r'[:]{1}[=]{1}'
t_PLUS = r'\+'
t_MINUS = r'\-'
t_MULT = r'\*'
t_DIVIDE = r'\/'
t_GT = r'>'
t_LT = r'<'
t_EQ = r'='
t_NEQ = r'[<]{1}[>]{1}'
t_GTEQ = r'[>]{1}[=]{1}'
t_LTEQ = r'[<]{1}[=]{1}'
t_SEMICOLON = r'\;'
t_COLON = r'\:'
t_COMMA = r'\,'
t_LPAREN = r'\('
t_RPAREN = r'\)'

def t_REALCONSTANT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_INTEGERCONSTANT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = keywords.get(t.value, 'IDENTIFIER')  # Check for reserved words
    return t

# Ignored token with an action associated with it
def t_ignore_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')


# Error handler for illegal characters
def t_error(t):
    print(f'Illegal character {t.value[0]!r}')
    t.lexer.skip(1)

temp_counter = 0
def new_temp():
    global temp_counter
    temp_counter += 1
    return f"T_{temp_counter}"



# Build the lexer object
lexer = lex()

precedence = (
    ('right', 'OR'),
    ('right', 'AND'),
    ('right', 'PLUS', 'MINUS'),
    ('right', 'MULT', 'DIVIDE', 'MOD'),
    ('right', 'UNOT'),
    ('nonassoc', 'GT', 'LT', 'EQ', 'NEQ', 'GTEQ', 'LTEQ'),

    ('right', 'UMINUS'),
)

class Quadruple:
    def __init__(self, op, left, right, result):
        self.op = op
        self.left = left
        self.right = right
        self.result = result


quadruples = []
symbol_table = {}
var_symbols = {'int': [], 'float': []}

def backpatch(quad_list, label):
    for i in quad_list:
        quadruples[i-1].result = label

def nextinstr():
    return len(quadruples) + 1


class E:
    def __init__(self, trueList, falseList, place, type):
        self['trueList'] = trueList
        self['falseList'] = falseList
        self['place'] = place
        self.type = type

def p_marker(t):
    'marker : '
    t[0] = nextinstr()

def p_endmarker(t):
    'endmarker : '
    nextList = [nextinstr()]

    q = Quadruple('GOTO', None, None, None)
    quadruples.append(q)
    t[0] = {'next': nextList,"inst":q}
    


def p_program(t):
    'program : PROGRAM IDENTIFIER declarations compoundstatement'
    pass
    # print('shit', t[1])

def p_declarations(t):
    '''declarations : VAR declarationlist 
                    | empty
    '''
    pass

def p_empty(p):
     'empty :'
     pass

def p_declarationlist(t):
    '''
    declarationlist : identifierlist COLON type
                    | declarationlist SEMICOLON identifierlist COLON type
    '''
    if len(t) == 4:
        var_symbols[t[3]]+=t[1]['var_name']
    else:
        var_symbols[t[5]]+=t[3]['var_name']
    pass


def p_identifierlist(t):
    '''
    identifierlist : IDENTIFIER
                   | identifierlist COMMA IDENTIFIER
    '''
    if len(t) == 2:
        t[0] = {'var_name': [t[1]]}
    else:
        t[0] = {'var_name' : t[1]['var_name']+[t[3]]}
def p_type(t):
    '''
    type : INT
        | REAL
    '''
    if t[1] == 'int':
        t[0] = 'int'
    else:
        t[0] = 'float'


def p_compoundstatement(t):
    'compoundstatement : BEGIN statementlist END'

    # t[0] = Quadruple("begin_block", None, None, None)
    # nextInstruction = nextinstr()
    # backpatch(t[2]['next'], nextInstruction)
    # t[0] = { 'next' : t[2]['next'] }
    t[0] = t[2]
    # print('here is t[0]', t[0])
    # backpatch(t[0]['next'], nextinstr())


def p_statementlist(t):
    '''statementlist : statement 
                     | statementlist SEMICOLON statement
    '''
    pass
    if len(t) == 2:
        # print("here is t[1]", t[1])
        t[0] = t[1]
    else:
        t[1]['next'] = t[3]['next']
        t[0] = t[1]

def p_statement(t):
    '''
    statement : compoundstatement                           
    '''
    # TODO for know while statement is commented
            #   | WHILE expression DO statement
    nextStatement = t[1]['next']
    t[0] = {'next': nextStatement}

def p_statement_print(t):
    '''
    statement : PRINT LPAREN expression RPAREN              
    '''
    result = f"print({t[3]['place']})"
    # print("here is print result")
    quadruples.append(Quadruple("print", None, None, t[3]['place']))

    # TODO for know while statement is commented
            #   | WHILE expression DO statement
    nextInstr = [nextinstr()]
    t[0] = {'next': nextInstr}



def p_statement_assign(t):
    'statement : IDENTIFIER ASSIGN expression'
    result = t[1]
    # print("here is t3", t[3])
    quadruples.append(Quadruple("=", t[3]['place'], None, result))

    nextInstr = [nextinstr()]
    t[0] = {'place': result, 'trueList': [], 'falseList':[], 'next': nextInstr}


def p_while_statement(t):
    'statement : WHILE marker expression DO marker statement'
    backpatch(t[3]["falseList"],nextinstr()+1)
    backpatch(t[3]["trueList"], t[5])
    t[0] = {'next':t[3]['falseList']}
    quadruples.append(Quadruple("GOTO",None,None,t[2]))
def p_if_else_statement(t):
    'statement : IF expression THEN marker statement endmarker ELSE marker statement'
    print("AAAAAAAA")
    # t[0] = f"IF {t[2]} THEN marker {t[5]}; IF NOT {t[2]} THEN marker {t[9]}"
    backpatch(t[2]['trueList'], t[4])
    backpatch(t[2]['falseList'], t[8])
    t[6]['inst'].result = nextinstr()
    nextList = t[5]['next'] + t[6]['next'] + t[9]['next']
    t[0] = {'next': nextList}



def p_if_statement(t):
    'statement : IF expression THEN marker statement'
    # t[4] is newinstr
    print("VVVVVVVV")
    backpatch(t[2]['trueList'], t[4])
    backpatch(t[2]['falseList'], nextinstr())
    nextList = t[5]['next'] + t[2]['falseList']
    t[0] = {'next': nextList}

def p_expression(t):
    '''
    expression : LPAREN expression RPAREN
    '''
    trueList = t[2]['trueList']
    falseList = t[2]['falseList']
    result = t[2]['place']
    nextInstr = [nextinstr()]
    t[0] = {'place': result, 'type':'expression', 'trueList': trueList, 'falseList': falseList, 'next': nextInstr}


def p_expression_int(t):
    '''
    expression : INTEGERCONSTANT
               | IDENTIFIER
               | REALCONSTANT
    '''
    # generate backpatching code
    result = new_temp()
    quadruples.append(Quadruple('=', t[1], None, result))
    trueList = []
    falseList = []

    t[0] = {'place': result, 'type': 'expression', 'trueList': trueList, 'falseList': falseList}

def p_expression_plus(t):
    '''
    expression : expression PLUS expression    
    '''
    result = new_temp()
    quadruples.append(Quadruple('+', t[1]['place'], t[3]['place'], result))
    t[0] = {'place': result, 'type': 'expression', 'trueList': [], 'falseList': []}

def p_expression_minus(t):
    '''
    expression : expression MINUS expression    
    '''
    result = new_temp()
    quadruples.append(Quadruple('-', t[1]['place'], t[3]['place'], result))
    t[0] = {'place': result, 'type': 'expression', 'trueList': [], 'falseList': []}

def p_expression_mult(t):
    '''
    expression : expression MULT expression    
    '''
    result = new_temp()
    quadruples.append(Quadruple('*', t[1]['place'], t[3]['place'], result))
    t[0] = {'place': result, 'type': 'expression', 'trueList': [], 'falseList': []}

def p_expression_divide(t):
    '''
    expression : expression DIVIDE expression    
    '''
    result = new_temp()
    quadruples.append(Quadruple('/', t[1]['place'], t[3]['place'], result))
    t[0] = {'place': result, 'type': 'expression', 'trueList': [], 'falseList': []}

def p_expression_mod(t):
    '''
    expression : expression MOD expression    
    '''
    result = new_temp()
    quadruples.append(Quadruple('%', t[1]['place'], t[3]['place'], result))
    t[0] = {'place': result, 'type': 'expression', 'trueList': [], 'falseList': []}


def p_expression_and(t):
    '''
    expression : expression AND marker expression
    '''
    # t[3] is nextinstruction line
    # there is no need to marker since
    # we can calling nextintr func directly
    result = new_temp()
    quadruples.append(Quadruple('and', t[1]['place'], t[4]['place'], result))


    backpatch(t[1]['trueList'], t[3])
    trueList = t[4]['trueList']
    falseList = t[1]['falseList'] + t[4]['falseList']

    t[0] = {'place': result, 'type': 'expression', 'trueList': trueList, 'falseList': falseList}

def p_expression_or(t):
    '''
    expression : expression OR marker expression
    '''
    # t[3] is nextinstruction line
    # there is no need to marker since
    # we can calling nextintr func directly
    result = new_temp()
    quadruples.append(Quadruple('or', t[1]['place'], t[4]['place'], result))

    backpatch(t[1]['falseList'], t[3])
    trueList = t[1]['trueList'] + t[4]['trueList']
    falseList = t[4]['falseList']

    t[0] = {'place': result, 'type': 'expression', 'trueList': trueList, 'falseList': falseList}


def p_expression_not(t):
    '''
    expression : NOT expression %prec UNOT
    '''
    print("PPPPPPPPP")
    result = new_temp()
    quadruples.append(Quadruple('not', t[2]['place'], None, result))

    trueList = t[2]['trueList']
    falseList = t[2]['falseList']
    t[0] = {'place':result, 'type': 'expression', 'trueList': falseList, 'falseList': trueList}

def p_expression_relop(t):
    '''
    expression : expression LT expression      
               | expression EQ expression      
               | expression GT expression      
               | expression NEQ expression     
               | expression LTEQ expression    
               | expression GTEQ expression         
    '''

    # result = new_temp()
    # quadruples.append(Quadruple(t[2], t[1]['place'], t[3]['place'], result))
    # t[0] = {'place': result, 'type': 'expression', 'trueList': [], 'falseList': []}

    nextInstruction = nextinstr()
    trueList = [nextInstruction]
    falseList = [nextInstruction+1]

    quadruples.append(Quadruple(f'if GOTO', f'{t[1]["place"]} {t[2]} {t[3]["place"]}', None, None))
    quadruples.append(Quadruple(f'GOTO', None, None, None))

    t[0] = {'place':f'{t[1]["place"]} {t[2]} {t[3]["place"]}', 'type': 'expression', 'trueList': trueList, 'falseList': falseList}


def p_expression_minus(t):
    '''
    expression : MINUS expression %prec UMINUS 
    '''
    result = new_temp()
    quadruples.append(Quadruple('-', '0', t[2]['place'], result))
    t[0] = {'place': result, 'type': 'expression', 'trueList': [], 'falseList': []}



# Build the parser
parser = yacc(start="program")

# Parse an expression


# try:
    # s = input('calc > ')
    # if not s:

def read_file(filename):
    with open(filename, 'r') as f:
        return f.read()
s = read_file(input.txt)

'''s = "program shit" \
    " var a,b:int;" \
     " c,d:real" \
     " begin" \
     " c:=1;"\
     " d:=10;"\
     " while c<d " \
     "do c:=c+1;" \
     "print(c);"\
     " end;"'''

# except EOFError:
#     print("error")
#     break
lexer.input(s)
# Tokenize
while True:
    tok = lexer.token()
    if not tok:
        break  # No more input
    # print(tok)
# print("$")
# print(s)
# print("#############")
r = parser.parse(s)
# print("===============")
# for quad in quadruples:
#     print(f'{quad.result} {quad.op} {quad.left} {quad.right}')
# print("===============")
# print("variables:",var_symbols)
print(compile_to_c_code(quadruples, var_symbols,temp_counter))

