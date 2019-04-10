# Solution Generation!
#
# Usage: Change two following lines and run!

output = "TextFile.txt"   # Your text file
programFile = "Printer.cpp"

templateFile = "Template.cpp"

def prepareLine(s):
    base = '\tprintf("<TEXT>\\n");\n'.replace("<TEXT>",s)
    return base



with open(output,"r") as f:
    s = f.read()

tokens = s.split()

code = ""
for token in tokens:
    code += prepareLine(token)


with open(templateFile,"r") as f:
    finalData = f.read()

finalData = finalData.replace("/*Your Code Here*/",code)

with open(programFile,"w") as f:
    f.write(finalData)

print("Complete!")