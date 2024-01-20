# Regex Engine
 A Regex Engine from scratch written in python

## 

A Program that should implement the basics of Regular Expressions

To Implement are:

     - Groups       '(.....)'
     - Class        '[.....]'
     - Range        '[a-z..]'
     - Or           '...|...'
     - Wildcard     '.......'
     - Zero-Inf     '......*'
     - One-Inf      '......+'
     - Zero-One     '......?'
     - Escaped      '\\d \\w'
     - From Start   '^......'
     - From End     '......$'


Grammar:

     - regex     - '^'? expr '$'?
     - expr      -  ( alternate | set | '\' chr | chr | '(' expr ')' ) operator?
     - set       -  '[' ( chr '-' chr | chr )+ ']'
     - alternate -  '('   expr ( '|' expr )*   ')'
     - operator  -  '*' | '+' | '?'