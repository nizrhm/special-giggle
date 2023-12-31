# lex_state_norule.py
#
# Declaration of a state for which no rules are defined

import ply.lex as lex

tokens = [ 
    "PLUS",
    "MINUS",
    "NUMBER",
    ]

states = (('comment', 'exclusive'),
          ('example', 'exclusive'))

t_PLUS = r'\+'
t_MINUS = r'-'
t_NUMBER = r'\d+'

# Comments
def t_comment(t):
    r'/\*'
    t.lexer.begin('comment')
    print("Entering comment state")

def t_comment_body_part(t):
    r'(.|\n)*\*/'
    print("comment body %s" % t)
    t.lexer.begin('INITIAL')

def t_error(t):
    pass


lex.lex()


