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
    theprg=prg.strip()
    print(theprg.split('$'))
    print('#',theprg)
    global coutputcode
    global bracescount
    global pre_space_count
    

    operators = ["+","-","*","/","%"]
    forfinal=[]
    # Function to Convert Print Statements
    def printstatements(linecode):
        linecode = linecode.strip()
        no_quotes = linecode.count('''"''')
        statements = []
        linecode1 = '''printf("'''

        #If Output statements in the print statement
        if(no_quotes != 0):
            while('''"''' in linecode):
                quotes_place = linecode.find('''"''')
                quotes_place2 = linecode[quotes_place + 1:].find('''"''') + 1 +quotes_place
                statements.append(linecode[quotes_place + 1:quotes_place2])
                linecode = linecode[:quotes_place] + linecode[quotes_place2 + 1:]
            if(linecode.strip().startswith("print(")):
                linecode = linecode.replace("print(",'')
            else:
                linecode = linecode.replace("print (",'')
            linecode = linecode.replace(")",'')
            variable = linecode.split(",")
            ind = 0 
            for i in variable:
                if(i == ''):
                    linecode1 += statements[ind]
                    ind += 1 
                else:
                    if(i in intbox):
                        linecode1 += "%d "
                    elif(i in floatbox):
                        linecode1 += "%f "
                    elif(i+"[100]" in stringbox):
                        linecode1 += "%s "
                    elif('+' in i or '-' in i or '*' in i or '/' in i or '%' in i):
                        for j in operators:
                            if(j in i):
                                operator = j 
                        variables = i.split(operator)
                        
                        if(((variables in intbox) and (variables not in floatbox)) and ("." not in variables)):
                            linecode1 += "%d "
                        elif((variables in floatbox) or "." in variables):
                            linecode1 += "%f "
                        elif((variables+"[100]" in stringbox and variables not in floatbox and variables not in intbox) or '''"''' in i):
                            linecode1 += "%s "
                        else:
                            linecode1 += "%d "
                
            linecode1 += '''"'''
            for i in variable:
                if(i == ''):
                    variable.remove(i)
            if(len(variable) != 0):
                linecode1 += ","
                for i in variable:
                    linecode1 += i 
                    if(variable.index(i) != len(variable) - 1):
                        linecode1 += ","
        
        #If only variables
        else:
            if(linecode.strip().startswith("print(")):
                linecode = linecode.replace("print(",'')
            else:
                linecode = linecode.replace("print (",'')
            linecode = linecode.replace(")",'')
            variable = linecode.split(",")
            for i in variable:
                if(i in intbox):
                    linecode1 += "%d "
                elif(i in floatbox):
                    linecode1 += "%f "
                elif(i+"[100]" in stringbox):
                    linecode1 += "%s "
                elif('+' in i or '-' in i or '*' in i or '/' in i or '%' in i):
                    variables1 = []
                    variables1.append(i)
                    for j in operators:
                        for k in range(len(variables1)):
                            if(j in variables1[k]):
                                variables2 = variables1[k].split(j)
                                variables1.remove(variables1[k])
                                for m in variables2:
                                    variables1.append(m)
                    
                    if(all(var.strip() not in floatbox for var in variables1) and all('.' not in var for var in variables1) and all('''"''' not in var for var in variables1)):
                        linecode1 += "%d "
                    elif(all(var.strip() not in intbox for var in variables1) and all('''"''' not in var for var in variables1)):
                        linecode1 += "%f "
                    elif((all(var.strip() not in intbox for var in variables1) and all(var.strip() not in floatbox for var in variables1))):
                        linecode1 += "%s "
                    else:
                        linecode1 += "%d "

            linecode1 += '''",'''
            for i in variable:
                linecode1 += i 
                if(variable.index(i) != len(variable) - 1):
                    linecode1 += ","
                    
        linecode1 += ")"
        coutputcode.append(linecode1)        

    # Function to Convert Input Statements
    def inputfunctions(linecode):
        thesplit = linecode.split('=')
        variables = thesplit[0].split(',')
        prompts = thesplit[1].split("),") 
        
        for i in range(len(variables)):
            declaration = variables[i].strip()
            
            #For input statements with prompts
            if ('''input("''' in prompts[i]):
                linecode1 = '''printf('''
                quotesplace = prompts[i].index('''"''')
                try:
                    bracketplace = prompts[i].index(")")
                except:
                    bracketplace = len(prompts[i])
                linecode1 += prompts[i][quotesplace:bracketplace] + ")"
                coutputcode.append(linecode1)
                # Converting Integer inputs
                if (prompts[i].strip().startswith("int")):
                    linecode = '''scanf("%d",&''' + variables[i].strip() + ")"
                    intbox.append(declaration)
        
                # Converting float inputs
                elif (prompts[i].strip().startswith("float")):
                    linecode = '''scanf("%f",&''' + variables[i].strip() + ")"
                    floatbox.append(declaration)
        
                # Converting Strings input
                else:
                    linecode = '''scanf("%s",''' + variables[i].strip() + ")"
                    declaration += "[100]"
                    stringbox.append(declaration)
            
            #Input Statements without Prompts
            else:
                # Converting Integer inputs
                if (prompts[i].strip().startswith("int")):
                    linecode = '''scanf("%d",&''' + variables[i].strip() + ")"
                    intbox.append(declaration)
                
                # Converting float inputs
                elif (prompts[i].strip().startswith("float")):
                    linecode = '''scanf("%f",&''' + variables[i] + ")"
                    floatbox.append(declaration)
        
                # Converting Strings input
                else:
                    linecode = '''scanf("%s",''' + variables[i] + ")"
                    declaration += "[100]"
                    stringbox.append(declaration)
            coutputcode.append(linecode)

    # Converting Comment lines
    def commentsfunction(linecode):
        linecode = str(linecode)
        linecode = linecode.replace("#", "//")
        coutputcode.append(linecode)

    # Declaring expressions variables
    def expressionsfunction(linecode):
        expressionsplit = linecode.split("=")
        variables = expressionsplit[0].split(",")
        declarations = expressionsplit[1].split(",")
        print("exp",variables,declarations)
        
        for i in range(len(variables)):
            declaration = variables[i].strip()
            if('+' not in declarations[i] and '-' not in declarations[i] and '*' not in declarations[i] and '/' not in declarations[i] and '%' not in declarations[i]):
               # print(variables1,"in exp")
                if ("." not in declarations[i] and '''"''' not in declarations[i]):
                    if(variables[i].strip() not in intbox):
                        print("int",variables[i])
                        intbox.append(declaration)
                elif ("." in declarations[i] and '''"''' not in declarations[i]):
                    if(variables[i].strip() not in floatbox):
                        floatbox.append(declaration)
                        if(declaration in intbox):
                            intbox.remove(declaration)
                elif ('''"''' in declarations[i]):
                    if(variables[i]+"[100]".strip() not in stringbox):
                        declaration += "[100]"
                        stringbox.append(declaration)
                    linecode = variables[i].strip() + "[100] = " + declarations[i].strip()
            
            else:
                variables1 = []
                variables1.append(declarations[i])
                
                for j in operators:
                    for k in range(len(variables1)):
                        if(j in variables1[k]):
                            variables2 = variables1[k].split(j)
                            variables1.remove(variables1[k])
                            for m in variables2:
                                variables1.append(m)
                if(all(var.strip() not in floatbox for var in variables1) and all('.' not in var for var in variables1) and all('''"''' not in var for var in variables1)):
                    if(variables[i].strip() not in intbox):
                        intbox.append(declaration)
                elif(all(var.strip() not in intbox for var in variables1) and all('''"''' not in var for var in variables1)):
                    if(variables[i].strip() not in floatbox):
                        floatbox.append(declaration)
                        if(declaration in intbox):
                            intbox.remove(declaration)
                elif((all(var.strip() not in intbox for var in variables1) and all(var.strip() not in floatbox for var in variables1))):
                    if(variables[i]+"[100]".strip() not in stringbox):
                        declaration += "[100]"
                        stringbox.append(declaration)
                    linecode = variables[i].strip() + "[100] = " + declarations[i].strip()
        coutputcode.append(linecode)


    #Control Statements
    def controlstatements(linecode):
        linecode = linecode.strip()
        linecode = linecode[:len(linecode) - 1]

        if('''"''' not in linecode):
            if("and" in linecode):
                linecode = linecode.replace("and","&&")
            elif("or" in linecode):
                linecode = linecode.replace("||","or")
            elif("not" in linecode):
                linecode.replace("!","not")
        #For if statements without parenthesis
        if(not linecode.strip().startswith("if(") and not linecode.strip().startswith("if (") and not linecode.strip().startswith("for ") and not linecode.strip().startswith("elif") and not linecode.strip().startswith("while")):
            try:
                space_index = linecode.strip().index(' ')
                linecode1 = "if("
            
                linecode = linecode1 + linecode[space_index + 1:]
            except:
                linecode = linecode
            
            linecode += ')'
        
        if(linecode.strip().startswith("else")):
            linecode = linecode.replace(')','')

        elif(linecode.strip().startswith("elif(") or linecode.strip().startswith("elif (")):
            bracket = linecode.find("(")
            linecode = "else if" + linecode[bracket:]

        elif(linecode.strip().startswith("for ")):
            fors = linecode.split()
            variable = str(fors[1])

            #If range functions is used
            if("range(" in linecode or "range (" in linecode):
                intbox.append(variable)
                bracket = linecode.find("(")
                bracketc = linecode.find(")")
                range1 = linecode[bracket + 1:bracketc].split(',')
                initialize = str(range1[0])
                endval = str(range1[1])
                if(len(range1) == 2):
                    stepval = '1'
                else:
                    stepval = str(range1[2])
                    if('-' in stepval):
                        minus = stepval.find("-")
                        stepval = stepval[minus + 1:]
                
                linecode = "for(" + variable +" = " + initialize + "; " + variable 
                if(initialize < endval):
                    linecode += " < " + endval + "; " + variable + " += " + stepval + ")"

                else:
                    linecode += " > " + endval + "; " + variable + " -= " + stepval + ")"
        
                
        coutputcode.append(linecode)
        
    intbox = []
    floatbox = []
    stringbox = []
    pyinputcode =theprg.split('$')
    pre_space_count = 0
    bracescount = 1
    coutputcode = ['#include<stdio.h>', '#include<conio.h>', '#include<stdlib.h>', 'void main()', '{']


    # Getting Multi-line inputs
   
    #Takes each line in the Intput
    for linecode in pyinputcode:
        print(linecode)
        #Automatic Curly Braces Function
        curr_space_count = 0
        for spaces in linecode:
            if(spaces != ' '):
                break
            elif(spaces == ' ' or spaces == '\t'):
                curr_space_count +=1
        if(pre_space_count > curr_space_count):
            print(".")
            coutputcode.append('}')
            bracescount += 1
        elif(pre_space_count < curr_space_count):
            coutputcode.append('{')
            bracescount += 1
        pre_space_count = curr_space_count

        # Converts print statement
        if (linecode.strip().startswith("print(") or linecode.strip().startswith("print (")):
            printstatements(linecode)

        # For input statement
        elif ("input" in linecode):
            sides = linecode.split("=")
            sides[1] = sides[1].strip()
            if(sides[1].strip().startswith('''"''')):
                expressionsfunction(linecode)
            else:
                inputfunctions(linecode)

        # For Comment lines
        elif (linecode.strip().startswith('#')):
            commentsfunction(linecode)
        
        elif(linecode.strip().startswith("if(") or linecode.strip().startswith("if (") or linecode.strip().startswith("if ") or linecode.strip().startswith("elif(") or linecode.strip().startswith("elif (") or linecode.strip().startswith("elif ") or linecode.strip().startswith("while(") or linecode.strip().startswith("while (") or linecode.strip().startswith("while ") or linecode.strip().startswith("for ")):
            controlstatements(linecode)
        
        elif((linecode.strip().startswith("else") or linecode.strip().startswith("else ")) and "=" not in linecode):
            controlstatements(linecode)

        # For others
        else:
            equals = linecode.find("=")
            if ("=" in linecode and linecode[equals - 1] not in operators):
                print("$")
                expressionsfunction(linecode)
            else:
                coutputcode.append(linecode)

    #Function for Initial Variable Declaration
    mainposition = coutputcode.index("void main()")

    if(len(intbox) != 0):
        coutputcode.insert(mainposition + 2,"int ")
        for i in range(0,len(intbox)):
            coutputcode[mainposition + 2] += intbox[i]
            if(i != len(intbox)-1):
                coutputcode[mainposition + 2] += ","

    if(len(floatbox) != 0):
        if(len(intbox) != 0):
            j = 3
        else:
            j = 2
        coutputcode.insert(mainposition + j,"float ")
        for i in range(0,len(floatbox)):
            coutputcode[mainposition + j] += floatbox[i]
            if(i != len(floatbox)-1):
                coutputcode[mainposition + j] += ","

    if(len(stringbox) != 0):
        if(len(intbox) != 0 and len(floatbox) != 0):
            j = 4
        elif(len(intbox) !=0 and len(floatbox) == 0):
            j = 3
        elif(len(intbox) == 0 and len(floatbox) != 0):
            j = 3
        else:
            j = 2
        coutputcode.insert(mainposition + j,"char ")
        for i in range(0,len(stringbox)):
            coutputcode[mainposition + j] += stringbox[i]
            if(i != len(stringbox)-1):
                coutputcode[mainposition + j] += ","

    # Appending the last Closing Curly Brace for main() function
    coutputcode.append('}')
    bracescount += 1
    if(bracescount % 2 == 1):
        coutputcode.append('}')
    
    print("***",coutputcode)
    # Printing the Output
    for linecode1 in coutputcode:
        if (linecode1.startswith('#include') or linecode1.startswith('void') or linecode1.startswith('{') or linecode1.startswith('}') or linecode1.strip().startswith("for(")):
            forfinal.append(linecode1)
        elif (linecode1.startswith('//') or linecode1.strip().startswith("if(") or linecode1.strip().startswith("if (") or linecode1.strip().startswith("else") or linecode1.strip().startswith("while")):
            forfinal.append(linecode1)
        else:
            forfinal.append(linecode1 + ";")

    final=' '.join(map(str, forfinal))
    print("*",theprg,file=sys.stderr)
    return jsonify(result={"status":200},data=final)

