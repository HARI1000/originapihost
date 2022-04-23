from http.client import ImproperConnectionState
from flask import Flask,jsonify,request
from flask_cors import CORS
import sys

app = Flask(__name__)
CORS(app)
#app.config["DEBUG"] = True
#cors=CORS(app,resources={r'*':{'origins':'*'}})

@app.route('/<string:prg>', methods=['GET'])
def home(prg):
    theprg=prg
    print(theprg)
    def printfunctions(linecode):
        variable=[]
        #If just statements and no variables
        if('''",''' not in linecode and not linecode.startswith('#') and '''("''' in linecode):
            linecode = str(linecode)
            linecode = linecode.replace("print", "printf")
            coutputcode.append(linecode)
    
        #If there are variables
        elif('''",''' in linecode and not linecode.startswith('#')):
            variablecount=linecode.count('''",''')
            linecode=linecode.replace("print","printf")
            place=linecode.split('''",''')
            
            #Code to get all the letters in the variable name
            for i in place[1:]:
                instantvalues=i.split(",")
                variable.append(instantvalues[0])
            
            #Converting Python to C    
            linecode=linecode.replace(''',"'''," ")
            for i in range(0,variablecount):
                
                #Removing Bracket from the last variable name
                if(")" in variable[i]):
                   variable[i]=variable[i].replace(")","")
                
                #Converting Data types as well   
                if("int "+variable[i] in coutputcode):
                    linecode=linecode.replace('''",'''+variable[i],"%d")
                elif("float "+variable[i] in coutputcode):
                    linecode=linecode.replace('''",'''+variable[i],"%f")
                elif("char "+variable[i]+"[100]" in coutputcode):
                    linecode=linecode.replace('''",'''+variable[i],"%s")
                    
                #Replacing bracket with ",
                linecode=linecode.replace(")",'''",''')
                
            #Appending variables in the printf
            for i in range(0,len(variable)):
                if(i!=len(variable)-1):
                    linecode=linecode+variable[i]+","
                else:
                    linecode=linecode+variable[i]+")"
                    
            #Appending to output list
            coutputcode.append(linecode)
            variable.clear()
        
        #If there are just variables and no print Statements
        elif('''"''' not in linecode):
            linecode=linecode.replace("print(",'''printf("''')
            variablecount=linecode.count(",")
            variablecount+=1
            
            #Storing Variables 
            place=linecode.split('''("''')
            variable.append(place[1])
            
            #For Single Varaibles
            if(variablecount==1):
                for i in range(0,variablecount):
                    
                    #Checking for brackets 
                    if(")" in variable[i]):
                        variable[i]=variable[i].replace(")","")
                    
                    #Checking for data types and Converting it 
                    if("int "+variable[i] in coutputcode):
                        linecode=linecode.replace(variable[i],"%d")
                    elif("float "+variable[i] in coutputcode):
                        linecode=linecode.replace('''",'''+variable[i],"%f")
                    elif("char "+variable[i]+"[100]" in coutputcode):
                        linecode=linecode.replace('''",'''+variable[i],"%s")
                        
                #Beating into shape
                linecode=linecode.replace(")",'''",''')
                linecode=linecode.replace(";","")
                linecode=linecode+variable[i]+")"
                
                #Appending to the output list
                coutputcode.append(linecode)
                variable.clear()
            
            #For multi variables
            else:
                lineduplicate=linecode 
                place=lineduplicate.split(",")
                no_of_variables=len(place)
                
                for i in place[1:]:
                    instantvalues=i.split(",")
                    variable.append(instantvalues[0])
                
                
              
        elif(linecode.startswith("#")):
            commentsfunction(linecode)
    
    
    #Function to Convert Input Statements
    def inputfunctions(linecode):
        if ("input()" not in linecode):
            pass
        else:
            thesplit = linecode.split('=')
    
            # Converting Integer inputs
            if ("int" in linecode):
                linecode = str(linecode)
                linecode = linecode.replace(thesplit[0] + "=int(input())", '''scanf("%d",&''' + thesplit[0] + ")")
                declaration = "int " + thesplit[0]
                coutputcode.append(declaration)
                coutputcode.append(linecode)
    
            # Converting float inputs
            elif ("float" in linecode):
                linecode = str(linecode)
                linecode = linecode.replace(thesplit[0] + "=float(input())", '''scanf("%f",&''' + thesplit[0] + ")")
                declaration = "float " + thesplit[0]
                coutputcode.append(declaration)
                coutputcode.append(linecode)
    
            # Converting Strings input
            else:
                linecode = str(linecode)
                linecode = linecode.replace(thesplit[0] + "=input()", '''scanf("%s",''' + thesplit[0] + ")")
                declaration = "char " + thesplit[0] + "[100]"
                coutputcode.append(declaration)
                coutputcode.append(linecode)
    
    #Converting Comment lines
    def commentsfunction(linecode):
        linecode=str(linecode)
        linecode=linecode.replace("#","//")
        coutputcode.append(linecode)
    
    #Declaring expressions variables
    def expressionsfunction(linecode):
        linecode=str(linecode)
        expressionsplit=linecode.split("=")
        if(expressionsplit[0].count(',')==0):
            if("." not in expressionsplit[1] and '''"''' not in expressionsplit[1]):
                declaration="int "+expressionsplit[0]
                coutputcode.append(declaration)
                coutputcode.append(linecode)
            elif("." in expressionsplit[1] and '''"''' not in expressionsplit[1]):
                declaration="float "+expressionsplit[0]
                coutputcode.append(declaration)
                coutputcode.append(linecode)
            elif('''"''' in expressionsplit[1]):
                declaration="char "+expressionsplit[0]+"[100]"
                linecode=expressionsplit[0]+"[100]="+expressionsplit[1]
                coutputcode.append(declaration)
                coutputcode.append(linecode)
    
    
    # Getting Multi-line inputs
    pyinputcode = []
    coutputcode=['#include<stdio.h>','#include<conio.h>','#include<stdlib.h>','void main()','{']
    pyinputcode=theprg.split()
        
    #Compares each line in the input
    for linecode in pyinputcode:
        #Converts print statement
        if("print" in linecode):
            printfunctions(linecode)
    
        #For input statement
        elif("input" in linecode):
            inputfunctions(linecode)
    
        #For Comment lines
        elif(linecode.startswith('#')):
            commentsfunction(linecode)
    
        #For others
        else:
            if("=" in linecode):
                expressionsfunction(linecode)
    
    #Appending the last Closing Curly Brace for main() function
    coutputcode.append('}')
    final=' '.join(map(str, coutputcode))
    print(theprg,file=sys.stderr)
    return jsonify(data=final)