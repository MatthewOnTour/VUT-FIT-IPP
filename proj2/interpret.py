######IMPORTS
import re
import argparse
import sys
import xml.etree.ElementTree as ET
######DEFINE ERRORS
ERR_OPEN_FILE = 11 #error with opening input file
ERR_WRITE_FILE = 12 #error with opening output file
ERR_FOR_XML = 31 #wrong format of XML document 
ERR_WRG_XML = 32 #unexpected struct of XML
ERR_SEM_CHECK = 52
ERR_OP_TYPE = 53
ERR_FRAME_EXIST = 54
ERR_FRAME_NON = 55 

######GLOBAL VARIABLES
sourceFile = ""
inputFile = ""


######CLASSES
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

######FUNCTIONS

def checkArgCount(expect, real):
    if except != real:
        stderr.write("Invalid number of arfuments")
