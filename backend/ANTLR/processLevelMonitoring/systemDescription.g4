grammar systemDescription;
import lexerRules;

/*
This is the rule responsible for calling an entire 'construct'
This allows for multiple constructs to be in one input file.
Multiple process variables can belong to one PLC so its important to understand the whole picture.
*/

masterRule:
	construct (construct)*
	;

construct:
	process
	plc
	plcToProcess
	adConverters
	dnp3Mapping
	;


//Process object
process:
	'Process' ID '{'
	binary_readings?
	binary_controls?
	discrete_readings?
	discrete_controls?
	analog_readings?
	analog_controls?
	'}';

binary_readings: 
	'binary_readings:' ID (',' ID)* ';' ;

binary_controls:
	'binary_controls:' ID  (',' ID )* ';' ;

discrete_readings:
	'discrete_readings:' ID (',' ID)* ';' ;

discrete_controls:
	'discrete_controls:' ID (',' ID)* ';' ;

analog_readings:
	'analog_readings:' ID (',' ID)* ';' ;

analog_controls:
	'analog_controls:' ID (',' ID)* ';' ;

//PLC object rules
plc:
    'PLC' ID '{'
       'slave_address:' INT ';' //~ 'slave_address:' INT' ';'
       'ip:' IP ';' 
       'protocol:' ID ';' 

       inputs?
       outputs?
    '}' ;

inputs:
   'inputs:' ID (',' ID)* ';' ;

outputs: 
   'outputs:' ID (',' ID)* ';' ;

//ad converter
adConverters:
   'adConverters' '{'
	r*
   '}';
 
r: ID ':' INT ':' DOUBLE ':' DOUBLE ';' ;


//PLC to Process
plcToProcess:
	'plcToProcess' ID '{'
	ID (',' ID)* 
	'}' ;

dnp3Mapping:
	'dnp3Mapping' ID '{'
	raw*
	'}'
	;

raw:
	ID ':' INT ':' INT ':' INT ';'
	//Name : object number - variation - index
	;
