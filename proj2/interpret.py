######IMPORTS######
from asyncore import read
from curses import ERR
from importlib.resources import path
from multiprocessing.context import assert_spawning
import re
import argparse
import sys
from tarfile import GNU_FORMAT
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

######FUNCTIONS######

def checkArgCount(expect, real):
    if expect != real:
        print("Invalid number of arfuments \n", file=sys.stderr)
        exit(ERR_WRG_XML)


######MAIN######

###PARSING###
argParser = argparse.ArgumentParser()
argParser.add_argument("--input", metavar="FILE", help="FILE which contains inputs of code")
argParser.add_argument("--source", metavar="FILE", help="Input file containing XML representation of code")

arguments = argParser.parse_args()

if arguments.input is None and arguments.source is None:
    print("ilegal combination of param", file=sys.stderr)
    exit(ERR_COMB_IN)

if arguments.input is not None:
    if exists(arguments.input):
        inputFile = arguments.input
    else:
        print("error with opening input file", file=sys.stderr)
        exit(ERR_OPEN_FILE)
else:
    inputFile = sys.stdin

if arguments.source is not None:
    if exists(arguments.source):
        sourceFile = arguments.source
    else:
        print("error with opening source file", file=sys.stderr)
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
    print("error with opening XML", file=sys.stderr)
    exit(ERR_FOR_XML)


root = tree.getroot()

