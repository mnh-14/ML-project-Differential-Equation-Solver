import json
import sys
from tokenize import endpats
from constants import *
import random


INITIALS = """\\documentclass{article}
\\usepackage{graphicx, amsmath} % Required for inserting images

\\title{ML dataset check}
\\author{MD. NAFIS HUSSAIN}
\\date{January 2026}

\\begin{document}

\\maketitle\n"""
ENDS = "\\end{document}"

def make_latex_file(filename: str, savefilename: str = None):
    strings = []
    with open(DATA_LOC + filename, 'r') as f:
        data = json.load(f)
        for item in data:
            strings.append("\\section*{Family: " + item[FAMILY] + "}\n")
            strings.append("\\textbf{Question:} $" + item[EQUATION] + "$\n\n")
            strings.append("\\textbf{Steps:}\n\\begin{enumerate}\n")
            for step in item[Q_STEPS]:
                strings.append("\\item " + step[STEP] + " :  $" + step[RESULT] + "$\n")
            strings.append("\\end{enumerate}\n")
            strings.append("\\textbf{Final Result:} $" + item[SOLUTION] + "$\n\n")

    savefilename = savefilename or filename.replace('.json', '.tex')
    with open(LATEX_LOC + savefilename, 'w') as f:
        f.write(INITIALS)
        f.writelines(strings)
        f.write(ENDS)



# Usage: python data_to_latex.py complex_ode_dataset.json
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python data_to_latex.py <input_json_file> [<output_tex_file>]")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        make_latex_file(input_file, output_file)



# import json
# import sys
# import re
# from constants import *

# def clean_latex_output(text: str) -> str:
#     if not isinstance(text, str): return ""

#     # 1. First, fix the 'textasciicircum' back into a real math caret
#     text = text.replace(r'\textasciicircum', '^')
    
#     # 2. Fix the "Inverse dx" hallucination: dy dx^{-1} -> \frac{dy}{dx}
#     # This regex catches both 'dy dx^{-1}' and 'dy dx^-1'
#     text = re.sub(r'dy\s*dx\^\{?-1\}?', r'\\frac{dy}{dx}', text)
    
#     # 3. Clean up the variable bracket hallucinations: {(x )} -> (x)
#     text = re.sub(r'\{\((.*?)\s*\)\}', r'(\1)', text)

#     # 4. Remove any accidental \mathtt or \text wrappers the model might have output
#     text = text.replace(r'\mathtt', '').replace(r'\text', '')
    
#     # 5. Final check for bracket balance
#     open_b = text.count('{')
#     close_b = text.count('}')
#     if open_b > close_b:
#         text += '}' * (open_b - close_b)
    
#     return text.strip()

# # Use raw strings (r"") to prevent Python from eating the backslashes
# INITIALS = r"""\documentclass{article}
# \usepackage[utf8]{inputenc}
# \usepackage{amsmath, amssymb}

# \title{ML Dataset Check}
# \author{MD. NAFIS HUSSAIN}
# \date{January 2026}

# \begin{document}
# \maketitle
# """

# ENDS = r"\end{document}"

# def make_latex_file(filename: str, savefilename: str = None):
#     strings = []
#     with open(DATA_LOC + filename, 'r') as f:
#         data = json.load(f)
        
#         for item in data:
#             # We use .replace() for literal curly brackets to avoid f-string errors
#             family_head = "\\section*{Family: " + item.get(FAMILY, "Unknown") + "}\n"
#             strings.append(family_head)
            
#             eq = clean_latex_output(item.get(EQUATION, ""))
#             strings.append("\\textbf{Question:} \\begin{equation*}\n" + eq + "\n\\end{equation*}\n\n")
            
#             strings.append("\\textbf{Steps:}\n\\begin{enumerate}\n")
#             for step in item.get(Q_STEPS, []):
#                 s_res = clean_latex_output(step.get(RESULT, ""))
#                 # Escaping the string for the item line
#                 strings.append("  \\item " + step.get(STEP, "Step") + " : $" + s_res + "$\n")
#             strings.append("\\end{enumerate}\n")
            
#             sol = clean_latex_output(item.get(SOLUTION, ""))
#             strings.append("\\textbf{Final Result:} \[ " + sol + " \]\n\n")
#             strings.append("\\hrulefill\n\n")

#     savefilename = savefilename or filename.replace('.json', '.tex')
#     with open(LATEX_LOC + savefilename, 'w', encoding='utf-8') as f:
#         f.write(INITIALS)
#         f.writelines(strings)
#         f.write(ENDS)

# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("Usage: python data_to_latex.py <input_json_file> [<output_tex_file>]")
#     else:
#         input_file = sys.argv[1]
#         output_file = sys.argv[2] if len(sys.argv) > 2 else None
#         make_latex_file(input_file, output_file)