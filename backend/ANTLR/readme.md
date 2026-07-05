# Structure
There are 2 folders listed "monitoringNeeds" and "processObjects." Each of these folders contains the following items:
1. 2 grammar files (1 is task specific and the other is just for lexer rules)
2. a test .txt file to ensure input is parsed properly under ideal conditions (already given in the Process Descriptive Language in a specific order)

## monitoringNeeds
This folder contains the files needed to run ANTLR on a file that contains monitoring needs.

| File                  | Purpose                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| MonitoringNeeds.g4    | This is the main grammar file that is used to parse the input file. It contains a single master rule which calls defined sub-rules for monitoring needs (e.g. monitor the status of a light). It requires input to match the process descriptive language's syntax and the monitoring needs must be structured in the following order:<br>1. status<br>2. value<br>3. multiplematch<br>4. frequency<br>5. Interval<br>6. rate of change<br>7. poll rate<br>If not provided in this order, then ANTLR will fail to properly parse the input. Multiple of the same monitoring needs can be provided as long as they follow the order (e.g. 3 status then 2 values) |
| lexerRules.g4         | This file contains the lexer rules used to tokenize input. It mainly contains rules for operators and variables.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| MonitoringTesting.txt | This is just a .txt file with sample input that could be provided by a process engineer. It was taken from the dissertation and gives examples of monitoring needs a process engineer might want to monitor.                                                                                                                                                                                                                                                                                                                                                                                                                                                     |

## processObjects

| File              | Purpose                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ProcessObjects.g4 | This is the main grammar file that is used to parse the input file. It contains a single master rule which calls defined sub-rules for process objects (e.g. process, plc, Modbus mappings, etc). Input must be given in the following order to be parsed correctly.<br>1. process<br>2. plc<br>3. plc to Process<br>4. adConverters<br>5. Modbus memory mappings<br>Like the monitoring needs file, it can also support multiple process objects of the same type, as long as they remain in the correct order. |
| lexerRules.g4     | This file contains the lexer rules used to tokenize input. It mainly contains rules for operators and variables.                                                                                                                                                                                                                                                                                                                                                                                                 |
| objectTester.txt  | This is just a .txt file with sample input that could be provided by a process engineer. It was taken from the dissertation and gives examples of process objects that a process engineer would want to define.                                                                                                                                                                                                                                                                                                  |
## Running
###### Versions used:
ANTLR - 4.13.2
Java - 21.0.12

To run ANTLR in the terminal do the following.
1. Ensure correct versions of the listed software are being used. (ANTLR is unable to work with java version > 21 [last time I checked])
2. run the "antlr4" command on the main .g4 file (not lexerRules.g4)
    EX: "antlr4 ProcessObjects.g4"
3. Compile the generated java files from antlr 
    "javac *.java"
4. Use the 'grun' command to run ANTLR on the input file
EX: 'grun ProcessObjects masterRule -gui objectTester.txt'
Structure: grun (grammar file name w/out .g4 extension) (rule to run from grammar file) (option) (input file)

*The -gui option provides a visual representation of the parse tree, which allows for parsing verifcation. Other options can be used to gain more insight (-tokens).

ANTLR contributions by Diego Salas-Esquivel
