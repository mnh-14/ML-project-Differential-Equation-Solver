import json
import sys
from tokenize import endpats
from constants import *


INITIALS = """ \\documentclass{article}
\\usepackage{graphicx} % Required for inserting images

\\title{ML dataset check}
\\author{MD. NAFIS HUSSAIN}
\\date{January 2026}

\\begin{document}

\\maketitle\n"""
ENDS = "\\end{document}"


def make_latex_file(filename: str, savefilename: str = None):
    strings = []
    with open(filename, 'r') as f:
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
    with open(savefilename, 'w') as f:
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