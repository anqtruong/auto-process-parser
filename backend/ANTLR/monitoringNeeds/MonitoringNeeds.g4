grammar MonitoringNeeds;
import lexerRules;

masterRule:
	status*
	value*
	multiple*
	frequency*
	interval*
	rateOfChange*
	pollRate*
	;

status:
	'status'  PV OPERATOR BOOL ';' 
	;

value:
	'value' PV OPERATOR DOUBLE';' 
	;

multiple:
	'multipleMatch' element* ';' 
	;

  element: rn | st ;
    rn : '(' PV OPERATOR (DOUBLE | INT)* ')' ;
    st : '(' PV OPERATOR BOOL  ')' ;

frequency:
	'frequency' PV OPERATOR DOUBLE ';' 
	;


interval:
	'interval' PV OPERATOR DOUBLE ';'
	;

rateOfChange:
	'rateOfChange' PV OPERATOR DOUBLE ';'
	;

pollRate:
	'pollRate' PV OPERATOR DOUBLE ';'
	;
