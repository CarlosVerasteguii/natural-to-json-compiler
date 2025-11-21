# Generated from NaturalToJson.g4 by ANTLR 4.13.2
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
        4,1,15,64,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,1,0,5,0,18,8,0,10,0,12,0,21,9,0,1,0,1,0,1,1,1,1,3,1,27,
        8,1,1,2,1,2,1,2,1,2,1,2,1,2,1,3,1,3,1,3,5,3,38,8,3,10,3,12,3,41,
        9,3,1,4,1,4,1,4,1,4,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,6,1,6,1,6,5,6,
        57,8,6,10,6,12,6,60,9,6,1,7,1,7,1,7,0,0,8,0,2,4,6,8,10,12,14,0,1,
        2,0,6,7,9,11,59,0,19,1,0,0,0,2,26,1,0,0,0,4,28,1,0,0,0,6,34,1,0,
        0,0,8,42,1,0,0,0,10,46,1,0,0,0,12,53,1,0,0,0,14,61,1,0,0,0,16,18,
        3,2,1,0,17,16,1,0,0,0,18,21,1,0,0,0,19,17,1,0,0,0,19,20,1,0,0,0,
        20,22,1,0,0,0,21,19,1,0,0,0,22,23,5,0,0,1,23,1,1,0,0,0,24,27,3,4,
        2,0,25,27,3,10,5,0,26,24,1,0,0,0,26,25,1,0,0,0,27,3,1,0,0,0,28,29,
        5,1,0,0,29,30,5,2,0,0,30,31,5,8,0,0,31,32,5,4,0,0,32,33,3,6,3,0,
        33,5,1,0,0,0,34,39,3,8,4,0,35,36,5,13,0,0,36,38,3,8,4,0,37,35,1,
        0,0,0,38,41,1,0,0,0,39,37,1,0,0,0,39,40,1,0,0,0,40,7,1,0,0,0,41,
        39,1,0,0,0,42,43,5,8,0,0,43,44,5,12,0,0,44,45,3,14,7,0,45,9,1,0,
        0,0,46,47,5,1,0,0,47,48,5,3,0,0,48,49,5,8,0,0,49,50,5,4,0,0,50,51,
        5,5,0,0,51,52,3,12,6,0,52,11,1,0,0,0,53,58,3,14,7,0,54,55,5,13,0,
        0,55,57,3,14,7,0,56,54,1,0,0,0,57,60,1,0,0,0,58,56,1,0,0,0,58,59,
        1,0,0,0,59,13,1,0,0,0,60,58,1,0,0,0,61,62,7,0,0,0,62,15,1,0,0,0,
        4,19,26,39,58
    ]

class NaturalToJsonParser ( Parser ):

    grammarFileName = "NaturalToJson.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "':'", "','" ]

    symbolicNames = [ "<INVALID>", "CREAR", "OBJETO", "LISTA", "CON", "ELEMENTOS", 
                      "KW_VERDADERO", "KW_FALSO", "IDENTIFICADOR", "STRING", 
                      "NUMERO_DECIMAL", "NUMERO_ENTERO", "DOS_PUNTOS", "COMA", 
                      "COMENTARIO_LINEA", "WHITESPACE" ]

    RULE_programa = 0
    RULE_comando = 1
    RULE_crear_objeto_cmd = 2
    RULE_propiedades = 3
    RULE_propiedad = 4
    RULE_crear_lista_cmd = 5
    RULE_items_lista = 6
    RULE_valor = 7

    ruleNames =  [ "programa", "comando", "crear_objeto_cmd", "propiedades", 
                   "propiedad", "crear_lista_cmd", "items_lista", "valor" ]

    EOF = Token.EOF
    CREAR=1
    OBJETO=2
    LISTA=3
    CON=4
    ELEMENTOS=5
    KW_VERDADERO=6
    KW_FALSO=7
    IDENTIFICADOR=8
    STRING=9
    NUMERO_DECIMAL=10
    NUMERO_ENTERO=11
    DOS_PUNTOS=12
    COMA=13
    COMENTARIO_LINEA=14
    WHITESPACE=15

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ProgramaContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(NaturalToJsonParser.EOF, 0)

        def comando(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NaturalToJsonParser.ComandoContext)
            else:
                return self.getTypedRuleContext(NaturalToJsonParser.ComandoContext,i)


        def getRuleIndex(self):
            return NaturalToJsonParser.RULE_programa

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPrograma" ):
                listener.enterPrograma(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPrograma" ):
                listener.exitPrograma(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPrograma" ):
                return visitor.visitPrograma(self)
            else:
                return visitor.visitChildren(self)




    def programa(self):

        localctx = NaturalToJsonParser.ProgramaContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_programa)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 19
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==1:
                self.state = 16
                self.comando()
                self.state = 21
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 22
            self.match(NaturalToJsonParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ComandoContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def crear_objeto_cmd(self):
            return self.getTypedRuleContext(NaturalToJsonParser.Crear_objeto_cmdContext,0)


        def crear_lista_cmd(self):
            return self.getTypedRuleContext(NaturalToJsonParser.Crear_lista_cmdContext,0)


        def getRuleIndex(self):
            return NaturalToJsonParser.RULE_comando

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterComando" ):
                listener.enterComando(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitComando" ):
                listener.exitComando(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitComando" ):
                return visitor.visitComando(self)
            else:
                return visitor.visitChildren(self)




    def comando(self):

        localctx = NaturalToJsonParser.ComandoContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_comando)
        try:
            self.state = 26
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 24
                self.crear_objeto_cmd()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 25
                self.crear_lista_cmd()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Crear_objeto_cmdContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.nombre_obj = None # Token

        def CREAR(self):
            return self.getToken(NaturalToJsonParser.CREAR, 0)

        def OBJETO(self):
            return self.getToken(NaturalToJsonParser.OBJETO, 0)

        def CON(self):
            return self.getToken(NaturalToJsonParser.CON, 0)

        def propiedades(self):
            return self.getTypedRuleContext(NaturalToJsonParser.PropiedadesContext,0)


        def IDENTIFICADOR(self):
            return self.getToken(NaturalToJsonParser.IDENTIFICADOR, 0)

        def getRuleIndex(self):
            return NaturalToJsonParser.RULE_crear_objeto_cmd

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCrear_objeto_cmd" ):
                listener.enterCrear_objeto_cmd(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCrear_objeto_cmd" ):
                listener.exitCrear_objeto_cmd(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCrear_objeto_cmd" ):
                return visitor.visitCrear_objeto_cmd(self)
            else:
                return visitor.visitChildren(self)




    def crear_objeto_cmd(self):

        localctx = NaturalToJsonParser.Crear_objeto_cmdContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_crear_objeto_cmd)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 28
            self.match(NaturalToJsonParser.CREAR)
            self.state = 29
            self.match(NaturalToJsonParser.OBJETO)
            self.state = 30
            localctx.nombre_obj = self.match(NaturalToJsonParser.IDENTIFICADOR)
            self.state = 31
            self.match(NaturalToJsonParser.CON)
            self.state = 32
            self.propiedades()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PropiedadesContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def propiedad(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NaturalToJsonParser.PropiedadContext)
            else:
                return self.getTypedRuleContext(NaturalToJsonParser.PropiedadContext,i)


        def COMA(self, i:int=None):
            if i is None:
                return self.getTokens(NaturalToJsonParser.COMA)
            else:
                return self.getToken(NaturalToJsonParser.COMA, i)

        def getRuleIndex(self):
            return NaturalToJsonParser.RULE_propiedades

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPropiedades" ):
                listener.enterPropiedades(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPropiedades" ):
                listener.exitPropiedades(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPropiedades" ):
                return visitor.visitPropiedades(self)
            else:
                return visitor.visitChildren(self)




    def propiedades(self):

        localctx = NaturalToJsonParser.PropiedadesContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_propiedades)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 34
            self.propiedad()
            self.state = 39
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==13:
                self.state = 35
                self.match(NaturalToJsonParser.COMA)
                self.state = 36
                self.propiedad()
                self.state = 41
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PropiedadContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.clave = None # Token

        def DOS_PUNTOS(self):
            return self.getToken(NaturalToJsonParser.DOS_PUNTOS, 0)

        def valor(self):
            return self.getTypedRuleContext(NaturalToJsonParser.ValorContext,0)


        def IDENTIFICADOR(self):
            return self.getToken(NaturalToJsonParser.IDENTIFICADOR, 0)

        def getRuleIndex(self):
            return NaturalToJsonParser.RULE_propiedad

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPropiedad" ):
                listener.enterPropiedad(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPropiedad" ):
                listener.exitPropiedad(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPropiedad" ):
                return visitor.visitPropiedad(self)
            else:
                return visitor.visitChildren(self)




    def propiedad(self):

        localctx = NaturalToJsonParser.PropiedadContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_propiedad)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 42
            localctx.clave = self.match(NaturalToJsonParser.IDENTIFICADOR)
            self.state = 43
            self.match(NaturalToJsonParser.DOS_PUNTOS)
            self.state = 44
            self.valor()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Crear_lista_cmdContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.nombre_lista = None # Token

        def CREAR(self):
            return self.getToken(NaturalToJsonParser.CREAR, 0)

        def LISTA(self):
            return self.getToken(NaturalToJsonParser.LISTA, 0)

        def CON(self):
            return self.getToken(NaturalToJsonParser.CON, 0)

        def ELEMENTOS(self):
            return self.getToken(NaturalToJsonParser.ELEMENTOS, 0)

        def items_lista(self):
            return self.getTypedRuleContext(NaturalToJsonParser.Items_listaContext,0)


        def IDENTIFICADOR(self):
            return self.getToken(NaturalToJsonParser.IDENTIFICADOR, 0)

        def getRuleIndex(self):
            return NaturalToJsonParser.RULE_crear_lista_cmd

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCrear_lista_cmd" ):
                listener.enterCrear_lista_cmd(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCrear_lista_cmd" ):
                listener.exitCrear_lista_cmd(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCrear_lista_cmd" ):
                return visitor.visitCrear_lista_cmd(self)
            else:
                return visitor.visitChildren(self)




    def crear_lista_cmd(self):

        localctx = NaturalToJsonParser.Crear_lista_cmdContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_crear_lista_cmd)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 46
            self.match(NaturalToJsonParser.CREAR)
            self.state = 47
            self.match(NaturalToJsonParser.LISTA)
            self.state = 48
            localctx.nombre_lista = self.match(NaturalToJsonParser.IDENTIFICADOR)
            self.state = 49
            self.match(NaturalToJsonParser.CON)
            self.state = 50
            self.match(NaturalToJsonParser.ELEMENTOS)
            self.state = 51
            self.items_lista()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Items_listaContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def valor(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(NaturalToJsonParser.ValorContext)
            else:
                return self.getTypedRuleContext(NaturalToJsonParser.ValorContext,i)


        def COMA(self, i:int=None):
            if i is None:
                return self.getTokens(NaturalToJsonParser.COMA)
            else:
                return self.getToken(NaturalToJsonParser.COMA, i)

        def getRuleIndex(self):
            return NaturalToJsonParser.RULE_items_lista

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterItems_lista" ):
                listener.enterItems_lista(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitItems_lista" ):
                listener.exitItems_lista(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitItems_lista" ):
                return visitor.visitItems_lista(self)
            else:
                return visitor.visitChildren(self)




    def items_lista(self):

        localctx = NaturalToJsonParser.Items_listaContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_items_lista)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 53
            self.valor()
            self.state = 58
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==13:
                self.state = 54
                self.match(NaturalToJsonParser.COMA)
                self.state = 55
                self.valor()
                self.state = 60
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ValorContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(NaturalToJsonParser.STRING, 0)

        def NUMERO_DECIMAL(self):
            return self.getToken(NaturalToJsonParser.NUMERO_DECIMAL, 0)

        def NUMERO_ENTERO(self):
            return self.getToken(NaturalToJsonParser.NUMERO_ENTERO, 0)

        def KW_VERDADERO(self):
            return self.getToken(NaturalToJsonParser.KW_VERDADERO, 0)

        def KW_FALSO(self):
            return self.getToken(NaturalToJsonParser.KW_FALSO, 0)

        def getRuleIndex(self):
            return NaturalToJsonParser.RULE_valor

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterValor" ):
                listener.enterValor(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitValor" ):
                listener.exitValor(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitValor" ):
                return visitor.visitValor(self)
            else:
                return visitor.visitChildren(self)




    def valor(self):

        localctx = NaturalToJsonParser.ValorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_valor)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 61
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 3776) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





