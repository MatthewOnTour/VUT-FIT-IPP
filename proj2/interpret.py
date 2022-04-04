######IMPORTS######
from ast import arg
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
GF = dict()
TF = dict()
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
    
    def findArgs(self, type, value):
        self.args.append(arg(type, value))

    def getName(self):
        return self.name
    
    def getOrder(self):
        return self.number

    def argsSize(self):
        return len(self.args)

    def getArg1(self):
        return self.args[0]

    def getArg2(self):
        return self.args[1]

    def getArg3(self):
        return self.args[2]

#####VALIDATION OF ARGs######



######CHECK ARGs######

def checkVar(names):
    if names.args[0].type != "var":
        print("Invalid argument try -> VAR \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    #check

def checkLabel(names):
    if names.args[0].type != "label":
        print("Invalid argument try -> LABEL \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    #check

def checkSymb(names):
    if names.args[0].type != "var" or names.args[0].type != "string" or names.args[0].type != "bool" or names.args[0].type != "int" or names.args[0].type != "nil":
        print("Invalid argument try -> SYMBOL \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    #check

def checkVarSymb(names):
    if names.args[0].type != "var":
        print("Invalid argument try -> VAR \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    #check
    if names.args[0].type != "var" or names.args[0].type != "string" or names.args[0].type != "bool" or names.args[0].type != "int" or names.args[0].type != "nil":
        print("Invalid argument try -> SYMBOL \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    #check




######FUNCTIONS######

def checkArgCount(expect, real):
    if expect != real:
        print("Invalid number of arfuments \n", file=sys.stderr)
        exit(ERR_WRG_XML)

def chcekInstruction(names):
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
        #check
    elif names.name == "POPS":
        checkArgCount(1, len(names.args))
        #check

    ##ONE ARG -> LABEL
    elif names.name == "CALL":
        checkArgCount(1, len(names.args))
        #check
    elif names.name == "LABEL":
        checkArgCount(1, len(names.args))
        #check
    elif names.name == "JUMP":
        checkArgCount(1, len(names.args))
        #check

    ##ONE ARG -> SYMB
    elif names.name == "PUSHS":
        checkArgCount(1, len(names.args))
        #check
    elif names.name == "WRITE":
        checkArgCount(1, len(names.args))
        #check
    elif names.name == "EXIT":
        checkArgCount(1, len(names.args))
        #check
    elif names.name == "DPRINT":
        checkArgCount(1, len(names.args))
        #check

    ##TWO ARG -> VAR, SYMB
    elif names.name == "MOVE":
        checkArgCount(2, len(names.args))
        #check
    elif names.name == "NOT":
        checkArgCount(2, len(names.args))
        #check
    elif names.name == "INT2CHAR":
        checkArgCount(2, len(names.args))
        #check
    elif names.name == "STRLEN":
        checkArgCount(2, len(names.args))
        #check
    elif names.name == "TYPE":
        checkArgCount(2, len(names.args))
        #check

    ##TWO ARG -> VAR, TYPE
    elif names.name == "READ":
        checkArgCount(2, len(names.args))
        #check
    
    ##THREE ARG -> LABEL, SYMB, SYMB
    elif names.name == "JUMPIFEQ":
        checkArgCount(3, len(names.args))
        #check
    elif names.name == "JUMPIFNEQ":
        checkArgCount(3, len(names.args))
        #check

    ##THREE ARG -> VAR, SYMB, SYMB
    elif names.name == "ADD":
        checkArgCount(3, len(names.args))
        #check
    elif names.name == "SUB":
        checkArgCount(3, len(names.args))
        #check
    elif names.name == "MUL":
        checkArgCount(3, len(names.args))
        #check
    elif names.name == "IDIV":
        checkArgCount(3, len(names.args))
        #check
    elif names.name == "LT":
        checkArgCount(3, len(names.args))
        #check
    elif names.name == "GT":
        checkArgCount(3, len(names.args))
        #check
    elif names.name == "EQ":
        checkArgCount(3, len(names.args))
        #check
    elif names.name == "AND":
        checkArgCount(3, len(names.args))
        #check
    elif names.name == "OR":
        checkArgCount(3, len(names.args))
        #check
    elif names.name == "OR":
        checkArgCount(3, len(names.args))
        #check
    elif names.name == "NOT":
        checkArgCount(3, len(names.args))
        #check
    elif names.name == "STRI2INT":
        checkArgCount(3, len(names.args))
        #check
    elif names.name == "CONCAT":
        checkArgCount(3, len(names.args))
        #check
    elif names.name == "GETCHAR":
        checkArgCount(3, len(names.args))
        #check
    elif names.name == "SETCHAR":
        checkArgCount(3, len(names.args))
        #check
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
for i in instructions:
    chcekInstruction(i)


