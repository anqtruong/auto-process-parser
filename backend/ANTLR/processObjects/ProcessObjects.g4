grammar ProcessObjects;
import lexerRules;

masterRule:
	process*
	plc*
	plcToProcess*
	adConverters*
	modbusMapping*
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
       'id:' INT ';' //~ 'slave_address:' INT' ';'
       'ip:' IP ';' 
       'protocol:' ID ';' 

       inputs?
       outputs?
    '}' ;

inputs:
   'inputs:' ID (',' ID)* ';' ;

outputs: 
   'outputs:' ID (',' ID)* ';' ;

//PLC to Process
plcToProcess:
	'plcToProcess' ID '{'
	ID (',' ID)* 
	'}' ;


//ad converter
adConverters:
   'adConverters' '{'
	r*
   '}';

r: ID ':' INT ':' DOUBLE ':' DOUBLE ';' ;

//Modbus memory modbus 
modbusMapping:
	'modbusMapping' ID '{'
	 mapping*
	'}';

mapping:
	ID ':' ID ':' INT ';'
	;

