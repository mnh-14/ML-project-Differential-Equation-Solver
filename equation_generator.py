import json
import sympy as sp
import random
import argparse
import sys
from previous_resources.Previous_Codes import constants as C
from sympy import Piecewise
from sympy.diffgeom import Differential

# Define symbols
x = sp.Symbol('x')
# y = sp.Function('y')(x)
y = sp.Symbol('y')
dx = sp.Symbol('dx', commutative=False)
dy = sp.Symbol('dy', commutative=False)
dy_dx = sp.Symbol('\\frac{dy}{dx}', commutative=False)
# dx = Differential(x)
# dy = Differential(y)
C1 = sp.Symbol('C1')


# Generate expressions :
def get_complex_expr(var, complexity=2):
    """Generates varied mathematical expressions to avoid duplicates."""
    basics = [var, 1/var, var**2, sp.sin(var), sp.cos(var), sp.tan(var), sp.exp(var), sp.log(var)]
    expr = random.choice(basics) * random.randint(1, 10)
    for _ in range(complexity - 1):
        other = random.choice(basics) + random.randint(1, 6)
        op = random.choice(['add', 'mul'])
        expr = expr + other if op == 'add' else expr * other
    return sp.simplify(expr)

def get_complex_expr_doubled(var1, var2, complexity=2):
    """Generates varied mathematical expressions to avoid duplicates."""
    vars_basic= [var1, var2, 1/var1, 1/var2]
    vars_extended = vars_basic + [var1**2, var2**2, var1*var2]
    basics_1 = [sp.sin(random.choice(vars_basic)), sp.cos(random.choice(vars_basic)), sp.exp(random.choice(vars_basic))]
    basics = basics_1 + [random.choice(vars_extended)]
    expr = random.choice(basics) * random.randint(1, 10)
    for _ in range(complexity - 1):
        other = random.choice(basics) + random.randint(1, 6)
        op = random.choice(['add', 'mul'])
        expr = expr + other if op == 'add' else expr * other
    return sp.simplify(expr)


# Generate ODE of different families : 
def generate_separable():
    """Expert for Separable ODEs: dy/dx = f(x)g(y)"""
    complexity = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
    f_x = get_complex_expr(x, complexity)
    # g_y_sym = random.choice([y, y**2, sp.exp(y), 1]) + random.randint(-5, 5) * random.choice([y, y**2, sp.exp(y), 1])
    g_y_sym = random.choice([y, y**2, sp.exp(y), random.randint(-5, 5), random.randint(-5, 5) + random.randint(-5, 5) * y, random.randint(-5, 5) + random.randint(-5, 5) * y**2]) 
    ode = sp.Eq(dy_dx, f_x * g_y_sym)
    lhs = sp.integrate(1/g_y_sym, y)
    rhs = sp.integrate(f_x, x)
    eqn = sp.Eq(lhs, rhs + C1)

    reasoning = "The equation contains a product of a function of x (" + sp.latex(f_x) + ") and a function of y (" +  sp.latex(g_y_sym) + "). By dividing both sides by " + sp.latex(g_y_sym) + " and multiplying by dx, we can isolate all y terms on the left and all x terms on the right."

    if lhs.has(sp.Integral) or rhs.has(sp.Integral):
        return None, None, None, None, None 
    
    steps = [
        # {C.ACTION: C.ACT_SEPARATE_VARIABLES, C.OP: "Separate Variables", C.PARAMS : {C.LEFT : sp.latex(g_y_sym), C.RIGHT : sp.latex(f_x)}, C.RESULT: f"\\frac{{1}}{{{sp.latex(g_y_sym)}}} dy = \\left({sp.latex(f_x)}\\right) dx"},
        {C.ACTION: C.ACT_IDENTIFY, C.OP: "Separate Variables", C.PARAMS : {C.EXPRESSION: sp.latex(1/g_y_sym), C.RESULT_AS: "left part"}, C.RESULT: f"\\frac{{1}}{{{sp.latex(g_y_sym)}}} dy = \\left({sp.latex(f_x)}\\right) dx"},
        {C.ACTION: C.ACT_IDENTIFY, C.OP: "Separate Variables", C.PARAMS : {C.EXPRESSION: sp.latex(f_x), C.RESULT_AS: "right part"}, C.RESULT: f"\\frac{{1}}{{{sp.latex(g_y_sym)}}} dy = \\left({sp.latex(f_x)}\\right) dx"},
        {C.ACTION: C.ACT_INTEGRATE, C.OP: "Integrate Left Side", C.PARAMS : {C.EXPRESSION : 'left part', C.WRT : "y", C.RESULT_AS: "integrated left"}, C.RESULT: sp.latex(lhs)},
        {C.ACTION: C.ACT_INTEGRATE, C.OP: "Integrate Right Side", C.PARAMS : {C.EXPRESSION : "right part", C.WRT : "x", C.RESULT_AS: "integrated right"}, C.RESULT: f"{sp.latex(rhs)} + C_1"},
        {C.ACTION: C.ACT_SOLVE, C.OP: "Isolate y", C.PARAMS : {C.EQUATION : ("integrated left", "integrated right"), C.WRT: "y", C.RESULT_AS: C.SOLUTION}, C.RESULT: sp.latex(eqn)}
    ]
    soln = sp.solve(eqn, y)
    return sp.latex(ode), "Separable", reasoning, steps, [sp.latex(s) for s in soln]

def generate_linear():
    """Expert for First-Order Linear: y' + P(x)y = Q(x)"""
    complexity = random.choices([1, 2], weights=[0.6, 0.4])[0]
    P_x = get_complex_expr(x, complexity)
    Q_x = get_complex_expr(x, complexity)
    ode = sp.Eq(dy_dx + P_x * y, Q_x)
    
    mu_int = sp.integrate(P_x, x)
    mu = sp.exp(mu_int)

    int_rhs = sp.integrate(mu*Q_x, x)
    eqn = sp.Eq(mu*y, int_rhs + C1)

    reasoning = "The equation is in the form " + sp.latex(ode) + ". By multiplying the entire equation by an integrating factor, I(x) = " + sp.latex(mu) + ", the left side becomes the derivative of the product I(x)y, allowing us to solve for y through direct integration of both sides."

    if mu_int.has(sp.Integral) or int_rhs.has(sp.Integral):
        return None, None, None, None, None
    
    # steps = [
    #     {C.ACTION: "Find P(x)", C.OP: "Find P(x)", C.PARAMS : {}, C.RESULT: f"P(x) = {sp.latex(P_x)}"},
    #     {C.ACTION: "Int Factor Setup", C.OP: "Set mu = exp(int P dx)", C.PARAMS : {}, C.RESULT: f"\\mu(x) = e^{{\\int \\left({sp.latex(P_x)} \\right) dx}}"},
    #     {C.ACTION: "Int Factor Calc", C.OP: "Calculate mu", C.PARAMS : {}, C.RESULT: f"\\mu(x) = {sp.latex(mu)}"},
    #     {C.ACTION: "Multiply", C.OP: "Apply mu to ODE", C.PARAMS : {}, C.RESULT: f"\\frac{{d}}{{dx}}({sp.latex(mu)}y) = {sp.latex(sp.simplify(mu*Q_x))}"},
    #     {C.ACTION: "Integrate", C.OP: "Integrate", C.PARAMS : {C.EXPRESSION : sp.latex(sp.simplify(mu*Q_x)), C.WRT : "x"}, C.RESULT: sp.latex(eqn)},
    # ]

    steps = [
        {C.ACTION: C.ACT_IDENTIFY, C.OP: "Find P(x)", C.PARAMS : {C.EXPRESSION: sp.latex(P_x), C.RESULT_AS: "P(x)"},
                                                            C.RESULT: f"P(x) = {sp.latex(P_x)}"},
        {C.ACTION: C.ACT_IF_CALC, C.OP: "Calculate Set mu = exp(int P dx)", C.PARAMS : {C.EXPRESSION: "P(x)", C.RESULT_AS: "IF", C.WRT : "x"},
                                                            C.RESULT: f"\\mu(x) = e^{{\\int \\left({sp.latex(P_x)} \\right) dx}}"},
        {C.ACTION: C.ACT_MULTIPLY, C.OP: "Prepare right hand side", C.PARAMS : {C.OPERAND1: C.EQ_RIGHT, C.OPERAND2: "IF", C.OPERAND_TYPE: (C.EXPRESSION, C.EXPRESSION), C.RESULT_AS: "prepared right"},
                                                            C.RESULT: f"\\frac{{d}}{{dx}}({sp.latex(mu)}y) = {sp.latex(sp.simplify(mu*Q_x))}"},
        {C.ACTION: C.ACT_MULTIPLY, C.OP: "Prepare left hand side", C.PARAMS : {C.OPERAND1: "IF", C.OPERAND2: "y", C.OPERAND_TYPE: (C.EXPRESSION, C.VAR), C.RESULT_AS: "prepared left"},
                                                            C.RESULT: f"\\frac{{d}}{{dx}}({sp.latex(mu)}y) = {sp.latex(sp.simplify(mu*Q_x))}"},
        {C.ACTION: C.ACT_INTEGRATE, C.OP: "Integrate", C.PARAMS : {C.EXPRESSION : "prepared right", C.WRT : "x", C.RESULT_AS: "integrated right"},
                                                            C.RESULT: sp.latex(eqn)},
        {C.ACTION: C.ACT_SOLVE, C.OP: "Isolate y", C.PARAMS : {C.EQUATION : ("prepared left", "integrated right"), C.WRT: "y", C.RESULT_AS: C.SOLUTION}, C.RESULT: sp.latex(eqn)}
    ]
    
    soln = sp.solve(eqn, y)
    return sp.latex(ode), "First-Order Linear", reasoning, steps, [sp.latex(s) for s in soln]

def generate_exact():
    """Expert for exact ODEs : M(x, y)dx + N(x, y)dy = 0"""
    complexity = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
    M = get_complex_expr_doubled(x, y, complexity)
    g_y = random.choice([y, y**2, sp.exp(y), sp.sin(y), sp.cos(y), random.randint(-5, 5), random.randint(-5, 5) + random.randint(-5, 5) * y, random.randint(-5, 5) + random.randint(-5, 5) * y**2]) 
    psi = sp.integrate(M, x) 
    diffed_int_M = sp.diff(psi, y) 
    g__y = sp.diff(g_y, y)
    N = diffed_int_M + g__y

    ode = sp.Eq(M * dx + N * dy, 0)

    reasoning = "The equation " + sp.latex(ode) + " satisfies the condition $\frac{\partial M}{\partial y} = \frac{\partial N}{\partial x}$, implying it is the total differential of a potential function $\psi(x, y)$. We can find $\psi$ by integrating M with respect to x and then adjusting for any remaining y-terms using N."

    if psi.has(sp.Integral):
        return None, None, None, None, None

    # eqn = sp.Eq(N, diffed_int_M)

    steps = [
        {C.ACTION: C.ACT_IDENTIFY, C.OP: "Find M(x, y) : ", C.PARAMS : {C.EXPRESSION : sp.latex(M), C.RESULT_AS: "M(x, y)"}, C.RESULT: f"M(x, y) = {sp.latex(M)}"},
        {C.ACTION: C.ACT_IDENTIFY, C.OP: "Find N(x, y) : ", C.PARAMS : {C.EXPRESSION : sp.latex(N), C.RESULT_AS: "N(x, y)"}, C.RESULT: f"N(x, y) = {sp.latex(N)}"},
        {C.ACTION: C.ACT_INTEGRATE, C.OP: "Integrate", C.PARAMS : {C.EXPRESSION : "M(x, y)", C.WRT :"x", C.RESULT_AS: "psi(x,y)"}, C.RESULT: sp.latex(psi) + " + g(y)"},
        {C.ACTION: C.ACT_DIFFERENTIATE, C.PARAMS : {C.EXPRESSION : "psi(x, y)", C.WRT :"y", C.RESULT_AS: "psi'(x,y)"}, C.OP: "Differentiate", C.RESULT: f"{sp.latex(diffed_int_M)} + g'(y)"},
        {C.ACTION: C.ACT_ADD, C.PARAMS : {C.OPERAND1: "psi'(x,y)", C.OPERAND2: "g'(y)", C.OPERAND_TYPE: (C.EXPRESSION, C.VAR), C.RESULT_AS: "psi'(x,y) + g'(y)"}, C.OP: "Add g'(y)", C.RESULT: f"{sp.latex(psi)} + g'(y)"},
        {C.ACTION: C.ACT_SOLVE, C.PARAMS : {C.EQUATION : ("psi'(x,y) + g'(y)", "N(x, y)"), C.WRT: "g'(y)", C.RESULT_AS: "g'(y)"}, C.OP: "Solve", C.RESULT: sp.latex(g__y)},
        {C.ACTION: C.ACT_INTEGRATE, C.PARAMS : {C.EXPRESSION : "g'(y)", C.WRT: "y", C.RESULT_AS: "g(y)"}, C.OP: "Integrate", C.RESULT: sp.latex(g_y) + " + C"},
        {C.ACTION: C.ACT_ADD, C.PARAMS : {C.OPERAND1: "psi(x,y)", C.OPERAND2: "g(y)", C.OPERAND_TYPE: (C.EXPRESSION, C.EXPRESSION), C.RESULT_AS: "psi(x,y) + g(y)"}, C.OP: "Form psi + g", C.RESULT: f"{sp.latex(psi)} + {sp.latex(g_y)} = C_1"},
        {C.ACTION: C.ACT_SOLVE, C.PARAMS : {C.EQUATION : ("psi(x,y) + g(y)", "C_1"), C.WRT: "y", C.RESULT_AS: C.SOLUTION }, C.OP: "Solve for y"},
    ]

    soln = sp.Eq(psi + g_y, C1)
    return sp.latex(ode), "Exact", reasoning, steps, [sp.latex(soln),]


def main():
    function_map = {
        "generate_exact" : generate_exact,
        "generate_linear" : generate_linear,
        "generate_separable" : generate_separable
    }

    parser = argparse.ArgumentParser(description="Generate ODE Step-by-Step Dataset")
    parser.add_argument("--output", default="ode_dataset.json", help="Output JSON filename")
    parser.add_argument("--samples", type=int, default=75, help="Number of samples to generate")
    parser.add_argument("--func", type=str, nargs='+', choices=function_map.keys(), help="The name of the function to add to the list")
    args = parser.parse_args()

    dataset = []
    
    generators = [function_map[name] for name in args.func]

    for i in range(args.samples):
        try:
            print(f"case {i+1} : ")
            gen_func = random.choice(generators)
            ode, family, reasoning, steps, soln = gen_func()
            if family == None:
                continue
            latex_ode = ode
            print(latex_ode)
            # latex_soln = sp.latex(soln)
            print(f"Function generated from: {family}\n")
            
            if family is not None:
                dataset.append({
                    C.REASONONG : reasoning,
                    C.FAMILY: family,
                    C.EQUATION: latex_ode,
                    C.Q_STEPS: steps,
                    C.SOLUTION: ", ".join(soln),
                })
        except Exception as e: print(f"Exception : {e}")

    with open(args.output, 'w') as f:
        json.dump(dataset, f, indent=4)
    print(f"Successfully generated {len(dataset)} samples to {args.output}")

if __name__ == "__main__":
    main()