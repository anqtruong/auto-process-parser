# Generated from systemDescription.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .systemDescriptionParser import systemDescriptionParser
else:
    from systemDescriptionParser import systemDescriptionParser

# This class defines a complete listener for a parse tree produced by systemDescriptionParser.
class systemDescriptionListener(ParseTreeListener):

    # Enter a parse tree produced by systemDescriptionParser#masterRule.
    def enterMasterRule(self, ctx:systemDescriptionParser.MasterRuleContext):
        pass

    # Exit a parse tree produced by systemDescriptionParser#masterRule.
    def exitMasterRule(self, ctx:systemDescriptionParser.MasterRuleContext):
        pass


    # Enter a parse tree produced by systemDescriptionParser#construct.
    def enterConstruct(self, ctx:systemDescriptionParser.ConstructContext):
        pass

    # Exit a parse tree produced by systemDescriptionParser#construct.
    def exitConstruct(self, ctx:systemDescriptionParser.ConstructContext):
        pass


    # Enter a parse tree produced by systemDescriptionParser#process.
    def enterProcess(self, ctx:systemDescriptionParser.ProcessContext):
        pass

    # Exit a parse tree produced by systemDescriptionParser#process.
    def exitProcess(self, ctx:systemDescriptionParser.ProcessContext):
        pass


    # Enter a parse tree produced by systemDescriptionParser#binary_readings.
    def enterBinary_readings(self, ctx:systemDescriptionParser.Binary_readingsContext):
        pass

    # Exit a parse tree produced by systemDescriptionParser#binary_readings.
    def exitBinary_readings(self, ctx:systemDescriptionParser.Binary_readingsContext):
        pass


    # Enter a parse tree produced by systemDescriptionParser#binary_controls.
    def enterBinary_controls(self, ctx:systemDescriptionParser.Binary_controlsContext):
        pass

    # Exit a parse tree produced by systemDescriptionParser#binary_controls.
    def exitBinary_controls(self, ctx:systemDescriptionParser.Binary_controlsContext):
        pass


    # Enter a parse tree produced by systemDescriptionParser#discrete_readings.
    def enterDiscrete_readings(self, ctx:systemDescriptionParser.Discrete_readingsContext):
        pass

    # Exit a parse tree produced by systemDescriptionParser#discrete_readings.
    def exitDiscrete_readings(self, ctx:systemDescriptionParser.Discrete_readingsContext):
        pass


    # Enter a parse tree produced by systemDescriptionParser#discrete_controls.
    def enterDiscrete_controls(self, ctx:systemDescriptionParser.Discrete_controlsContext):
        pass

    # Exit a parse tree produced by systemDescriptionParser#discrete_controls.
    def exitDiscrete_controls(self, ctx:systemDescriptionParser.Discrete_controlsContext):
        pass


    # Enter a parse tree produced by systemDescriptionParser#analog_readings.
    def enterAnalog_readings(self, ctx:systemDescriptionParser.Analog_readingsContext):
        pass

    # Exit a parse tree produced by systemDescriptionParser#analog_readings.
    def exitAnalog_readings(self, ctx:systemDescriptionParser.Analog_readingsContext):
        pass


    # Enter a parse tree produced by systemDescriptionParser#analog_controls.
    def enterAnalog_controls(self, ctx:systemDescriptionParser.Analog_controlsContext):
        pass

    # Exit a parse tree produced by systemDescriptionParser#analog_controls.
    def exitAnalog_controls(self, ctx:systemDescriptionParser.Analog_controlsContext):
        pass


    # Enter a parse tree produced by systemDescriptionParser#plc.
    def enterPlc(self, ctx:systemDescriptionParser.PlcContext):
        pass

    # Exit a parse tree produced by systemDescriptionParser#plc.
    def exitPlc(self, ctx:systemDescriptionParser.PlcContext):
        pass


    # Enter a parse tree produced by systemDescriptionParser#inputs.
    def enterInputs(self, ctx:systemDescriptionParser.InputsContext):
        pass

    # Exit a parse tree produced by systemDescriptionParser#inputs.
    def exitInputs(self, ctx:systemDescriptionParser.InputsContext):
        pass


    # Enter a parse tree produced by systemDescriptionParser#outputs.
    def enterOutputs(self, ctx:systemDescriptionParser.OutputsContext):
        pass

    # Exit a parse tree produced by systemDescriptionParser#outputs.
    def exitOutputs(self, ctx:systemDescriptionParser.OutputsContext):
        pass


    # Enter a parse tree produced by systemDescriptionParser#adConverters.
    def enterAdConverters(self, ctx:systemDescriptionParser.AdConvertersContext):
        pass

    # Exit a parse tree produced by systemDescriptionParser#adConverters.
    def exitAdConverters(self, ctx:systemDescriptionParser.AdConvertersContext):
        pass


    # Enter a parse tree produced by systemDescriptionParser#r.
    def enterR(self, ctx:systemDescriptionParser.RContext):
        pass

    # Exit a parse tree produced by systemDescriptionParser#r.
    def exitR(self, ctx:systemDescriptionParser.RContext):
        pass


    # Enter a parse tree produced by systemDescriptionParser#plcToProcess.
    def enterPlcToProcess(self, ctx:systemDescriptionParser.PlcToProcessContext):
        pass

    # Exit a parse tree produced by systemDescriptionParser#plcToProcess.
    def exitPlcToProcess(self, ctx:systemDescriptionParser.PlcToProcessContext):
        pass


    # Enter a parse tree produced by systemDescriptionParser#dnp3Mapping.
    def enterDnp3Mapping(self, ctx:systemDescriptionParser.Dnp3MappingContext):
        pass

    # Exit a parse tree produced by systemDescriptionParser#dnp3Mapping.
    def exitDnp3Mapping(self, ctx:systemDescriptionParser.Dnp3MappingContext):
        pass


    # Enter a parse tree produced by systemDescriptionParser#raw.
    def enterRaw(self, ctx:systemDescriptionParser.RawContext):
        pass

    # Exit a parse tree produced by systemDescriptionParser#raw.
    def exitRaw(self, ctx:systemDescriptionParser.RawContext):
        pass



del systemDescriptionParser