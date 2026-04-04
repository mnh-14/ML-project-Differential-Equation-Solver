from execution_engine import ExecutionEngine as EE


ques = {
    "family": "Exact",
    "reasoning": "The equation 6 \\sin{\\left(\\frac{1}{x} \\right)} dx + dy = 0 satisfies the condition $\\frac{\\partial M}{\\partial y} = \\frac{\\partial N}{\\partial x}$, implying it is the total differential of a potential function $\\psi(x, y)$. We can find $\\psi$ by integrating M with respect to x and then adjusting for any remaining y-terms using N.",
    "equation": "6 \\sin{\\left(\\frac{1}{x} \\right)} dx + dy = 0",
    "steps": [
        {
            "action": "Identify",
            "op": "Find M(x, y) : ",
            "params": {
                "expression": "6 \\sin{\\left(\\frac{1}{x} \\right)}",
                "result_as": "M(x, y)"
            },
            "result": "M(x, y) = 6 \\sin{\\left(\\frac{1}{x} \\right)}"
        },
        {
            "action": "Identify",
            "op": "Find N(x, y) : ",
            "params": {
                "expression": "1",
                "result_as": "N(x, y)"
            },
            "result": "N(x, y) = 1"
        },
        {
            "action": "Integrate",
            "op": "Integrate",
            "params": {
                "expression": "M(x, y)",
                "wrt": "x",
                "result_as": "psi(x,y)"
            },
            "result": "6 x \\sin{\\left(\\frac{1}{x} \\right)} - 3 \\log{\\left(\\frac{1}{x^{2}} \\right)} + 6 \\log{\\left(\\frac{1}{x} \\right)} - 6 \\operatorname{Ci}{\\left(\\frac{1}{x} \\right)} + g(y)"
        },
        {
            "action": "Differentiate",
            "params": {
                "expression": "psi(x, y)",
                "wrt": "y",
                "result_as": "psi'(x,y)"
            },
            "op": "Differentiate",
            "result": "0 + g'(y)"
        },
        {
            "action": "Add",
            "params": {
                "operand1": "psi'(x,y)",
                "operand2": "g'(y)",
                "operand_type": [
                    "expression",
                    "var"
                ],
                "result_as": "psi'(x,y) + g'(y)"
            },
            "op": "Add g'(y)",
            "result": "6 x \\sin{\\left(\\frac{1}{x} \\right)} - 3 \\log{\\left(\\frac{1}{x^{2}} \\right)} + 6 \\log{\\left(\\frac{1}{x} \\right)} - 6 \\operatorname{Ci}{\\left(\\frac{1}{x} \\right)} + g'(y)"
        },
        {
            "action": "Solve",
            "params": {
                "equation": [
                    "psi'(x,y) + g'(y)",
                    "N(x, y)"
                ],
                "wrt": "g'(y)",
                "result_as": "g'(y)"
            },
            "op": "Solve",
            "result": "1"
        },
        {
            "action": "Integrate",
            "params": {
                "expression": "g'(y)",
                "wrt": "y",
                "result_as": "g(y)"
            },
            "op": "Integrate",
            "result": "y + C"
        },
        {
            "action": "Add",
            "params": {
                "operand1": "psi(x,y)",
                "operand2": "g(y)",
                "operand_type": [
                    "expression",
                    "expression"
                ],
                "result_as": "psi(x,y) + g(y)"
            },
            "op": "Form psi + g",
            "result": "6 x \\sin{\\left(\\frac{1}{x} \\right)} - 3 \\log{\\left(\\frac{1}{x^{2}} \\right)} + 6 \\log{\\left(\\frac{1}{x} \\right)} - 6 \\operatorname{Ci}{\\left(\\frac{1}{x} \\right)} + y = C_1"
        },
        {
            "action": "Solve",
            "params": {
                "equation": [
                    "psi(x,y) + g(y)",
                    "C_1"
                ],
                "wrt": "y",
                "result_as": "solution"
            },
            "op": "Solve for y"
        }
    ],
    "solution": "y(x) = 6 x \\sin{\\left(\\frac{1}{x} \\right)} + y - 3 \\log{\\left(\\frac{1}{x^{2}} \\right)} + 6 \\log{\\left(\\frac{1}{x} \\right)} - 6 \\operatorname{Ci}{\\left(\\frac{1}{x} \\right)} = C_{1}"
}

ee = EE()

ee.prepare_execution(ques.get("equation"), ques.get("steps", []))
res = ee.execute()
print("Final result:", res)