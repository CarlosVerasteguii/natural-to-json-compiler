// Encabezado de la gramática
grammar NaturalToJson;

/*
 * Gramática ANTLR v4 para el lenguaje "Natural a JSON".
 *
 * Propósito:
 * Esta gramática define la estructura léxica y sintáctica de un lenguaje
 * pseudo-natural diseñado para describir objetos y listas simples, con el
 * objetivo de transformarlos a formato JSON.
 *
 * El lenguaje permite comandos como:
 *   - CREAR OBJETO miObjeto CON propiedad1:"valor1", propiedad2:123
 *   - CREAR LISTA miLista CON ELEMENTOS "item1", 2, verdadero
 *
 * Genera un parser y lexer en Python 3.
 */

options {
    language=Python3;
}

// --- REGLAS SINTÁCTICAS ---

// La regla inicial (o axioma) de la gramática.
// Un programa consiste en cero o más comandos, seguidos por el fin de archivo (EOF).
programa : (comando)* EOF;

// Un comando puede ser la creación de un objeto o la creación de una lista.
// Esta es una regla de elección (alternativa).
comando
    : crear_objeto_cmd
    | crear_lista_cmd
    ;

// Define la sintaxis para crear un objeto JSON.
// Ejemplo: CREAR OBJETO miPerfil CON nombre:"Ana", edad:30
crear_objeto_cmd
    : CREAR OBJETO nombre_obj=IDENTIFICADOR CON propiedades
    ;

// Un conjunto de una o más propiedades para un objeto, separadas por comas.
// Ejemplo: nombre:"Ana", edad:30, activa:verdadero
propiedades
    : propiedad (COMA propiedad)*
    ;

// Define una única propiedad de un objeto, que consiste en una clave (identificador)
// y un valor, separados por dos puntos.
// Ejemplo: nombre:"Ana"
propiedad
    : clave=IDENTIFICADOR DOS_PUNTOS valor
    ;

// Define la sintaxis para crear una lista (array) JSON.
// Ejemplo: CREAR LISTA misNumeros CON ELEMENTOS 1, 2, 3, 4
crear_lista_cmd
    : CREAR LISTA nombre_lista=IDENTIFICADOR CON ELEMENTOS items_lista
    ;

// Un conjunto de uno o más valores para una lista, separados por comas.
// Ejemplo: "manzana", "banana", "cereza"
items_lista
    : valor (COMA valor)*
    ;

// Define los tipos de valores permitidos en el lenguaje, que se mapean
// directamente a los tipos de datos JSON (string, número, booleano).
valor
    : STRING          // Un valor de cadena de texto, ej: "hola mundo"
    | NUMERO_DECIMAL  // Un número decimal, ej: 3.14
    | NUMERO_ENTERO   // Un número entero, ej: 123
    | KW_VERDADERO    // El valor booleano verdadero
    | KW_FALSO        // El valor booleano falso
    ;

// --- REGLAS LÉXICAS ---

// Palabras clave del lenguaje.
// Se definen explícitamente para que el lexer las reconozca como tokens individuales
// y no como IDENTIFICADOR genérico. La definición letra por letra (ej. C R E A R)
// las hace insensibles a mayúsculas/minúsculas si los fragmentos A, B, C, etc.
// están definidos para incluir ambas cajas (como es el caso aquí).
CREAR     : C R E A R;
OBJETO    : O B J E T O;
LISTA     : L I S T A;
CON       : C O N;
ELEMENTOS : E L E M E N T O S;

// Palabras clave para valores booleanos.
KW_VERDADERO : V E R D A D E R O;
KW_FALSO     : F A L S O;

// Un identificador comienza con una letra (o guion bajo) seguido de cero o más
// letras, dígitos o guiones bajos.
IDENTIFICADOR
    : (LETRA_UNICODE | '_') (LETRA_UNICODE | DIGITO | '_')*
    ;

// Un string es cualquier secuencia de caracteres entre comillas dobles.
// No permite saltos de línea dentro del string.
STRING
    : '"' ( ~["\r\n] )* '"'
    ;

// Un número decimal, opcionalmente con signo negativo, con al menos un dígito
// antes y después del punto decimal.
NUMERO_DECIMAL
    : '-'? DIGITO+ '.' DIGITO+
    ;

// Un número entero, opcionalmente con signo negativo, compuesto por uno o más dígitos.
// Esta regla debe aparecer DESPUÉS de NUMERO_DECIMAL en la gramática para que
// el lexer priorice NUMERO_DECIMAL si encuentra un patrón que coincida con ambos
// (ej. "123.45" podría ser reconocido como NUMERO_ENTERO "123" seguido de ".45" si
// NUMERO_ENTERO estuviera antes y fuera más "greedy" o si NUMERO_DECIMAL no fuera específico).
// En este caso, la estructura es suficientemente distinta, pero es una buena práctica considerarlo.
NUMERO_ENTERO
    : '-'? DIGITO+
    ;

// Tokens para signos de puntuación.
DOS_PUNTOS : ':';
COMA       : ',';

// Los comentarios de línea (estilo //) se envían al canal OCULTO (HIDDEN).
// Esto significa que el parser no los verá, pero pueden ser accedidos si es necesario.
COMENTARIO_LINEA : '//' ~[\r\n]* -> channel(HIDDEN);

// Los espacios en blanco (espacios, tabuladores, saltos de línea) también se envían al canal OCULTO.
WHITESPACE       : [ \t\r\n]+ -> channel(HIDDEN);

// --- FRAGMENTOS LÉXICOS ---
// Los fragmentos son reglas léxicas parciales que no generan tokens por sí mismas,
// sino que son usadas para construir otras reglas léxicas.
// Estos fragmentos definen letras individuales, permitiendo que las palabras clave
// (CREAR, OBJETO, etc.) sean insensibles a mayúsculas/minúsculas.
fragment A : [aAÁá]; fragment B : [bB]; fragment C : [cC]; fragment D : [dD];
fragment E : [eEÉé]; fragment F : [fF]; fragment G : [gG]; fragment H : [hH];
fragment I : [iIÍí]; fragment J : [jJ]; fragment K : [kK]; fragment L : [lL];
fragment M : [mM]; fragment N : [nNÑñ]; fragment O : [oOÓó]; fragment P : [pP];
fragment Q : [qQ]; fragment R : [rR]; fragment S : [sS]; fragment T : [tT];
fragment U : [uUÚúÜü]; fragment V : [vV]; fragment W : [wW]; fragment X : [xX];
fragment Y : [yY]; fragment Z : [zZ];

// Fragmento para definir qué se considera una letra (incluyendo acentos y ñ).
// Usado en IDENTIFICADOR.
fragment LETRA_UNICODE : [a-zA-ZÁÉÍÓÚÜÑáéíóúüñ];
// Fragmento para definir un dígito.
fragment DIGITO        : [0-9];
