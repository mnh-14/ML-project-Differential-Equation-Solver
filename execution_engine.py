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
        self.expressions[C.EQ_LEFT] = sp_latex.parse_latex(lhs, symbol_map=self.VARS)
        self.expressions[C.EQ_RIGHT] = sp_latex.parse_latex(rhs, symbol_map=self.VARS)
        self.expressions[C.EQ_MAIN] = sp.Eq(self.expressions[C.EQ_LEFT], self.expressions[C.EQ_RIGHT])
    

    def _identify(self, params):
        self.expressions[params[C.RESULT_AS]] = sp_latex.parse_latex(params.get(C.EXPRESSION), symbol_map=self.VARS)
        # pass
    
    def _integrate(self, params : dict):
        exp_name = params.get(C.EXPRESSION)
        exp = self.expressions.get(exp_name, sp_latex.parse_latex(exp_name, symbol_map=self.VARS))
        self.expressions[params[C.RESULT_AS]] = sp.integrate(exp, self.VARS.get(params[C.WRT]))
        # pass

    def _differentiate(self, params : dict):
        exp_name = params.get(C.EXPRESSION)
        exp = self.expressions.get(exp_name, sp_latex.parse_latex(exp_name, symbol_map=self.VARS))
        self.expressions[params[C.RESULT_AS]] = sp.diff(exp, self.VARS.get(params[C.WRT]))
        # pass

    def _int_factor_calculate(self, params : dict):
        exp = self.expressions.get(params.get(C.EXPRESSION))
        wrt = self.VARS.get(params.get(C.WRT))
        self.expressions[params.get(C.RESULT_AS)] = sp.exp(sp.integrate(exp, wrt))
        #pass

    def _multiply(self, params : dict):
        op_1 = self.expressions.get(params.get(C.OPERAND1), sp_latex.parse_latex(params.get(C.OPERAND1), symbol_map=self.VARS))
        op_2 = None
        if params.get(C.OPERAND_TYPE)[1] == C.EXPRESSION:
            op_2 = self.expressions.get(params.get(C.OPERAND2), sp_latex.parse_latex(params.get(C.OPERAND2), symbol_map=self.VARS))
        else:
            op_2 = self.VARS.get(params.get(C.OPERAND2))

        self.expressions[params.get(C.RESULT_AS)] = sp.Mul(op_1, op_2)
        #pass

    def _add(self, params : dict):
        op_1 = self.expressions.get(params.get(C.OPERAND1), sp_latex.parse_latex(params.get(C.OPERAND1), symbol_map=self.VARS))
        op_2 = None
        if params.get(C.OPERAND_TYPE)[1] == C.EXPRESSION:
            op_2 = self.expressions.get(params.get(C.OPERAND2), sp_latex.parse_latex(params.get(C.OPERAND2), symbol_map=self.VARS))
        else:
            op_2 = self.VARS.get(params.get(C.OPERAND2))

        self.expressions[params.get(C.RESULT_AS)] = sp.Add(op_1, op_2)
        #pass

    def _solve(self, params : dict):
        eqn = self.expressions.get(params.get(C.EQUATION), sp_latex.parse_latex(params.get(C.EQUATION)))
        wrt = self.expressions.get(params.get(C.WRT), sp_latex.parse_latex(params.get(C.WRT)))
        self.expressions[C.RESULT_AS] = sp.solve(eqn, wrt)
        #pass



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
            elif action == C.ACT_INTEGRATE:
                pass





"""
Execute:
    for action in actions:
        expressions[specific_result_name_for_that_action] = action_map[action_name](params)
"""