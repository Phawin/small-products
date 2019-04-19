# Solution Generation 2!
# This version allow you to convert a multiple choice string to a number
#
# Usage: Change two following lines and run!

output = "TestText.txt"   # Your text file
programFile = "Printer.cpp"

templateFile = "Template.cpp"

def prepareLine(s):
    base = '\tprintf("<TEXT>\\n");\n'.replace("<TEXT>",s)
    return base

def convertAnswer(s):
    try:
        val = float(s)
        return s
    except:
        # Convert a letter choice to a number
        choiceSelected = s.title()[0]
        return str(ord(choiceSelected) - 64)
    
    




with open(output,"r") as f:
    s = f.read()

tokens = s.split("\n")

code = ""
for token in tokens:
    if token == "":
        continue
    code += prepareLine(convertAnswer(token))


with open(templateFile,"r") as f:
    finalData = f.read()

finalData = finalData.replace("/*Your Code Here*/",code)

with open(programFile,"w") as f:
    f.write(finalData)

print("Complete!")