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
dataStack = []
jumpStack = []
TFFlag = False


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
    if validit.type == "int":
        if re.search(r"^(-){0,1}([0-9]*)$", validit.value) is None:
            print("Invalid argument int \n", file=sys.stderr)
            exit(ERR_WRG_XML)
    if validit.type == "string":
        if validit.value is not None:
            if re.match(r"(\\\\[^0-9])|(\\\\[0-9][^0-9])|(\\\\[0-9][0-9][^0-9])|(\\\\$)", validit.value):
                print("Invalid argument string \n", file=sys.stderr)
                exit(ERR_WRG_XML)
            
    if validit.type == "bool":
        if validit.value != "true" and validit.value != "false":
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
    if not(re.match(r"^(string|bool|int|type|nil)$", names.args[1].type)):
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
    names.name = names.name.upper()
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
    if child.tag != 'instruction':
        print("unknown instruction \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    if checkOrder == child.attrib['order']:
        print("wrong order in XML \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    checkOrder = child.attrib['order']
    if int(checkOrder) <= 0:
        print("negative order \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    countrer = 1
    if 'opcode' not in child.attrib.keys():
        print("missing opcode \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    if 'order' not in child.attrib.keys():
        print("missing order \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    instructions.append(Instruction(child.attrib['opcode'], child.attrib['order']))
    try:
        child[:] = sorted(child, key=lambda some: (some.tag, int(some.tag[3])))
    except:
        print("Error occured when sorting \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    for cycle in child:
        instructions[-1].argsCreate(cycle.attrib['type'], cycle.text)
        if not re.match(r'^arg[1-3]$', cycle.tag):
            print("wrong name of arg \n", file=sys.stderr)
            exit(ERR_WRG_XML)
        tmp = re.search(r'[0-9]+', cycle.tag)
        if int(tmp[0]) != countrer:
            print("wrong number of arg \n", file=sys.stderr)
            exit(ERR_WRG_XML)
            
        countrer += 1
    checkInstruction(instructions[-1])

    if child.attrib['opcode'] == "LABEL":
        if instructions[-1].args[0].value in label.keys():
            print("LABEL duplicate was found \n", file=sys.stderr)
            exit(ERR_SEM_CHECK)
        label[instructions[-1].args[0].value] = child.attrib['order']
#####FIND VAR#####
def findVar(nameVar):
    global TFFlag
    match = re.match(r'^(GF|LF|TF)@(.*)$', nameVar.value)
    var = match.group(1)
    name = match.group(2)
    if var == 'GF':
        if name in GF:
            return GF.get(name)
        else:
            print("non existing GF \n", file=sys.stderr)
            exit(ERR_FRAME_EXIST)
    if var == 'TF':
        if TFFlag == False:
            print("TF is undefined \n", file=sys.stderr)
            exit(ERR_FRAME_NON)
        if name in TF:
            return TF.get(name)
        else:
            print("non existing TF \n", file=sys.stderr)
            exit(ERR_FRAME_EXIST)
    if var == 'LF':
        if len(LF) == 0:
            print("LF is undefined \n", file=sys.stderr)
            exit(ERR_FRAME_NON)
        if name in LF[-1]:
            return LF[-1].get(name)
        else:
            print("non existing LF \n", file=sys.stderr)
            exit(ERR_FRAME_EXIST)
#####FIND ALL#####
def findAll(nameAll):
    if nameAll is None:
        print("non existing value \n", file=sys.stderr)
        exit(ERR_MISS_VALUE)
    if nameAll.type == 'var':
        tmp = findVar(nameAll)
    else: 
        tmp = nameAll
    return tmp.value , tmp.type

#####MAIN FUNCTION OF INTERPRET#####

def interpretMainFunction(instr):
    global positionI
    global TF
    global LF
    global TFFlag


    if instr.name.upper() == "MOVE":
        var = findVar(instr.args[0])
        val, type = findAll(instr.args[1])
        if type == None:
            print("uninit var \n", file=sys.stderr)
            exit(ERR_MISS_VALUE)

        var.value = val
        var.type = type
        

    elif instr.name.upper() == "CREATEFRAME":
        TF.clear()
        TFFlag = True

    elif instr.name.upper() == "PUSHFRAME":
        if TFFlag == False:
            print("cant push, TF is undefined \n", file=sys.stderr)
            exit(ERR_FRAME_NON)
        LF.append(TF.copy())
        TF.clear()
        TFFlag = False

    elif instr.name.upper() == "POPFRAME":
        if len(LF) == 0:
            print("LF is undefined \n", file=sys.stderr)
            exit(ERR_FRAME_NON)
        TF = LF.pop()
        TFFlag = True
        

    elif instr.name.upper() == "DEFVAR":
        match = re.match(r'^(GF|LF|TF)@(.*)$', instr.args[0].value)
        var = match.group(1)
        name = match.group(2)
        if var == 'GF':
            if name in GF.keys():
                print("GF is existing \n", file=sys.stderr)
                exit(ERR_SEM_CHECK)
            GF.update({name:Variable(None,None)})
           
        
        elif var == 'TF':
            if TFFlag == False:
                print("TF is undefined \n", file=sys.stderr)
                exit(ERR_FRAME_NON)
            if name in TF.keys():
                print("TF is existing \n", file=sys.stderr)
                exit(ERR_SEM_CHECK)
            TF.update({name: Variable(None, None)})
            

        elif var == 'LF':
            if len(LF) == 0:
                print("LF is undefined \n", file=sys.stderr)
                exit(ERR_FRAME_NON)
            if name in LF[-1].keys():
                print("LF is existing \n", file=sys.stderr)
                exit(ERR_SEM_CHECK)
            LF[-1].update({name: Variable(None, None)})
           

    elif instr.name.upper() == "CALL":
        lab = instr.args[0]
        
        if lab.value not in label.keys():
            print("label not existing \n", file=sys.stderr)
            exit(ERR_SEM_CHECK)

        jumpStack.append(positionI)
        while int(label[lab.value]) != int(instructions[positionI].number):
            if int(label[lab.value]) < int(instructions[positionI].number):
                positionI -= 1
            else:
                positionI += 1
        

    elif instr.name.upper() == "RETURN":
        if len(jumpStack) == 0:
            print("cant return stack is empty \n", file=sys.stderr)
            exit(ERR_MISS_VALUE)
        positionI = jumpStack.pop(-1)
        

    elif instr.name.upper() == "PUSHS":
        val, type = findAll(instr.args[0])
        if type == None:
            print("Empty stack cant pop \n", file=sys.stderr)
            exit(ERR_MISS_VALUE)
        tmp = Argument(type, val)
        dataStack.append(tmp)
        

    elif instr.name.upper() == "POPS":
        if len(dataStack) == 0:
            print("Empty stack cant pop \n", file=sys.stderr)
            exit(ERR_MISS_VALUE)
        var = findVar(instr.args[0])
        sym = dataStack.pop(-1)
        
        var.value = sym.value
        var.type = sym.type

    elif instr.name.upper() == "ADD":
        var = findVar(instr.args[0])
        symb1 = instr.args[1]
        symb2 = instr.args[2]
        if symb1.type == 'var':
            symb1 = findVar(instr.args[1])
        if symb2.type == 'var':
            symb2 = findVar(instr.args[2])
        if symb1.type == None or symb2.type == None:
            print("uninit var \n", file=sys.stderr)
            exit(ERR_MISS_VALUE)
        if symb1.type != "int":
            print("arg has to be INT \n", file=sys.stderr)
            exit(ERR_OP_TYPE)
        if symb2.type != "int":
            print("arg has to be INT \n", file=sys.stderr)
            exit(ERR_OP_TYPE)
        var.type = 'int'
        var.value = int(symb1.value) + int(symb2.value)
        
        
    elif instr.name.upper() == "SUB":
        var = findVar(instr.args[0])
        symb1 = instr.args[1]
        symb2 = instr.args[2]
        if symb1.type == 'var':
            symb1 = findVar(instr.args[1])
        if symb2.type == 'var':
            symb2 = findVar(instr.args[2])
        if symb1.type == None or symb2.type == None:
            print("uninit var \n", file=sys.stderr)
            exit(ERR_MISS_VALUE)
        if symb1.type != "int":
            print("arg has to be INT \n", file=sys.stderr)
            exit(ERR_OP_TYPE)
        if symb2.type != "int":
            print("arg has to be INT \n", file=sys.stderr)
            exit(ERR_OP_TYPE)
        var.type = 'int'
        var.value = int(symb1.value) - int(symb2.value)


    elif instr.name.upper() == "MUL":
        var = findVar(instr.args[0])
        symb1 = instr.args[1]
        symb2 = instr.args[2]
        if symb1.type == 'var':
            symb1 = findVar(instr.args[1])
        if symb2.type == 'var':
            symb2 = findVar(instr.args[2])
        if symb1.type == None or symb2.type == None:
            print("uninit var \n", file=sys.stderr)
            exit(ERR_MISS_VALUE)
        if symb1.type != "int":
            print("arg has to be INT \n", file=sys.stderr)
            exit(ERR_OP_TYPE)
        if symb2.type != "int":
            print("arg has to be INT \n", file=sys.stderr)
            exit(ERR_OP_TYPE)
        var.type = 'int'
        var.value = int(symb1.value) * int(symb2.value)


    elif instr.name.upper() == "IDIV":
        var = findVar(instr.args[0])
        symb1 = instr.args[1]
        symb2 = instr.args[2]
        if symb1.type == 'var':
            symb1 = findVar(instr.args[1])
        if symb2.type == 'var':
            symb2 = findVar(instr.args[2])
        if symb1.type == None or symb2.type == None:
            print("uninit var \n", file=sys.stderr)
            exit(ERR_MISS_VALUE)
        if symb1.type != "int":
            print("arg has to be INT \n", file=sys.stderr)
            exit(ERR_OP_TYPE)
        if symb2.type != "int":
            print("arg has to be INT \n", file=sys.stderr)
            exit(ERR_OP_TYPE)
        if int(symb2.value) == 0:
            print("illegal operation div by 0 \n", file=sys.stderr)
            exit(ERR_WRONG_OP_VAL)
        var.value = int(symb1.value) // int(symb2.value)
        var.type = 'int'


    elif instr.name.upper() == "LT":
        var = findVar(instr.args[0])
        symb1 = instr.args[1]
        symb2 = instr.args[2]
        if symb1.type == 'var':
            symb1 = findVar(instr.args[1])
        if symb2.type == 'var':
            symb2 = findVar(instr.args[2])
        if symb1.type == None or symb2.type == None:
            print("uninit var \n", file=sys.stderr)
            exit(ERR_MISS_VALUE)
        
        if symb1.type != symb2.type:
            print("symb1 and symb2 are not same \n", file=sys.stderr)
            exit(ERR_OP_TYPE)
        if symb1.type == "int":
            if int(symb1.value) < int(symb2.value):
                var.type = "bool"
                var.value = "true"
            else:
                var.type = "bool"
                var.value = "false"
        elif symb1.type == "bool":
            if symb1.value < symb2.value:
                var.type = "bool"
                var.value = "true"
            else:
                var.type = "bool"
                var.value = "false"
        elif symb1.type == "string":
            tmp = re.split(r"\\", '' if symb1.value is None else symb1.value)
            tmp2 = ""
            for i in range(0, len(tmp)):
                if i == 0:
                    tmp2 += tmp[i]
                elif len(tmp[i]) > 3:
                    tmp2 += chr(int((tmp[i][:3])))
                    tmp2 += tmp[i][3:]
                else:
                    tmp2 += chr(int((tmp[i])))
            tmp3 = re.split(r"\\", '' if symb2.value is None else symb2.value)
            tmp4 = ""
            for i in range(0, len(tmp3)):
                if i == 0:
                    tmp4 += tmp3[i]
                elif len(tmp3[i]) > 3:
                    tmp4 += chr(int((tmp3[i][:3])))
                    tmp4 += tmp3[i][3:]
                else:
                    tmp4 += chr(int((tmp3[i])))

            if tmp2 < tmp4:
                var.type = "bool"
                var.value = "true"
            else:
                var.type = "bool"
                var.value = "false"
        else:
            print("symb1 and symb2 are not int/bool/string \n", file=sys.stderr)
            exit(ERR_OP_TYPE)

    elif instr.name.upper() == "GT":
        var = findVar(instr.args[0])
        symb1 = instr.args[1]
        symb2 = instr.args[2]
        if symb1.type == 'var':
            symb1 = findVar(instr.args[1])
        if symb2.type == 'var':
            symb2 = findVar(instr.args[2])
        if symb1.type == None or symb2.type == None:
            print("uninit var \n", file=sys.stderr)
            exit(ERR_MISS_VALUE)
        if symb1.type != symb2.type:
            print("symb1 and symb2 are not same \n", file=sys.stderr)
            exit(ERR_OP_TYPE)
        if symb1.type == "int":
            if int(symb1.value) > int(symb2.value):
                var.type = "bool"
                var.value = "true"
            else:
                var.type = "bool"
                var.value = "false"
        elif symb1.type == "bool":
            if symb1.value > symb2.value:
                var.type = "bool"
                var.value = "true"
            else:
                var.type = "bool"
                var.value = "false"
        elif symb1.type == "string":
            tmp = re.split(r"\\", '' if symb1.value is None else symb1.value)
            tmp2 = ""
            for i in range(0, len(tmp)):
                if i == 0:
                    tmp2 += tmp[i]
                elif len(tmp[i]) > 3:
                    tmp2 += chr(int((tmp[i][:3])))
                    tmp2 += tmp[i][3:]
                else:
                    tmp2 += chr(int((tmp[i])))
            tmp3 = re.split(r"\\", '' if symb2.value is None else symb2.value)
            tmp4 = ""
            for i in range(0, len(tmp3)):
                if i == 0:
                    tmp4 += tmp3[i]
                elif len(tmp3[i]) > 3:
                    tmp4 += chr(int((tmp3[i][:3])))
                    tmp4 += tmp3[i][3:]
                else:
                    tmp4 += chr(int((tmp3[i])))

            if tmp2 > tmp4:
                var.type = "bool"
                var.value = "true"
            else:
                var.type = "bool"
                var.value = "false"
        else:
            print("symb1 and symb2 are not int/bool/string \n", file=sys.stderr)
            exit(ERR_OP_TYPE)

    elif instr.name.upper() == "EQ":
        var = findVar(instr.args[0])
        symb1 = instr.args[1]
        symb2 = instr.args[2]
        if symb1.type == 'var':
            symb1 = findVar(instr.args[1])
        if symb2.type == 'var':
            symb2 = findVar(instr.args[2])
        if symb1.type == None or symb2.type == None:
            print("uninit var \n", file=sys.stderr)
            exit(ERR_MISS_VALUE)
        if symb1.type != symb2.type:
            if symb1.type == 'nil' or symb2.type == 'nil':
                var.type = "bool"
                var.value = "false"
            else:
                print("symb1 and symb2 are not same \n", file=sys.stderr)
                exit(ERR_OP_TYPE)
        elif symb1.type == "int":
            if int(symb1.value) == int(symb2.value):
                var.type = "bool"
                var.value = "true"
            else:
                var.type = "bool"
                var.value = "false"
        elif symb1.type == "bool":
            if symb1.value == symb2.value:
                var.type = "bool"
                var.value = "true"
            else:
                var.type = "bool"
                var.value = "false"
        elif symb1.type == "string":
            tmp = re.split(r"\\", '' if symb1.value is None else symb1.value)
            tmp2 = ""
            for i in range(0, len(tmp)):
                if i == 0:
                    tmp2 += tmp[i]
                elif len(tmp[i]) > 3:
                    tmp2 += chr(int((tmp[i][:3])))
                    tmp2 += tmp[i][3:]
                else:
                    tmp2 += chr(int((tmp[i])))
            tmp3 = re.split(r"\\", '' if symb2.value is None else symb2.value)
            tmp4 = ""
            for i in range(0, len(tmp3)):
                if i == 0:
                    tmp4 += tmp3[i]
                elif len(tmp3[i]) > 3:
                    tmp4 += chr(int((tmp3[i][:3])))
                    tmp4 += tmp3[i][3:]
                else:
                    tmp4 += chr(int((tmp3[i])))
            
            if tmp2 == tmp4:
                var.type = "bool"
                var.value = "true"
            else:
                var.type = "bool"
                var.value = "false"
        elif symb1.type == 'nil':
            if symb1.value == symb2.value:
                var.type = "bool"
                var.value = "true"
            else:
                var.type = "bool"
                var.value = "false"
        else:
            print("symb1 and symb2 are not int/bool/string \n", file=sys.stderr)
            exit(ERR_OP_TYPE)

    elif instr.name.upper() == "AND":
        var = findVar(instr.args[0])
        symb1 = instr.args[1]
        symb2 = instr.args[2]
        if symb1.type == 'var':
            symb1 = findVar(instr.args[1])
        if symb2.type == 'var':
            symb2 = findVar(instr.args[2])
        if symb1.type == None or symb2.type == None:
            print("uninit var \n", file=sys.stderr)
            exit(ERR_MISS_VALUE)
        if symb1.type != symb2.type:
            print("symb1 and symb2 are not same \n", file=sys.stderr)
            exit(ERR_OP_TYPE)
        if symb1.type == 'bool':
            if symb1.value == 'true' and symb2.value == 'true':
                var.type = "bool"
                var.value = "true"
            else:
                var.type = "bool"
                var.value = "false"
        else:
            print("symb1 and symb2 are not bool \n", file=sys.stderr)
            exit(ERR_OP_TYPE)

    elif instr.name.upper() == "OR":
        var = findVar(instr.args[0])
        symb1 = instr.args[1]
        symb2 = instr.args[2]
        if symb1.type == 'var':
            symb1 = findVar(instr.args[1])
        if symb2.type == 'var':
            symb2 = findVar(instr.args[2])
        if symb1.type == None or symb2.type == None:
            print("uninit var \n", file=sys.stderr)
            exit(ERR_MISS_VALUE)
        if symb1.type != symb2.type:
            print("symb1 and symb2 are not same \n", file=sys.stderr)
            exit(ERR_OP_TYPE)
        if symb1.type == 'bool':
            if symb1.value == 'false' and symb2.value == 'false':
                var.type = "bool"
                var.value = "false"
            else:
                var.type = "bool"
                var.value = "true"
        else:
            print("symb1 and symb2 are not bool \n", file=sys.stderr)
            exit(ERR_OP_TYPE)
        
    elif instr.name.upper() == "NOT":
        var = findVar(instr.args[0])
        symb = instr.args[1]
        if symb.type == 'var':
            symb = findVar(instr.args[1])
        if symb.type == None:
            print("uninit var \n", file=sys.stderr)
            exit(ERR_MISS_VALUE)
        if symb.type == 'bool':
            if symb.value == 'false':
                var.type = "bool"
                var.value = "true"
            else:
                var.type = "bool"
                var.value = "false"
        else:
            print("symb1 and symb2 are not bool \n", file=sys.stderr)
            exit(ERR_OP_TYPE)

    elif instr.name.upper() == "INT2CHAR":
        var = findVar(instr.args[0])
        symb = instr.args[1]
        if symb.type == 'var':
            symb = findVar(instr.args[1])
        if symb.type == None:
            print("uninit var \n", file=sys.stderr)
            exit(ERR_MISS_VALUE)
        if symb.type != 'int':
            print("cant convert non int value \n", file=sys.stderr)
            exit(ERR_OP_TYPE)
        try:
            var.type = "string"
            var.value = chr(int(symb.value))
        except:
            print("cant convert int to char \n", file=sys.stderr)
            exit(ERR_STRING)
        
    elif instr.name.upper() == "STRI2INT":
        var = findVar(instr.args[0])
        symb1 = instr.args[1]
        symb2 = instr.args[2]
        if symb1.type == 'var':
            symb1 = findVar(instr.args[1])
        if symb2.type == 'var':
            symb2 = findVar(instr.args[2])
        if symb1.type == None or symb2.type == None:
            print("uninit var \n", file=sys.stderr)
            exit(ERR_MISS_VALUE)
        if symb1.type != 'string' or symb2.type != 'int':
            print("wrong types when STRI2INT \n", file=sys.stderr)
            exit(ERR_OP_TYPE)
        if int(symb2.value) < 0:
            print("out of range \n", file=sys.stderr)
            exit(ERR_STRING)
        try:
            var.type = "int"
            var.value = ord(symb1.value[int(symb2.value)])
        except:
            print("out of range \n", file=sys.stderr)
            exit(ERR_STRING)
        

    elif instr.name.upper() == "READ":
        var = findVar(instr.args[0])
        symb = instr.args[1]
        if symb.type == 'var':
            symb = findVar(instr.args[1])
        inVar = inputFile.readline()
        if symb.type == None:
            print("uninit var \n", file=sys.stderr)
            exit(ERR_MISS_VALUE)
        if symb.value == 'int':
            try:
                var.type = "int"
                var.value = int(inVar)
            except:
                var.type = "nil"
                var.value = "nil"
        elif symb.value == 'string':
            if inVar == '':
                var.type = 'nil'
                var.value = 'nil'
            else:
                var.type = "string"
                var.value = inVar[:-1]
        elif symb.value == 'bool':
            inVar = inVar[:-1].lower()
            if inVar == 'true':
                var.type = 'bool'
                var.value = 'true'
            elif inVar == '':
                var.type = 'nil'
                var.value = 'nil'
            else:
                var.type = 'bool'
                var.value = 'false'
        elif symb.value == 'float':
            try:
                var.type = symb.type
                var.value = float.fromhex(inVar)
            except:
                var.type = "nil"
                var.value = "nil"
        else:
           print("invalid type \n", file=sys.stderr)
           exit(ERR_OP_TYPE)


    elif instr.name.upper() == "WRITE":
        symb = instr.args[0]
        if symb.type == 'var':
            symb = findVar(instr.args[0])
        if symb.type == None:
            print("uninit var \n", file=sys.stderr)
            exit(ERR_MISS_VALUE)
        if symb.value == None:
            print("", end='')
        elif symb.type == 'nil':
            print("",end = '')
        elif symb.type == 'float':
            print(float.hex(symb.value), end='')
        elif symb.type == 'bool':
            if symb.value == 'true':
                print("true", end='')
            else:
                print("false", end='')
        elif symb.type == 'int':
            print(symb.value, end='')
        else:
            tmp = re.split(r"\\", symb.value)
            tmp2 = ""
            for i in range(0, len(tmp)):
                if i == 0:
                    tmp2 += tmp[i]
                elif len(tmp[i]) > 3:
                    tmp2 += chr(int((tmp[i][:3])))
                    tmp2 += tmp[i][3:]
                elif int(len(tmp[i])) == 0:
                    tmp2 += '\\'
                else:
                    try:
                        tmp2 += chr(int((tmp[i])))
                    except:
                        tmp2 += tmp[i]
            print(tmp2 ,end = '')
        

    elif instr.name.upper() == "CONCAT":
        var = findVar(instr.args[0])
        symb1 = instr.args[1]
        symb2 = instr.args[2]
        if symb1.type == 'var':
            symb1 = findVar(instr.args[1])
        if symb2.type == 'var':
            symb2 = findVar(instr.args[2])
        if symb1.type == None or symb2.type == None:
            print("uninit var \n", file=sys.stderr)
            exit(ERR_MISS_VALUE)
        if symb1.type != 'string' or symb2.type != 'string':
            print("out of range \n", file=sys.stderr)
            exit(ERR_OP_TYPE)

        if symb1.value == None:
            symb1.value = ""
        if symb2.value == None:
            symb2.value = ""
        var.type = symb1.type
        var.value = symb1.value + symb2.value

    elif instr.name.upper() == "STRLEN":
        var = findVar(instr.args[0])
        symb = instr.args[1]
        if symb.type == 'var':
            symb = findVar(instr.args[1])
        symb.value = '' if symb.value == None else symb.value
        if symb.type == 'string':
            var.type = 'int'
            var.value = len(symb.value)
        elif symb.type == None:
            print("invalid type \n", file=sys.stderr)
            exit(ERR_MISS_VALUE)
        else:
            print("invalid type \n", file=sys.stderr)
            exit(ERR_OP_TYPE)

    elif instr.name.upper() == "GETCHAR":
        var = findVar(instr.args[0])
        symb1 = instr.args[1]
        symb2 = instr.args[2]
        if symb1.type == 'var':
            symb1 = findVar(instr.args[1])
        if symb2.type == 'var':
            symb2 = findVar(instr.args[2])
        if symb1.type == None or symb2.type == None:
            print("uninit var \n", file=sys.stderr)
            exit(ERR_MISS_VALUE)
        if symb1.type != 'string' or symb2.type != 'int':
            print("invalid arg type \n", file=sys.stderr)
            exit(ERR_OP_TYPE)
        if int(len(symb1.value)) <= int(symb2.value) or int(symb2.value) < 0:
            print("invalid range \n", file=sys.stderr)
            exit(ERR_STRING)
        var.type = 'string'
        var.value = symb1.value[int(symb2.value)]

    elif instr.name.upper() == "SETCHAR":
        var = findVar(instr.args[0])
        symb1 = instr.args[1]
        symb2 = instr.args[2]
        if symb1.type == 'var':
            symb1 = findVar(instr.args[1])
        if symb2.type == 'var':
            symb2 = findVar(instr.args[2])
        if var.type == None or symb1.type == None or symb2.type == None:
            print("var is none \n", file=sys.stderr)
            exit(ERR_MISS_VALUE)
        if var.type != 'string':
            print("var have to be str \n", file=sys.stderr)
            exit(ERR_OP_TYPE)
        if symb1.type != 'int':
            print("symb1 has to be int \n", file=sys.stderr)
            exit(ERR_OP_TYPE)
        if symb2.type != 'string':
            print("symb2 has to be string \n", file=sys.stderr)
            exit(ERR_OP_TYPE)
        if symb2.value == None:
            print("empty str \n", file=sys.stderr)
            exit(ERR_STRING)
        if int(symb1.value) >= len(var.value) or int(symb1.value) < 0:
            print("wrong index \n", file=sys.stderr)
            exit(ERR_STRING)
        tmp = var.value
        tmp1 = re.split(r"\\", '' if symb2.value is None else symb2.value)
        tmp2 = ""
        for i in range(0, len(tmp1)):
            if i == 0:
                tmp2 += tmp1[i]
            elif len(tmp1[i]) > 3:
                tmp2 += chr(int((tmp1[i][:3])))
                tmp2 += tmp1[i][3:]
            else:
                tmp2 += chr(int((tmp1[i])))
        symb2.value = tmp2
        var.value = tmp[:int(symb1.value)] + symb2.value[0] + tmp[int(symb1.value)+1:]
        var.type = 'string'
        

    elif instr.name.upper() == "TYPE":
        var = findVar(instr.args[0])
        symb = instr.args[1]
        if symb.type == 'var':
            symb = findVar(instr.args[1])
        
        if symb.type == 'none':
            symb.type = ""
        if symb.type == 'type':
            var.value = 'string'
            var.type = 'string'
            
        else:
            var.value = symb.type
            var.type = 'string'

    elif instr.name.upper() == "LABEL":
        pass

    elif instr.name.upper() == "JUMP":
        lab = instr.args[0]

        if lab.value not in label.keys():
            print("label not existing \n", file=sys.stderr)
            exit(ERR_SEM_CHECK)
        while int(label[lab.value]) != int(instructions[positionI].number):
            if int(label[lab.value]) < int(instructions[positionI].number):
                positionI -= 1
            else:
                positionI += 1
        positionI -= 1

    elif instr.name.upper() == "JUMPIFEQ":
        lab = instr.args[0]
        symb1 = instr.args[1]
        symb2 = instr.args[2]
        if symb1.type == 'var':
            symb1 = findVar(instr.args[1])
        if symb2.type == 'var':
            symb2 = findVar(instr.args[2])
        if symb1.type == None or symb2.type == None:
            print("uninit var \n", file=sys.stderr)
            exit(ERR_MISS_VALUE)
        if lab.value not in label.keys():
            print("label not existing \n", file=sys.stderr)
            exit(ERR_SEM_CHECK)
        if symb1.type == symb2.type:
            if symb1.type == 'int':
                symb1.value = int(symb1.value)
                symb2.value = int(symb2.value)
            elif symb1.type == 'string':
                tmp = re.split(r"\\", '' if symb1.value is None else symb1.value)
                tmp2 = ""
                for i in range(0, len(tmp)):
                    if i == 0:
                        tmp2 += tmp[i]
                    elif len(tmp[i]) > 3:
                        tmp2 += chr(int((tmp[i][:3])))
                        tmp2 += tmp[i][3:]
                    else:
                        tmp2 += chr(int((tmp[i])))
                tmp3 = re.split(r"\\", '' if symb2.value is None else symb2.value)
                tmp4 = ""
                for i in range(0, len(tmp3)):
                    if i == 0:
                        tmp4 += tmp3[i]
                    elif len(tmp3[i]) > 3:
                        tmp4 += chr(int((tmp3[i][:3])))
                        tmp4 += tmp3[i][3:]
                    else:
                        tmp4 += chr(int((tmp3[i])))
                symb1.value = tmp2
                symb2.value = tmp4

            if symb1.value == symb2.value:
                while int(label[lab.value]) != int(instructions[positionI].number):
                    if int(label[lab.value]) < int(instructions[positionI].number):
                        positionI -= 1
                    else:
                        positionI += 1
                positionI -= 1
        elif symb1.type == 'nil' or symb2.type == 'nil':
            if symb1.value == symb2.value: 
                while int(label[lab.value]) != int(instructions[positionI].number):
                    if int(label[lab.value]) < int(instructions[positionI].number):
                        positionI -= 1
                    else:
                        positionI += 1
                positionI -= 1
        
        else:
            print("wrong types \n", file=sys.stderr)
            exit(ERR_OP_TYPE)

    elif instr.name.upper() == "JUMPIFNEQ":
        lab = instr.args[0]
        symb1 = instr.args[1]
        symb2 = instr.args[2]
        if symb1.type == 'var':
            symb1 = findVar(instr.args[1])
        if symb2.type == 'var':
            symb2 = findVar(instr.args[2])
        if symb1.type == None or symb2.type == None:
            print("uninit var \n", file=sys.stderr)
            exit(ERR_MISS_VALUE)
        if lab.value not in label.keys():
            print("label not existing \n", file=sys.stderr)
            exit(ERR_SEM_CHECK)
        if symb1.type == symb2.type:
            if symb1.type == 'int':
                symb1.value = int(symb1.value)
                symb2.value = int(symb2.value)
            elif symb1.type == 'string':
                tmp = re.split(r"\\", '' if symb1.value is None else symb1.value)
                tmp2 = ""
                for i in range(0, len(tmp)):
                    if i == 0:
                        tmp2 += tmp[i]
                    elif len(tmp[i]) > 3:
                        tmp2 += chr(int((tmp[i][:3])))
                        tmp2 += tmp[i][3:]
                    else:
                        tmp2 += chr(int((tmp[i])))
                tmp3 = re.split(r"\\", '' if symb2.value is None else symb2.value)
                tmp4 = ""
                for i in range(0, len(tmp3)):
                    if i == 0:
                        tmp4 += tmp3[i]
                    elif len(tmp3[i]) > 3:
                        tmp4 += chr(int((tmp3[i][:3])))
                        tmp4 += tmp3[i][3:]
                    else:
                        tmp4 += chr(int((tmp3[i])))
                symb1.value = tmp2
                symb2.value = tmp4
            if symb1.value != symb2.value:
                while int(label[lab.value]) != int(instructions[positionI].number):
                    if int(label[lab.value]) < int(instructions[positionI].number):
                        positionI -= 1
                    else:
                        positionI += 1
                    
        elif symb1.type == 'nil' or symb2.type == 'nil':
            if symb1.value != symb2.value: 
                while int(label[lab.value]) != int(instructions[positionI].number):
                    if int(label[lab.value]) < int(instructions[positionI].number):
                        positionI -= 1
                    else:
                        positionI += 1
                    
        else:
            print("wrong types \n", file=sys.stderr)
            exit(ERR_OP_TYPE)
        
    elif instr.name.upper() == "EXIT":
        if instr.args[0].type != 'int':
            print("invalid type \n", file=sys.stderr)
            exit(ERR_OP_TYPE)
        if int(instr.args[0].value) < 0 or int(instr.args[0].value) > 49:
            print("invalid type \n", file=sys.stderr)
            exit(ERR_WRONG_OP_VAL)

        sys.exit(int(instr.args[0].value))

    elif instr.name.upper() == "DPRINT":
        print(instr.args[0].type, file=sys.stderr)
    elif instr.name.upper() == "BREAK":
        pass
        print("TBD", file=sys.stderr)
    else:
        print("Instruction was not found \n", file=sys.stderr)
        exit(ERR_WRG_XML)
    positionI += 1

#####INTREPRET#####

while positionI < len(instructions):
    interpretMainFunction(instructions[positionI])
