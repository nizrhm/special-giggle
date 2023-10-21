%{
    #include<stdio.h>
    int yylineno = 1;
%}

letter [a-zA-z]
digit [0-9]

%%
\n                                                   yylineno++;
#include<{letter}+(\.{letter}*)?>                    printf("%d\t%s\t\tPREPROCESSOR\n", yylineno,yytext);
return|main|for|while|case|switch|if|else|and|or|not|try|except|finally|raise|assert|None|True|False|class|def|from|import|as|with|yield|global|lambda|nonlocal|in|is|del|elif|pass|break|continue|try|except|finally|elif|pass|break|continue            printf("%d\t%s\t\tKEYWORD\n", yylineno,yytext);
int|float|chat|struct                                printf("%d\t%s\t\tDATATYPE\n", yylineno,yytext);
\(                                                   printf("%d\t%s\t\tBRACKET OPEN\n", yylineno,yytext);
\)                                                   printf("%d\t%s\t\tBRACKET CLOSE\n", yylineno,yytext);
{letter}({letter}|{digit})*                          printf("%d\t%s\t\tIDENTIFIER\n", yylineno,yytext);
{digit}+                                             printf("%d\t%s\t\tINTEGER\n", yylineno,yytext);
\{                                                   printf("%d\t%s\t\tBRACE OPEN\n", yylineno,yytext);
\}                                                   printf("%d\t%s\t\tBRACE CLOSE\n", yylineno,yytext);
{digit}+"E"(\+|\-)?{digit}+                          printf("%d\t%s\t\tREAL NUMBER\n", yylineno,yytext);
{digit}+\.{digit}+(E(\+|\-)?{digit}+)?               printf("%d\t%s\t\tFLOATING NUMBER\n", yylineno,yytext);
=                                                    printf("%d\t%s\t\tASSIGNMENT\n", yylineno,yytext);                                                    
;                                                    printf("%d\t%s\t\tTERMINATOR\n", yylineno,yytext);
\t                                                   ;
" "                                                  ;
\"({letter}|{digit}|" ")*\"                          printf("%d\t%s\t\tSTRING CONSTANT\n", yylineno,yytext);




%%

int yywrap(){
    return 1;
}

int main(){
    FILE* inputFile = fopen("F:\\VS CODE REPOS WIN11\\special-giggle\\testing\\input_code_file.py", "r");
    if (inputFile == NULL) {
        printf("Unable to open the input Python file.\n");
        return 1;
    }
    printf("LINE\tLEXEME\t\t\t\tTOKEN\n");
    yyin = inputFile;
    yylex();
    fclose(yyin);
    return 0;
}

