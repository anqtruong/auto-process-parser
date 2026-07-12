lexer grammar lexerRules;

//Operator Rules
OPERATOR : OR | AND | EQ | NEQ | G | L | GEQ | LEQ | ADD | SUB | MUL | DIV;
OR : '|';
AND : '&';
EQ : '==' | '=';
NEQ : '!=';
G : '>';
L : '<';
GEQ : '>=';
LEQ : '<=';
ADD : '+';
SUB : '-';
MUL : '*';
DIV : '/';

BOOL : TRUE | FALSE ;
TRUE: 'on' ;
FALSE : 'off' ;

//Lexer rules from dissertation (pg.35)
INT : [0-9]+;
ID : ('a'..'z' | 'A'..'Z') ('a'..'z' | 'A'..'Z' | '0'..'9' | '_' )*;
DOUBLE : INT ('.' (INT)? )? ;
WS: [ \t\r\n]+ -> skip;
COMMENT : '/*' .*? '*/' -> skip;

//Custom rules by me
IP: INT '.' INT '.' INT '.' INT ;
PV: ('A'..'Z') ('0'..'9' | 'a'..'z' |'.' )*;//process variables belonging to a PLC

