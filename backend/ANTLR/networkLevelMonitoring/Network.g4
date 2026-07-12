grammar Network;
import lexerRules;

masterRule:
	PROTOCOL ACTION option+ 
	;

option:
	s
	| sp
	| d
	| dp 
	| fc
	| ec
	;

s:
	's=' IPSUBNET (',' IPSUBNET)*
	| 's=' IP (',' IP)*
	;
sp:
	'sp=' INT
	;
d:
	'd=' IPSUBNET (',' IPSUBNET)*
	| 'd=' IP (',' IP)*
	;
dp:
	'dp=' INT 
	;
fc:
	'fc=' INT 
	;

ec:
	'ec=' INT
	;

PROTOCOL: 'dnp3' | 'modbus' ;
ACTION: 'drop' | 'accept' |'alert' | 'log' ;
IPSUBNET:  IP '/' INT;

