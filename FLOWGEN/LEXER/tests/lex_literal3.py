# lex_literal3.py
#
# An empty literal specification given as a list
# Issue 8 : Literals empty list causes IndexError

import ply.lex as lex

tokens = [
    "NUMBER",
    ]

literals = []

def t_NUMBER(t):
    r'\d+'
    return t

def t_error(t):
    pass

lex.lex()


