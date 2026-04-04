from ast import parse
from selectors import SelectorKey

import sympy as sp
import sympy.parsing.latex as sp_latex
# from sympy.parsing.latex import parse_latex
from previous_resources.Previous_Codes import constants as C


def latex_parser(latex_str):
    try:
        latex_str = latex_str.replace("\\\\\\\\", "\\")
        print(f"Parsing LaTeX: {latex_str}")
        parsed = sp_latex.parse_latex(latex_str)
        # var_map = {s.name: s for s in parsed.atoms(sp.Symbol)}
        var_map = {s.name: s for s in parsed.free_symbols}
        return sp_latex.parse_latex(latex_str), var_map
    except Exception as e:
        print(f"Error parsing LaTeX: {latex_str}")
        raise e


# not a model executioner, rather something that uses sympy to execute the steps and get the final result, which can be used for evaluation
class ExecutionEngine:
    VARS = {
        'x': sp.Symbol('x', real=True),
        'y': sp.Symbol('y', real=True),
        'dx': sp.Symbol('dx', immutable=True),
        'dy': sp.Symbol('dy', immutable=True),
        'C_1': sp.Symbol('C_1'),
        "g'(y)": sp.Symbol("g'(y)"),
    }
    def __init__(self):
        self.latex_eq: str = None
        self.steps: list = None
        self.expressions: dict = {}
        
        self.functions = {
            C.ACT_ADD.lower() : self._add,
            C.ACT_DIFFERENTIATE.lower() : self._differentiate,
            C.ACT_IDENTIFY.lower() : self._identify,
            C.ACT_IF_CALC.lower() : self._int_factor_calculate,
            C.ACT_INTEGRATE.lower() : self._integrate,
            C.ACT_MULTIPLY.lower() : self._multiply,
            C.ACT_SOLVE.lower() : self._solve
        }
    

    def _custom_parse_latex(self, latex_str):
        try:
            # print(f"Custom Parsing LaTeX (before cleanup): {latex_str}")
            latex_str = latex_str.replace("\\\\", "\\")
            # print(f"Custom Parsing LaTeX (after cleanup): {latex_str}")
            # latex_str = latex_str.encode('utf-8').decode('unicode_escape')
            parsed = sp_latex.parse_latex(latex_str)
            final_expr = parsed.subs({s: self.VARS[s.name] for s in parsed.free_symbols if s.name in self.VARS})
            return final_expr
        except Exception as e:
            print(f"Error parsing LaTeX: {latex_str}")
            raise e
    
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
        # self.expressions[C.EQ_LEFT] = sp_latex.parse_latex(lhs, symbol_map=self.VARS)
        # self.expressions[C.EQ_RIGHT] = sp_latex.parse_latex(rhs, symbol_map=self.VARS)
        # self.expressions[C.EQ_LEFT] = sp_latex.parse_latex(lhs)
        # self.expressions[C.EQ_RIGHT] = sp_latex.parse_latex(rhs)
        self.expressions[C.EQ_LEFT] = self._custom_parse_latex(lhs)
        self.expressions[C.EQ_RIGHT] = self._custom_parse_latex(rhs)
        self.expressions[C.EQ_MAIN] = sp.Eq(self.expressions[C.EQ_LEFT], self.expressions[C.EQ_RIGHT])
    

    def _identify(self, params):
        result_key = params.get(C.RESULT_AS)
        self.expressions[result_key] = self._custom_parse_latex(params.get(C.EXPRESSION))
        print(f"[Identify] Final result ({result_key}): {self.expressions[result_key]}")
        # pass
    
    def _integrate(self, params : dict):
        exp_name = params.get(C.EXPRESSION)
        exp = self.expressions.get(exp_name, self._custom_parse_latex(exp_name))
        result_key = params.get(C.RESULT_AS)
        self.expressions[result_key] = sp.integrate(exp, self.VARS.get(params[C.WRT]))
        print(f"[Integrate] Final result ({result_key}): {self.expressions[result_key]}")
        # pass

    def _differentiate(self, params : dict):
        exp_name = params.get(C.EXPRESSION)
        exp = self.expressions.get(exp_name, self._custom_parse_latex(exp_name))
        result_key = params.get(C.RESULT_AS)
        self.expressions[result_key] = sp.diff(exp, self.VARS.get(params[C.WRT]))
        print(f"[Differentiate] Final result ({result_key}): {self.expressions[result_key]}")
        # pass

    def _int_factor_calculate(self, params : dict):
        exp = self.expressions.get(params.get(C.EXPRESSION))
        wrt = self.VARS.get(params.get(C.WRT))
        result_key = params.get(C.RESULT_AS)
        self.expressions[result_key] = sp.exp(sp.integrate(exp, wrt))
        print(f"[IF Calc] Final result ({result_key}): {self.expressions[result_key]}")
        #pass

    def _multiply(self, params : dict):
        op_1 = self.expressions.get(params.get(C.OPERAND1), self._custom_parse_latex(params.get(C.OPERAND1)))
        op_2 = None
        if params.get(C.OPERAND_TYPE)[1] == C.EXPRESSION:
            op_2 = self.expressions.get(params.get(C.OPERAND2), self._custom_parse_latex(params.get(C.OPERAND2)))
        else:
            op_2 = self.VARS.get(params.get(C.OPERAND2))

        result_key = params.get(C.RESULT_AS)
        self.expressions[result_key] = sp.Mul(op_1, op_2)
        print(f"[Multiply] Final result ({result_key}): {self.expressions[result_key]}")
        #pass

    def _add(self, params : dict):
        op_1 = self.expressions.get(params.get(C.OPERAND1), self._custom_parse_latex(params.get(C.OPERAND1)))
        op_2 = None
        if params.get(C.OPERAND_TYPE)[1] == C.EXPRESSION:
            op_2 = self.expressions.get(params.get(C.OPERAND2), self._custom_parse_latex(params.get(C.OPERAND2)))
        else:
            op_2 = self.VARS.get(params.get(C.OPERAND2))

        result_key = params.get(C.RESULT_AS)
        self.expressions[result_key] = sp.Add(op_1, op_2)
        print(f"[Add] Final result ({result_key}): {self.expressions[result_key]}")
        #pass

    def _solve(self, params : dict):
        eqn_left = self.expressions.get(params.get(C.EQUATION)[0], self._custom_parse_latex(params.get(C.EQUATION)[0]))
        eqn_right = self.expressions.get(params.get(C.EQUATION)[1], self._custom_parse_latex(params.get(C.EQUATION)[1]))
        eqn = sp.Eq(eqn_left, eqn_right)
        wrt = self.VARS.get(params.get(C.WRT), self._custom_parse_latex(params.get(C.WRT)))
        # self.expressions[params.get(C.RESULT_AS)] = sp.solve(eqn, wrt)
        print(f"[Solve] Solving equation: {eqn} for variable: {wrt}")
        solutions = self.expressions[params.get(C.RESULT_AS)] = sp.solve(eqn, wrt)
        print(f"[Solve] Raw solutions: {solutions}")
        allowed_types = (sp.Symbol, sp.Rational, sp.Pow, sp.Add, sp.Mul, sp.sin, sp.cos, sp.tan, sp.log)
    
        clean_solutions = []
        
        for sol in solutions:
            # Check if every part of the solution is in our allowed list
            # .atoms() breaks the expression into its core building blocks
            is_transcendental = any(not isinstance(atom, allowed_types) for atom in sol.atoms())
            
            if not is_transcendental:
                clean_solutions.append(sol)
                
        if clean_solutions:
            self.expressions[params.get(C.RESULT_AS)] = clean_solutions
        else:
            # Return the original equation if no clean solution exists
            self.expressions[params.get(C.RESULT_AS)] = eqn
        if len(self.expressions[params.get(C.RESULT_AS)]) == 1:
            self.expressions[params.get(C.RESULT_AS)] = self.expressions[params.get(C.RESULT_AS)][0]
        print(f"[Solve] Final result ({params.get(C.RESULT_AS)}): {self.expressions[params.get(C.RESULT_AS)]}")
        #pass


    def execute(self):
        for step in self.steps:
            action = step.get(C.ACTION)
            params = step.get(C.PARAMS, {})
            # print(f"Executing action: ||{action}||")
            self.functions.get(action.lower())(params)
        return self.expressions.get(C.SOLUTION, None)





"""
Execute:
    for action in actions:
        expressions[specific_result_name_for_that_action] = action_map[action_name](params)
"""