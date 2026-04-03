from selectors import SelectorKey

import sympy as sp
import sympy.parsing.latex as sp_latex
from previous_resources.Previous_Codes import constants as C


# not a model executioner, rather something that uses sympy to execute the steps and get the final result, which can be used for evaluation
class ExecutionEngine:
    VARS = {
        'x': sp.Symbol('x'),
        'y': sp.Symbol('y'),
        'dx': sp.Symbol('dx', immutable=True),
        'dy': sp.Symbol('dy', immutable=True),
        'C_1': sp.Symbol('C_1'),
        "g'(y)": sp.Symbol("g'(y)"),
    }
    def __init__(self):
        self.latex_eq: str = None
        self.steps: list = None
        self.expressions: dict = {}
    
    def prepare_execution(self, latex_eq, steps):
        self.latex_eq = latex_eq
        self.steps = steps
        self.expressions = {}
        self._parse_equation()
        self.expressions["C_1"] = sp.Symbol("C_1")
    
    def _parse_equation(self):
        if self.latex_eq is None:
            raise ValueError("No equation provided for execution.")
        if '=' not in self.latex_eq:
            raise ValueError("Invalid equation format. Expected an equation with '='.")

        lhs, rhs = self.latex_eq.split('=', 1)
        self.expressions[C.EQ_LEFT] = sp_latex.parse_latex(lhs, local_dict=self.VARS)
        self.expressions[C.EQ_RIGHT] = sp_latex.parse_latex(rhs, local_dict=self.VARS)
        self.expressions[C.EQ_MAIN] = sp.Eq(self.expressions[C.EQ_LEFT], self.expressions[C.EQ_RIGHT])
    

    def _separate_variables(self, params):
        pass
    
    def _integrate(self, params):
        pass

    def _differentiate(self, params):
        pass



    def execute(self):
        for step in self.steps:
            action = step.get(C.ACTION)
            params = step.get(C.PARAMS, {})
            if action == "Separate Variables":
                left_expr = params.get(C.LEFT)
                right_expr = params.get(C.RIGHT)
                if left_expr and right_expr:
                    self.expressions[C.EXP_LEFT] = sp.simplify(1/left_expr * self.expressions[C.EXP_LEFT])
                    self.expressions[C.EXP_RIGHT] = sp.simplify(right_expr * self.expressions[C.EXP_RIGHT])
                    self.expressions[C.EXP_MAIN] = sp.Eq(self.expressions[C.EXP_LEFT], self.expressions[C.EXP_RIGHT])
                else:
                    raise ValueError("Missing parameters for Separate Variables action.")
            # Implement other actions as needed