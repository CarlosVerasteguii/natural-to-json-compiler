# Generated from NaturalToJson.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .NaturalToJsonParser import NaturalToJsonParser
else:
    from NaturalToJsonParser import NaturalToJsonParser

# This class defines a complete listener for a parse tree produced by NaturalToJsonParser.
class NaturalToJsonListener(ParseTreeListener):

    # Enter a parse tree produced by NaturalToJsonParser#programa.
    def enterPrograma(self, ctx:NaturalToJsonParser.ProgramaContext):
        pass

    # Exit a parse tree produced by NaturalToJsonParser#programa.
    def exitPrograma(self, ctx:NaturalToJsonParser.ProgramaContext):
        pass


    # Enter a parse tree produced by NaturalToJsonParser#comando.
    def enterComando(self, ctx:NaturalToJsonParser.ComandoContext):
        pass

    # Exit a parse tree produced by NaturalToJsonParser#comando.
    def exitComando(self, ctx:NaturalToJsonParser.ComandoContext):
        pass


    # Enter a parse tree produced by NaturalToJsonParser#crear_objeto_cmd.
    def enterCrear_objeto_cmd(self, ctx:NaturalToJsonParser.Crear_objeto_cmdContext):
        pass

    # Exit a parse tree produced by NaturalToJsonParser#crear_objeto_cmd.
    def exitCrear_objeto_cmd(self, ctx:NaturalToJsonParser.Crear_objeto_cmdContext):
        pass


    # Enter a parse tree produced by NaturalToJsonParser#propiedades.
    def enterPropiedades(self, ctx:NaturalToJsonParser.PropiedadesContext):
        pass

    # Exit a parse tree produced by NaturalToJsonParser#propiedades.
    def exitPropiedades(self, ctx:NaturalToJsonParser.PropiedadesContext):
        pass


    # Enter a parse tree produced by NaturalToJsonParser#propiedad.
    def enterPropiedad(self, ctx:NaturalToJsonParser.PropiedadContext):
        pass

    # Exit a parse tree produced by NaturalToJsonParser#propiedad.
    def exitPropiedad(self, ctx:NaturalToJsonParser.PropiedadContext):
        pass


    # Enter a parse tree produced by NaturalToJsonParser#crear_lista_cmd.
    def enterCrear_lista_cmd(self, ctx:NaturalToJsonParser.Crear_lista_cmdContext):
        pass

    # Exit a parse tree produced by NaturalToJsonParser#crear_lista_cmd.
    def exitCrear_lista_cmd(self, ctx:NaturalToJsonParser.Crear_lista_cmdContext):
        pass


    # Enter a parse tree produced by NaturalToJsonParser#items_lista.
    def enterItems_lista(self, ctx:NaturalToJsonParser.Items_listaContext):
        pass

    # Exit a parse tree produced by NaturalToJsonParser#items_lista.
    def exitItems_lista(self, ctx:NaturalToJsonParser.Items_listaContext):
        pass


    # Enter a parse tree produced by NaturalToJsonParser#valor.
    def enterValor(self, ctx:NaturalToJsonParser.ValorContext):
        pass

    # Exit a parse tree produced by NaturalToJsonParser#valor.
    def exitValor(self, ctx:NaturalToJsonParser.ValorContext):
        pass



del NaturalToJsonParser