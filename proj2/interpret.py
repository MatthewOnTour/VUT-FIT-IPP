######IMPORTS######

import re
import argparse
import sys
import xml.etree.ElementTree as ET
from os.path import exists


######DEFINE ERRORS######
ERR_COMB_IN = 10            #missing param of script
ERR_OPEN_FILE = 11          #error with opening input file
ERR_WRITE_FILE = 12         #error with opening output file
ERR_FOR_XML = 31            #wrong format of XML document 
ERR_WRG_XML = 32            #unexpected struct of XML
ERR_SEM_CHECK = 52          #semantic error
ERR_OP_TYPE = 53            #error invalid type of operands
ERR_FRAME_EXIST = 54        #error with variable
ERR_FRAME_NON = 55          #frame does not exist
ERR_MISS_VALUE = 56         #missing value
ERR_WRONG_OP_VAL = 57       #error wrong operand value
ERR_STRING = 58             #error with string 

######GLOBAL VARIABLES######
instructions = list()
positionI = 0
sourceFile = ""
inputFile = ""
call = list()
call_dead = list()
label = dict()
TF = dict()
GF = dict()
LF = []

######CLASSES######
class Variable:
    def __init__(self, varType, value):
        self.type = varType
        self.value = value

class Argument:
    def __init__(self, argType, value):
        self.type = argType
        self.value = value

class Instruction:
    def __init__(self, name, number):
        self.name = name
        self.number = number
        self.args = []
    def argsCreate(self, type, value):
        self.args.append(Argument(type, value))
        


#####VALIDATION OF ARGs###### neviem ci je potrebna :shrug:
def validVar(validit):
    if not re.match(r"^(GF@|LF@|TF@)(?!@)[a-zA-Z\_\-\$\&\%\*\!\?][a-zA-Z0-9\_\-\$\&\%\*\!\?]*$", validit.value):
        print("Invalid argument try -> VAR \n", file=sys.stderr)
        exit(ERR_WRG_XML)

def validLabel(validit):
    if not re.match(r"^[a-zA-Z\_\-\$\&\%\*\!\?][a-zA-Z0-9\_\-\$\&\%\*\!\?]*$", validit.value):
        print("Invalid argument try -> LABEL \n", file=sys.stderr)
        exit(ERR_WRG_XML)

def validOthers(validit):
    if validit.type == "nil":
        print("Invalid argument nil \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    if validit.type == "int":
        if re.search(r"[^\d-]", validit.item):
            print("Invalid argument int \n", file=sys.stderr)
            exit(ERR_WRG_XML)
    if validit.type == "string":
        if validit.value is not None:
            if re.match(r"(\\\\[^0-9])|(\\\\[0-9][^0-9])|(\\\\[0-9][0-9][^0-9])|(\\\\$)", validit.value):
                print("Invalid argument string \n", file=sys.stderr)
                exit(ERR_WRG_XML)
            
    if validit.type == "bool":
        if not validit.value == "true" or validit.value == "false":
            print("Invalid argument bool \n", file=sys.stderr)
            exit(ERR_WRG_XML)

def validSymb(validit):
    if validit.type == "var":
        validVar(validit)
    else:
        validOthers(validit)


def validType(validit):
    if not re.match(r"^(string|int|bool)$", validit.value):
        print("Invalid argument Type \n", file=sys.stderr)
        exit(ERR_WRG_XML)

######CHECK ARGs######

def checkVar(names):
    if names.type != "var":
        print("Invalid argument try -> VAR \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    validVar(names)

def checkLabel(names):
    if names.args[0].type != "label":
        print("Invalid argument try -> LABEL \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    validLabel(names.args[0])

def checkSymb(names):
    if not(re.match(r"^(var|string|bool|int|nil)$", names.type)):
        print("Invalid argument try -> SYMB \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    validSymb(names)

def checkVarSymb(names):
    if names.args[0].type != "var":
        print("Invalid argument try -> VAR \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    validVar(names.args[0])
    if not(re.match(r"^(var|string|bool|int|nil)$", names.args[1].type)):
        print("Invalid argument try -> SYMB \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    validSymb(names.args[1])

def checkVarType(names):
    if names.args[0].type != "var":
        print("Invalid argument try -> VAR \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    validVar(names.args[0])
    if not(re.match(r"^(string|bool|int)$", names.args[1].type)):
        print("Invalid argument try -> TYPE \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    validType(names.args[1])

def checkLabelSymbSymb(names):
    if names.args[0].type != "label":
        print("Invalid argument try -> LABEL \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    checkLabel(names)
    if not(re.match(r"^(var|string|bool|int|nil)$", names.args[1].type)):
        print("Invalid argument try -> SYMB \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    checkSymb(names.args[1])
    if not(re.match(r"^(var|string|bool|int|nil)$", names.args[2].type)):
        print("Invalid argument try -> SYMB \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    checkSymb(names.args[2])

def checkVarSymbSymb(names):
    if names.args[0].type != "var":
        print("Invalid argument try -> VAR \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    checkVar(names.args[0])
    if not(re.match(r"^(var|string|bool|int|nil)$", names.args[1].type)):
        print("Invalid argument try -> SYMB \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    checkSymb(names.args[1])
    if not(re.match(r"^(var|string|bool|int|nil)$", names.args[2].type)):
        print("Invalid argument try -> SYMB \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    checkSymb(names.args[2])


######FUNCTIONS######

def checkArgCount(expect, real):
    if expect != real:
        print("Invalid number of arguments \n", file=sys.stderr)
        exit(ERR_WRG_XML)


def checkInstruction(names):
    ##NO ARG
    if names.name == "CREATEFRAME":
        checkArgCount(0, len(names.args))
    elif names.name == "PUSHFRAME":
        checkArgCount(0, len(names.args))
    elif names.name == "POPFRAME":
        checkArgCount(0, len(names.args))
    elif names.name == "RETURN":
        checkArgCount(0, len(names.args))
    elif names.name == "BREAK":
        checkArgCount(0, len(names.args))

    ##ONE ARG -> VAR
    elif names.name == "DEFVAR":
        checkArgCount(1, len(names.args))
        checkVar(names.args[0])
    elif names.name == "POPS":
        checkArgCount(1, len(names.args))
        checkVar(names.args[0])

    ##ONE ARG -> LABEL
    elif names.name == "CALL":
        checkArgCount(1, len(names.args))
        checkLabel(names)
    elif names.name == "LABEL":
        checkArgCount(1, len(names.args))
        checkLabel(names)
    elif names.name == "JUMP":
        checkArgCount(1, len(names.args))
        checkLabel(names)

    ##ONE ARG -> SYMB
    elif names.name == "PUSHS":
        checkArgCount(1, len(names.args))
        checkSymb(names.args[0])
    elif names.name == "WRITE":
        checkArgCount(1, len(names.args))
        checkSymb(names.args[0])
    elif names.name == "EXIT":
        checkArgCount(1, len(names.args))
        checkSymb(names.args[0])
    elif names.name == "DPRINT":
        checkArgCount(1, len(names.args))
        checkSymb(names.args[0])

    ##TWO ARG -> VAR, SYMB
    elif names.name == "MOVE":
        checkArgCount(2, len(names.args))
        checkVarSymb(names)
    elif names.name == "NOT":
        checkArgCount(2, len(names.args))
        checkVarSymb(names)
    elif names.name == "INT2CHAR":
        checkArgCount(2, len(names.args))
        checkVarSymb(names)
    elif names.name == "STRLEN":
        checkArgCount(2, len(names.args))
        checkVarSymb(names)
    elif names.name == "TYPE":
        checkArgCount(2, len(names.args))
        checkVarSymb(names)

    ##TWO ARG -> VAR, TYPE
    elif names.name == "READ":
        checkArgCount(2, len(names.args))
        checkVarType(names)
    
    ##THREE ARG -> LABEL, SYMB, SYMB
    elif names.name == "JUMPIFEQ":
        checkArgCount(3, len(names.args))
        checkLabelSymbSymb(names)
    elif names.name == "JUMPIFNEQ":
        checkArgCount(3, len(names.args))
        checkLabelSymbSymb(names)

    ##THREE ARG -> VAR, SYMB, SYMB
    elif names.name == "ADD":
        checkArgCount(3, len(names.args))
        checkVarSymbSymb(names)
    elif names.name == "SUB":
        checkArgCount(3, len(names.args))
        checkVarSymbSymb(names)
    elif names.name == "MUL":
        checkArgCount(3, len(names.args))
        checkVarSymbSymb(names)
    elif names.name == "IDIV":
        checkArgCount(3, len(names.args))
        checkVarSymbSymb(names)
    elif names.name == "LT":
        checkArgCount(3, len(names.args))
        checkVarSymbSymb(names)
    elif names.name == "GT":
        checkArgCount(3, len(names.args))
        checkVarSymbSymb(names)
    elif names.name == "EQ":
        checkArgCount(3, len(names.args))
        checkVarSymbSymb(names)
    elif names.name == "AND":
        checkArgCount(3, len(names.args))
        checkVarSymbSymb(names)
    elif names.name == "OR":
        checkArgCount(3, len(names.args))
        checkVarSymbSymb(names)
    elif names.name == "OR":
        checkArgCount(3, len(names.args))
        checkVarSymbSymb(names)
    elif names.name == "NOT":
        checkArgCount(3, len(names.args))
        checkVarSymbSymb(names)
    elif names.name == "STRI2INT":
        checkArgCount(3, len(names.args))
        checkVarSymbSymb(names)
    elif names.name == "CONCAT":
        checkArgCount(3, len(names.args))
        checkVarSymbSymb(names)
    elif names.name == "GETCHAR":
        checkArgCount(3, len(names.args))
        checkVarSymbSymb(names)
    elif names.name == "SETCHAR":
        checkArgCount(3, len(names.args))
        checkVarSymbSymb(names)
    else:
        print("Instruction is non valid \n", file=sys.stderr)
        exit(ERR_WRG_XML)

######MAIN######

###PARSING###
argParser = argparse.ArgumentParser()
argParser.add_argument("--input", metavar="FILE", help="FILE which contains inputs of code")
argParser.add_argument("--source", metavar="FILE", help="Input file containing XML representation of code")

arguments = argParser.parse_args()

if arguments.input is None and arguments.source is None:
    print("ilegal combination of param \n", file=sys.stderr)
    exit(ERR_COMB_IN)

if arguments.input is not None:
    if exists(arguments.input):
        inputFile = arguments.input
    else:
        print("error with opening input file \n", file=sys.stderr)
        exit(ERR_OPEN_FILE)
else:
    inputFile = sys.stdin

if arguments.source is not None:
    if exists(arguments.source):
        sourceFile = arguments.source
    else:
        print("error with opening source file \n", file=sys.stderr)
        exit(ERR_OPEN_FILE)
else:
    sourceFile = sys.stdin


###LOADING XML###
tree = None
try:
    if sourceFile:
        tree = ET.parse(sourceFile)

    else:
        tree = ET.parse(sys.stdin)
except:
    print("error with opening XML \n", file=sys.stderr)
    exit(ERR_FOR_XML)


root = tree.getroot()

####MANY IF/ELIF aka SWITCH####
if root.tag != "program" or 'language' not in root.attrib.keys():
    print("missing atribute \n", file=sys.stderr)
    exit(ERR_WRG_XML)
if root.attrib['language'] != "IPPcode22":
    print("Invalid xml language \n", file=sys.stderr)
    exit(ERR_WRG_XML)

try:
  root[:] = sorted(root, key=lambda child: (child.tag, int(child.get('order'))))
except:
  print("Error occured when sorting \n", file=sys.stderr)
  exit(ERR_WRG_XML)

checkOrder = 0

for child in root:
    if checkOrder == child.attrib['order']:
        print("wrong order in XML \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    checkOrder = child.attrib['order']


    instructions.append(Instruction(child.attrib['opcode'], child.attrib['order']))
    for cycle in child:
        instructions[-1].argsCreate(cycle.attrib['type'], cycle.text)
    checkInstruction(instructions[-1])

    if child.attrib['opcode'] == "LABEL":
        if instructions[-1].args[0].value in label.keys():
            print("LABEL duplicate was found \n", file=sys.stderr)
            exit(ERR_WRG_XML)
        label[instructions[-1].args[0].value] = child.attrib['order']

#####MAIN FUNCTION OF INTERPRET#####

def interpretMainFunction(instr):
    if instr.name.upper() == "MOVE":
        print("hallo")

    elif instr.name.upper() == "CREATEFRAME":
        print("hallo")

    elif instr.name.upper() == "PUSHFRAME":
        print("hallo")

    elif instr.name.upper() == "POPFRAME":
        print("hallo")

    elif instr.name.upper() == "DEFVAR":
        print("hallo")

    elif instr.name.upper() == "CALL":
        print("hallo")

    elif instr.name.upper() == "RETURN":
        print("hallo")

    elif instr.name.upper() == "PUSHS":
        print("hallo")

    elif instr.name.upper() == "POPS":
        print("hallo")

    elif instr.name.upper() == "ADD":
        print("hallo")

    elif instr.name.upper() == "SUB":
        print("hallo")

    elif instr.name.upper() == "MUL":
        print("hallo")

    elif instr.name.upper() == "IDIV":
        print("hallo")

    elif instr.name.upper() == "LT":
        print("hallo")

    elif instr.name.upper() == "GT":
        print("hallo")

    elif instr.name.upper() == "EQ":
        print("hallo")

    elif instr.name.upper() == "ADD":
        print("hallo")

    elif instr.name.upper() == "OR":
        print("hallo")
        
    elif instr.name.upper() == "NOT":
        print("hallo")

    elif instr.name.upper() == "INT2CHAR":
        print("hallo")
        
    elif instr.name.upper() == "STR2INT":
        print("hallo")

    elif instr.name.upper() == "READ":
        print("hallo")

    elif instr.name.upper() == "WRITE":
        print("hallo")

    elif instr.name.upper() == "CONCAT":
        print("hallo")

    elif instr.name.upper() == "STRLEN":
        print("hallo")

    elif instr.name.upper() == "GETCHAR":
        print("hallo")

    elif instr.name.upper() == "SETCHAR":
        print("hallo")

    elif instr.name.upper() == "TYPE":
        print("hallo")

    elif instr.name.upper() == "LABEL":
        print("hallo")

    elif instr.name.upper() == "JUMP":
        print("hallo")

    elif instr.name.upper() == "JUMPIFEQ":
        print("hallo")
        
    elif instr.name.upper() == "EXIT":
        print("hallo")

    elif instr.name.upper() == "DPRINT":
        print("hallo")

    elif instr.name.upper() == "BREAK":
        print("hallo")

#####INTREPRET#####
i=0
while i < len(instructions):
    interpretMainFunction(instructions[i])
    i += 1



print("blyat")