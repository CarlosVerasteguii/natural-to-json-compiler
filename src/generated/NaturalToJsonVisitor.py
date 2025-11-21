# Generated from NaturalToJson.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .NaturalToJsonParser import NaturalToJsonParser
else:
    from NaturalToJsonParser import NaturalToJsonParser

# This class defines a complete generic visitor for a parse tree produced by NaturalToJsonParser.

class NaturalToJsonVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by NaturalToJsonParser#programa.
    def visitPrograma(self, ctx:NaturalToJsonParser.ProgramaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NaturalToJsonParser#comando.
    def visitComando(self, ctx:NaturalToJsonParser.ComandoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NaturalToJsonParser#crear_objeto_cmd.
    def visitCrear_objeto_cmd(self, ctx:NaturalToJsonParser.Crear_objeto_cmdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NaturalToJsonParser#propiedades.
    def visitPropiedades(self, ctx:NaturalToJsonParser.PropiedadesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NaturalToJsonParser#propiedad.
    def visitPropiedad(self, ctx:NaturalToJsonParser.PropiedadContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NaturalToJsonParser#crear_lista_cmd.
    def visitCrear_lista_cmd(self, ctx:NaturalToJsonParser.Crear_lista_cmdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NaturalToJsonParser#items_lista.
    def visitItems_lista(self, ctx:NaturalToJsonParser.Items_listaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NaturalToJsonParser#valor.
    def visitValor(self, ctx:NaturalToJsonParser.ValorContext):
        return self.visitChildren(ctx)



del NaturalToJsonParser