# testlex.py

import unittest
try:
    import StringIO
except ImportError:
    import io as StringIO

import sys
import os
import warnings
import platform

sys.tracebacklimit = 0

import ply.lex

try:
    from importlib.util import cache_from_source
except ImportError:
    # Python 2.7, but we don't care.
    cache_from_source = None


def make_pymodule_path(filename, optimization=None):
    path = os.path.dirname(filename)
    file = os.path.basename(filename)
    mod, ext = os.path.splitext(file)

    if sys.hexversion >= 0x3050000:
        fullpath = cache_from_source(filename, optimization=optimization)
    elif sys.hexversion >= 0x3040000:
        fullpath = cache_from_source(filename, ext=='.pyc')
    elif sys.hexversion >= 0x3020000:
        import imp
        modname = mod+"."+imp.get_tag()+ext
        fullpath = os.path.join(path,'__pycache__',modname)
    else:
        fullpath = filename
    return fullpath

def pymodule_out_exists(filename, optimization=None):
    return os.path.exists(make_pymodule_path(filename,
                                             optimization=optimization))

def pymodule_out_remove(filename, optimization=None):
    os.remove(make_pymodule_path(filename, optimization=optimization))

def implementation():
    if platform.system().startswith("Java"):
        return "Jython"
    elif hasattr(sys, "pypy_version_info"):
        return "PyPy"
    else:
        return "CPython"

test_pyo = (implementation() == 'CPython')

def check_expected(result, expected, contains=False):
    if sys.version_info[0] >= 3:
        if isinstance(result,str):
            result = result.encode('ascii')
        if isinstance(expected,str):
            expected = expected.encode('ascii')
    resultlines = result.splitlines()
    expectedlines = expected.splitlines()

    if len(resultlines) != len(expectedlines):
        return False

    for rline,eline in zip(resultlines,expectedlines):
        if contains:
            if eline not in rline:
                return False
        else:
            if not rline.endswith(eline):
                return False
    return True

def run_import(module):
    code = "import "+module
    exec(code)
    del sys.modules[module]
    
# Tests related to errors and warnings when building lexers
class LexErrorWarningTests(unittest.TestCase):
    def setUp(self):
        sys.stderr = StringIO.StringIO()
        sys.stdout = StringIO.StringIO()
        if sys.hexversion >= 0x3020000:
            warnings.filterwarnings('ignore',category=ResourceWarning)

    def tearDown(self):
        sys.stderr = sys.__stderr__
        sys.stdout = sys.__stdout__
    def test_lex_doc1(self):
        self.assertRaises(SyntaxError,run_import,"lex_doc1")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                              "lex_doc1.py:15: No regular expression defined for rule 't_NUMBER'\n"))
    def test_lex_dup1(self):
        self.assertRaises(SyntaxError,run_import,"lex_dup1")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "lex_dup1.py:17: Rule t_NUMBER redefined. Previously defined on line 15\n" ))        
        
    def test_lex_dup2(self):
        self.assertRaises(SyntaxError,run_import,"lex_dup2")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "lex_dup2.py:19: Rule t_NUMBER redefined. Previously defined on line 15\n" ))
            
    def test_lex_dup3(self):
        self.assertRaises(SyntaxError,run_import,"lex_dup3")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "lex_dup3.py:17: Rule t_NUMBER redefined. Previously defined on line 15\n" ))

    def test_lex_empty(self):
        self.assertRaises(SyntaxError,run_import,"lex_empty")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "No rules of the form t_rulename are defined\n"
                                    "No rules defined for state 'INITIAL'\n"))

    def test_lex_error1(self):
        run_import("lex_error1")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "No t_error rule is defined\n"))

    def test_lex_error2(self):
        self.assertRaises(SyntaxError,run_import,"lex_error2")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "Rule 't_error' must be defined as a function\n")
                     )

    def test_lex_error3(self):
        self.assertRaises(SyntaxError,run_import,"lex_error3")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "lex_error3.py:17: Rule 't_error' requires an argument\n"))

    def test_lex_error4(self):
        self.assertRaises(SyntaxError,run_import,"lex_error4")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "lex_error4.py:17: Rule 't_error' has too many arguments\n"))

    def test_lex_ignore(self):
        self.assertRaises(SyntaxError,run_import,"lex_ignore")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "lex_ignore.py:17: Rule 't_ignore' must be defined as a string\n"))

    def test_lex_ignore2(self):
        run_import("lex_ignore2")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "t_ignore contains a literal backslash '\\'\n"))


    def test_lex_re1(self):
        self.assertRaises(SyntaxError,run_import,"lex_re1")
        result = sys.stderr.getvalue()
        if sys.hexversion < 0x3050000:
            msg = "Invalid regular expression for rule 't_NUMBER'. unbalanced parenthesis\n"
        else:
            msg = "Invalid regular expression for rule 't_NUMBER'. missing ), unterminated subpattern at position 0"
        self.assertTrue(check_expected(result,
                                    msg,
                                    contains=True))

    def test_lex_re2(self):
        self.assertRaises(SyntaxError,run_import,"lex_re2")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "Regular expression for rule 't_PLUS' matches empty string\n"))

    def test_lex_re3(self):
        self.assertRaises(SyntaxError,run_import,"lex_re3")
        result = sys.stderr.getvalue()
#        self.assertTrue(check_expected(result,
#                                    "Invalid regular expression for rule 't_POUND'. unbalanced parenthesis\n"
#                                    "Make sure '#' in rule 't_POUND' is escaped with '\\#'\n"))

        if sys.hexversion < 0x3050000:
            msg = ("Invalid regular expression for rule 't_POUND'. unbalanced parenthesis\n"
                   "Make sure '#' in rule 't_POUND' is escaped with '\\#'\n")
        else:
            msg = ("Invalid regular expression for rule 't_POUND'. missing ), unterminated subpattern at position 0\n"
                   "ERROR: Make sure '#' in rule 't_POUND' is escaped with '\#'")
        self.assertTrue(check_expected(result,
                                    msg,
                                    contains=True), result)

    def test_lex_rule1(self):
        self.assertRaises(SyntaxError,run_import,"lex_rule1")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "t_NUMBER not defined as a function or string\n"))

    def test_lex_rule2(self):
        self.assertRaises(SyntaxError,run_import,"lex_rule2")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "lex_rule2.py:15: Rule 't_NUMBER' requires an argument\n"))

    def test_lex_rule3(self):
        self.assertRaises(SyntaxError,run_import,"lex_rule3")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "lex_rule3.py:15: Rule 't_NUMBER' has too many arguments\n"))


    def test_lex_state1(self):
        self.assertRaises(SyntaxError,run_import,"lex_state1")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                   "states must be defined as a tuple or list\n"))

    def test_lex_state2(self):
        self.assertRaises(SyntaxError,run_import,"lex_state2")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "Invalid state specifier 'comment'. Must be a tuple (statename,'exclusive|inclusive')\n"
                                    "Invalid state specifier 'example'. Must be a tuple (statename,'exclusive|inclusive')\n"))

    def test_lex_state3(self):
        self.assertRaises(SyntaxError,run_import,"lex_state3")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "State name 1 must be a string\n"
                                    "No rules defined for state 'example'\n"))

    def test_lex_state4(self):
        self.assertRaises(SyntaxError,run_import,"lex_state4")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "State type for state 'comment' must be 'inclusive' or 'exclusive'\n"))


    def test_lex_state5(self):
        self.assertRaises(SyntaxError,run_import,"lex_state5")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "State 'comment' already defined\n"))

    def test_lex_state_noerror(self):
        run_import("lex_state_noerror")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "No error rule is defined for exclusive state 'comment'\n"))    

    def test_lex_state_norule(self):
        self.assertRaises(SyntaxError,run_import,"lex_state_norule")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "No rules defined for state 'example'\n"))

    def test_lex_token1(self):
        self.assertRaises(SyntaxError,run_import,"lex_token1")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "No token list is defined\n"
                                    "Rule 't_NUMBER' defined for an unspecified token NUMBER\n"
                                    "Rule 't_PLUS' defined for an unspecified token PLUS\n"
                                    "Rule 't_MINUS' defined for an unspecified token MINUS\n"
))

    def test_lex_token2(self):
        self.assertRaises(SyntaxError,run_import,"lex_token2")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "tokens must be a list or tuple\n"
                                    "Rule 't_NUMBER' defined for an unspecified token NUMBER\n"
                                    "Rule 't_PLUS' defined for an unspecified token PLUS\n"
                                    "Rule 't_MINUS' defined for an unspecified token MINUS\n"
))
    
    def test_lex_token3(self):
        self.assertRaises(SyntaxError,run_import,"lex_token3")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "Rule 't_MINUS' defined for an unspecified token MINUS\n"))


    def test_lex_token4(self):
        self.assertRaises(SyntaxError,run_import,"lex_token4")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "Bad token name '-'\n"))


    def test_lex_token_dup(self):
        run_import("lex_token_dup")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "Token 'MINUS' multiply defined\n"))   

        
    def test_lex_literal1(self):
        self.assertRaises(SyntaxError,run_import,"lex_literal1")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "Invalid literal '**'. Must be a single character\n"))

    def test_lex_literal2(self):
        self.assertRaises(SyntaxError,run_import,"lex_literal2")
        result = sys.stderr.getvalue()
        self.assertTrue(check_expected(result,
                                    "Invalid literals specification. literals must be a sequence of characters\n"))

import os
import subprocess
import shutil

# Tests related to various build options associated with lexers
class LexBuildOptionTests(unittest.TestCase):
    def setUp(self):
        sys.stderr = StringIO.StringIO()
        sys.stdout = StringIO.StringIO()
    def tearDown(self):
        sys.stderr = sys.__stderr__
        sys.stdout = sys.__stdout__
        try:
            shutil.rmtree("lexdir")
        except OSError:
            pass

    def test_lex_module(self):
        run_import("lex_module")
        result = sys.stdout.getvalue()
        self.assertTrue(check_expected(result,
                                    "(NUMBER,3,1,0)\n"
                                    "(PLUS,'+',1,1)\n"
                                    "(NUMBER,4,1,2)\n"))
        
    def test_lex_object(self):
        run_import("lex_object")
        result = sys.stdout.getvalue()
        self.assertTrue(check_expected(result,
                                    "(NUMBER,3,1,0)\n"
                                    "(PLUS,'+',1,1)\n"
                                    "(NUMBER,4,1,2)\n"))

    def test_lex_closure(self):
        run_import("lex_closure")
        result = sys.stdout.getvalue()
        self.assertTrue(check_expected(result,
                                    "(NUMBER,3,1,0)\n"
                                    "(PLUS,'+',1,1)\n"
                                    "(NUMBER,4,1,2)\n"))

    def test_lex_many_tokens(self):
        run_import("lex_many_tokens")
        result = sys.stdout.getvalue()
        self.assertTrue(check_expected(result,
                                    "(TOK34,'TOK34:',1,0)\n"
                                    "(TOK143,'TOK143:',1,7)\n"
                                    "(TOK269,'TOK269:',1,15)\n"
                                    "(TOK372,'TOK372:',1,23)\n"
                                    "(TOK452,'TOK452:',1,31)\n"
                                    "(TOK561,'TOK561:',1,39)\n"
                                    "(TOK999,'TOK999:',1,47)\n"
                                    ))
        
# Tests related to run-time behavior of lexers
class LexRunTests(unittest.TestCase):
    def setUp(self):
        sys.stderr = StringIO.StringIO()
        sys.stdout = StringIO.StringIO()
    def tearDown(self):
        sys.stderr = sys.__stderr__
        sys.stdout = sys.__stdout__

    def test_lex_hedit(self):
        run_import("lex_hedit")
        result = sys.stdout.getvalue()
        self.assertTrue(check_expected(result,
                                    "(H_EDIT_DESCRIPTOR,'abc',1,0)\n"
                                    "(H_EDIT_DESCRIPTOR,'abcdefghij',1,6)\n"
                                    "(H_EDIT_DESCRIPTOR,'xy',1,20)\n"))
       
    def test_lex_state_try(self):
        run_import("lex_state_try")
        result = sys.stdout.getvalue()
        self.assertTrue(check_expected(result,
                                    "(NUMBER,'3',1,0)\n"
                                    "(PLUS,'+',1,2)\n"
                                    "(NUMBER,'4',1,4)\n"
                                    "Entering comment state\n"
                                    "comment body LexToken(body_part,'This is a comment */',1,9)\n"
                                    "(PLUS,'+',1,30)\n"
                                    "(NUMBER,'10',1,32)\n"
                                    ))    



unittest.main()
