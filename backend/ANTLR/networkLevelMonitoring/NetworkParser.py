# Generated from Network.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,33,84,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,1,0,1,0,1,0,4,0,20,8,0,11,0,12,0,21,1,1,1,1,1,1,1,1,1,
        1,1,1,3,1,30,8,1,1,2,1,2,1,2,1,2,5,2,36,8,2,10,2,12,2,39,9,2,1,2,
        1,2,1,2,1,2,5,2,45,8,2,10,2,12,2,48,9,2,3,2,50,8,2,1,3,1,3,1,3,1,
        4,1,4,1,4,1,4,5,4,59,8,4,10,4,12,4,62,9,4,1,4,1,4,1,4,1,4,5,4,68,
        8,4,10,4,12,4,71,9,4,3,4,73,8,4,1,5,1,5,1,5,1,6,1,6,1,6,1,7,1,7,
        1,7,1,7,0,0,8,0,2,4,6,8,10,12,14,0,0,87,0,16,1,0,0,0,2,29,1,0,0,
        0,4,49,1,0,0,0,6,51,1,0,0,0,8,72,1,0,0,0,10,74,1,0,0,0,12,77,1,0,
        0,0,14,80,1,0,0,0,16,17,5,8,0,0,17,19,5,9,0,0,18,20,3,2,1,0,19,18,
        1,0,0,0,20,21,1,0,0,0,21,19,1,0,0,0,21,22,1,0,0,0,22,1,1,0,0,0,23,
        30,3,4,2,0,24,30,3,6,3,0,25,30,3,8,4,0,26,30,3,10,5,0,27,30,3,12,
        6,0,28,30,3,14,7,0,29,23,1,0,0,0,29,24,1,0,0,0,29,25,1,0,0,0,29,
        26,1,0,0,0,29,27,1,0,0,0,29,28,1,0,0,0,30,3,1,0,0,0,31,32,5,1,0,
        0,32,37,5,10,0,0,33,34,5,2,0,0,34,36,5,10,0,0,35,33,1,0,0,0,36,39,
        1,0,0,0,37,35,1,0,0,0,37,38,1,0,0,0,38,50,1,0,0,0,39,37,1,0,0,0,
        40,41,5,1,0,0,41,46,5,32,0,0,42,43,5,2,0,0,43,45,5,32,0,0,44,42,
        1,0,0,0,45,48,1,0,0,0,46,44,1,0,0,0,46,47,1,0,0,0,47,50,1,0,0,0,
        48,46,1,0,0,0,49,31,1,0,0,0,49,40,1,0,0,0,50,5,1,0,0,0,51,52,5,3,
        0,0,52,53,5,27,0,0,53,7,1,0,0,0,54,55,5,4,0,0,55,60,5,10,0,0,56,
        57,5,2,0,0,57,59,5,10,0,0,58,56,1,0,0,0,59,62,1,0,0,0,60,58,1,0,
        0,0,60,61,1,0,0,0,61,73,1,0,0,0,62,60,1,0,0,0,63,64,5,4,0,0,64,69,
        5,32,0,0,65,66,5,2,0,0,66,68,5,32,0,0,67,65,1,0,0,0,68,71,1,0,0,
        0,69,67,1,0,0,0,69,70,1,0,0,0,70,73,1,0,0,0,71,69,1,0,0,0,72,54,
        1,0,0,0,72,63,1,0,0,0,73,9,1,0,0,0,74,75,5,5,0,0,75,76,5,27,0,0,
        76,11,1,0,0,0,77,78,5,6,0,0,78,79,5,27,0,0,79,13,1,0,0,0,80,81,5,
        7,0,0,81,82,5,27,0,0,82,15,1,0,0,0,8,21,29,37,46,49,60,69,72
    ]

class NetworkParser ( Parser ):

    grammarFileName = "Network.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'s='", "','", "'sp='", "'d='", "'dp='", 
                     "'fc='", "'ec='", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'|'", "'&'", "<INVALID>", "'!='", "'>'", 
                     "'<'", "'>='", "'<='", "'+'", "'-'", "'*'", "'/'", 
                     "<INVALID>", "'on'", "'off'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "PROTOCOL", "ACTION", "IPSUBNET", "OPERATOR", "OR", 
                      "AND", "EQ", "NEQ", "G", "L", "GEQ", "LEQ", "ADD", 
                      "SUB", "MUL", "DIV", "BOOL", "TRUE", "FALSE", "INT", 
                      "ID", "DOUBLE", "WS", "COMMENT", "IP", "PV" ]

    RULE_masterRule = 0
    RULE_option = 1
    RULE_s = 2
    RULE_sp = 3
    RULE_d = 4
    RULE_dp = 5
    RULE_fc = 6
    RULE_ec = 7

    ruleNames =  [ "masterRule", "option", "s", "sp", "d", "dp", "fc", "ec" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    PROTOCOL=8
    ACTION=9
    IPSUBNET=10
    OPERATOR=11
    OR=12
    AND=13
    EQ=14
    NEQ=15
    G=16
    L=17
    GEQ=18
    LEQ=19
    ADD=20
    SUB=21
    MUL=22
    DIV=23
    BOOL=24
    TRUE=25
    FALSE=26
    INT=27
    ID=28
    DOUBLE=29
    WS=30
    COMMENT=31
    IP=32
    PV=33

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class MasterRuleContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PROTOCOL(self):
            return self.getToken(NetworkParser.PROTOCOL, 0)

        def ACTION(self):
            return self.getToken(NetworkParser.ACTION, 0)

        def option(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NetworkParser.OptionContext)
            else:
                return self.getTypedRuleContext(NetworkParser.OptionContext,i)


        def getRuleIndex(self):
            return NetworkParser.RULE_masterRule

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMasterRule" ):
                listener.enterMasterRule(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMasterRule" ):
                listener.exitMasterRule(self)




    def masterRule(self):

        localctx = NetworkParser.MasterRuleContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_masterRule)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 16
            self.match(NetworkParser.PROTOCOL)
            self.state = 17
            self.match(NetworkParser.ACTION)
            self.state = 19 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 18
                self.option()
                self.state = 21 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 250) != 0)):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OptionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def s(self):
            return self.getTypedRuleContext(NetworkParser.SContext,0)


        def sp(self):
            return self.getTypedRuleContext(NetworkParser.SpContext,0)


        def d(self):
            return self.getTypedRuleContext(NetworkParser.DContext,0)


        def dp(self):
            return self.getTypedRuleContext(NetworkParser.DpContext,0)


        def fc(self):
            return self.getTypedRuleContext(NetworkParser.FcContext,0)


        def ec(self):
            return self.getTypedRuleContext(NetworkParser.EcContext,0)


        def getRuleIndex(self):
            return NetworkParser.RULE_option

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOption" ):
                listener.enterOption(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOption" ):
                listener.exitOption(self)




    def option(self):

        localctx = NetworkParser.OptionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_option)
        try:
            self.state = 29
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [1]:
                self.enterOuterAlt(localctx, 1)
                self.state = 23
                self.s()
                pass
            elif token in [3]:
                self.enterOuterAlt(localctx, 2)
                self.state = 24
                self.sp()
                pass
            elif token in [4]:
                self.enterOuterAlt(localctx, 3)
                self.state = 25
                self.d()
                pass
            elif token in [5]:
                self.enterOuterAlt(localctx, 4)
                self.state = 26
                self.dp()
                pass
            elif token in [6]:
                self.enterOuterAlt(localctx, 5)
                self.state = 27
                self.fc()
                pass
            elif token in [7]:
                self.enterOuterAlt(localctx, 6)
                self.state = 28
                self.ec()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IPSUBNET(self, i:int=None):
            if i is None:
                return self.getTokens(NetworkParser.IPSUBNET)
            else:
                return self.getToken(NetworkParser.IPSUBNET, i)

        def IP(self, i:int=None):
            if i is None:
                return self.getTokens(NetworkParser.IP)
            else:
                return self.getToken(NetworkParser.IP, i)

        def getRuleIndex(self):
            return NetworkParser.RULE_s

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterS" ):
                listener.enterS(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitS" ):
                listener.exitS(self)




    def s(self):

        localctx = NetworkParser.SContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_s)
        self._la = 0 # Token type
        try:
            self.state = 49
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,4,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 31
                self.match(NetworkParser.T__0)
                self.state = 32
                self.match(NetworkParser.IPSUBNET)
                self.state = 37
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==2:
                    self.state = 33
                    self.match(NetworkParser.T__1)
                    self.state = 34
                    self.match(NetworkParser.IPSUBNET)
                    self.state = 39
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 40
                self.match(NetworkParser.T__0)
                self.state = 41
                self.match(NetworkParser.IP)
                self.state = 46
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==2:
                    self.state = 42
                    self.match(NetworkParser.T__1)
                    self.state = 43
                    self.match(NetworkParser.IP)
                    self.state = 48
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SpContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INT(self):
            return self.getToken(NetworkParser.INT, 0)

        def getRuleIndex(self):
            return NetworkParser.RULE_sp

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSp" ):
                listener.enterSp(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSp" ):
                listener.exitSp(self)




    def sp(self):

        localctx = NetworkParser.SpContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_sp)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 51
            self.match(NetworkParser.T__2)
            self.state = 52
            self.match(NetworkParser.INT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IPSUBNET(self, i:int=None):
            if i is None:
                return self.getTokens(NetworkParser.IPSUBNET)
            else:
                return self.getToken(NetworkParser.IPSUBNET, i)

        def IP(self, i:int=None):
            if i is None:
                return self.getTokens(NetworkParser.IP)
            else:
                return self.getToken(NetworkParser.IP, i)

        def getRuleIndex(self):
            return NetworkParser.RULE_d

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterD" ):
                listener.enterD(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitD" ):
                listener.exitD(self)




    def d(self):

        localctx = NetworkParser.DContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_d)
        self._la = 0 # Token type
        try:
            self.state = 72
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,7,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 54
                self.match(NetworkParser.T__3)
                self.state = 55
                self.match(NetworkParser.IPSUBNET)
                self.state = 60
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==2:
                    self.state = 56
                    self.match(NetworkParser.T__1)
                    self.state = 57
                    self.match(NetworkParser.IPSUBNET)
                    self.state = 62
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 63
                self.match(NetworkParser.T__3)
                self.state = 64
                self.match(NetworkParser.IP)
                self.state = 69
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==2:
                    self.state = 65
                    self.match(NetworkParser.T__1)
                    self.state = 66
                    self.match(NetworkParser.IP)
                    self.state = 71
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DpContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INT(self):
            return self.getToken(NetworkParser.INT, 0)

        def getRuleIndex(self):
            return NetworkParser.RULE_dp

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDp" ):
                listener.enterDp(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDp" ):
                listener.exitDp(self)




    def dp(self):

        localctx = NetworkParser.DpContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_dp)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 74
            self.match(NetworkParser.T__4)
            self.state = 75
            self.match(NetworkParser.INT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FcContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INT(self):
            return self.getToken(NetworkParser.INT, 0)

        def getRuleIndex(self):
            return NetworkParser.RULE_fc

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFc" ):
                listener.enterFc(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFc" ):
                listener.exitFc(self)




    def fc(self):

        localctx = NetworkParser.FcContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_fc)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 77
            self.match(NetworkParser.T__5)
            self.state = 78
            self.match(NetworkParser.INT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class EcContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INT(self):
            return self.getToken(NetworkParser.INT, 0)

        def getRuleIndex(self):
            return NetworkParser.RULE_ec

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEc" ):
                listener.enterEc(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEc" ):
                listener.exitEc(self)




    def ec(self):

        localctx = NetworkParser.EcContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_ec)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 80
            self.match(NetworkParser.T__6)
            self.state = 81
            self.match(NetworkParser.INT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





