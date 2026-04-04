import json
string = """
{
  "reasoning": "The equation is in the form 5\\sin x y + \\frac{dy}{dx} = 2 x^2. By multiplying the entire equation by an integrating factor, I(x) = e^{-5 \cos x}, the left side becomes the derivative of the product I(x)y, allowing us to solve for y through direct integration of both sides.",
  "equation_family": "First Order Linear",
  "steps": [
    {
      "action": "Identify",
      "params": {
        "expression": "5\\sin x",
        "result_as": "P(x)"
      }
    },
    {
      "action": "IF Calc",
      "params": {
        "expression": "P(x)",
        "result_as": "IF",
        "wrt": "x"
      }
    },
    {
      "action": "Multiply",
      "params": {
        "operand1": "right_expr",
        "operand2": "IF",
        "operand_type": [
          "expression",
          "expression"
        ],
        "result_as": "prepared right"
      }
    },
    {
      "action": "Multiply",
      "params": {
        "operand1": "IF",
        "operand2": "y",
        "operand_type": [
          "expression",
          "var"
        ],
        "result_as": "prepared left"
      }
    },
    {
      "action": "Integrate",
      "params": {
        "expression": "prepared right",
        "wrt": "x",
        "result_as": "integrated right"
      }
    },
    {
      "action": "Solve",
      "params": {
        "equation": [
          "prepared left",
          "integrated right"
        ],
        "wrt": "y",
        "result_as": "solution"
      }
    }
  ]
}
"""


print("Parsed JSON:")
json_str = string.replace('\\', '\\\\')
plan = json.loads(json_str)
print(json.dumps(plan, indent=2))