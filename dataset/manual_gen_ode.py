import json
import sympy as sp
import random
import argparse
import sys
import constants as C
from sympy import Piecewise

# Define symbols
x = sp.Symbol('x')
# y = sp.Function('y')(x)
y = sp.Symbol('y')
dx = sp.Symbol('dx')
dy = sp.Symbol('dy')
C1 = sp.Symbol('C1')

piecewise_log = Piecewise(
    (sp.log(x), x>0),
    (sp.log(-x), x<0)
)

def get_complex_expr(var, complexity=2):
    """Generates varied mathematical expressions to avoid duplicates."""
    basics = [var, var**2, sp.sin(var), sp.cos(var), sp.tan(var), sp.exp(var), sp.acos(var), sp.asin(var), sp.atan(var), sp.log(var)]
    expr = random.choice(basics) * random.randint(1, 10)
    for _ in range(complexity - 1):
        other = random.choice(basics) + random.randint(1, 6)
        op = random.choice(['add', 'mul'])
        expr = expr + other if op == 'add' else expr * other
    return sp.simplify(expr)

def get_complex_expr_doubled(var1, var2, complexity=2):
    """Generates varied mathematical expressions to avoid duplicates."""
    basics_1 = [var1, var1**2, var2, var2**2, var1*var2]
    basics = [random.choice(basics_1), sp.sin(random.choice(basics_1)), sp.cos(random.choice(basics_1))]
    expr = random.choice(basics) * random.randint(1, 10)
    for _ in range(complexity - 1):
        other = random.choice(basics) + random.randint(1, 6)
        op = random.choice(['add', 'mul'])
        expr = expr + other if op == 'add' else expr * other
    return sp.simplify(expr)

def generate_separable():
    """Expert for Separable ODEs: dy/dx = f(x)g(y)"""
    f_x = get_complex_expr(x, complexity=2)
    g_y_sym = random.choice([y, y**2, sp.exp(y)])
    ode = sp.Eq(dy/dx, f_x * g_y_sym)
    lhs = sp.integrate(1/g_y_sym, y)
    rhs = sp.integrate(f_x, x)
    eqn = sp.Eq(lhs, rhs + C1)

    if lhs.has(sp.Integral) or rhs.has(sp.Integral):
        return None, None, None, None
    
    steps = [
        {C.STEP: "Classify", C.OP: "Separate Variables", C.RESULT: f"\\frac{{1}}{{{sp.latex(g_y_sym)}}} dy = \\left({sp.latex(f_x)}\\right) dx"},
        {C.STEP: "Integrate LHS", C.OP: "Integrate Left Side", C.RESULT: sp.latex(lhs)},
        {C.STEP: "Integrate RHS", C.OP: "Integrate Right Side", C.RESULT: f"{sp.latex(rhs)} + C_1"},
        {C.STEP: "Solve", C.OP: "Isolate y", C.RESULT: sp.latex(eqn)}
    ]
    soln = sp.solve(eqn, y)
    return "Separable", sp.latex(ode), steps, [sp.latex(s) for s in soln]

def generate_linear():
    """Expert for First-Order Linear: y' + P(x)y = Q(x)"""
    P_x = get_complex_expr(x, complexity=1)
    Q_x = get_complex_expr(x, complexity=1)
    ode = sp.Eq(dy/dx + P_x * y, Q_x)
    
    mu_int = sp.integrate(P_x, x)
    mu = sp.exp(mu_int)

    int_rhs = sp.integrate(mu*Q_x, x)
    eqn = sp.Eq(mu*y, int_rhs + C1)

    if mu_int.has(sp.Integral) or int_rhs.has(sp.Integral):
        return None, None, None, None
    
    steps = [
        {C.STEP: "Identify", C.OP: "Find P(x)", C.RESULT: f"P(x) = {sp.latex(P_x)}"},
        {C.STEP: "Int Factor Setup", C.OP: "Set mu = exp(int P dx)", C.RESULT: f"\\mu(x) = e^{{\\int \\left({sp.latex(P_x)} \\right) dx}}"},
        {C.STEP: "Int Factor Calc", C.OP: "Calculate mu", C.RESULT: f"\\mu(x) = {sp.latex(mu)}"},
        {C.STEP: "Multiply", C.OP: "Apply mu to ODE", C.RESULT: f"\\frac{{d}}{{dx}}({sp.latex(mu)}y) = {sp.latex(sp.simplify(mu*Q_x))}"},
        {C.STEP: "Integrate", C.OP: "Integrate both sides", C.RESULT: sp.latex(eqn)}
    ]
    
    soln = sp.solve(eqn, y)
    return "First-Order Linear", sp.latex(ode), steps, [sp.latex(s) for s in soln]

def generate_exact():
    """Expert for exact ODEs : M(x, y)dx + N(x, y)dy = 0"""
    M = get_complex_expr_doubled(x, y)
    N = get_complex_expr_doubled(x, y)

    print(f"Functions found : M = {M}, N = {N}\n")
    ode = sp.Eq(M * dx + N * dy, 0)

    #================= Skipping this thing for now =================
    # if sp.diff(M, y) != sp.diff(N, x):
    #     return None

    int_M_dx = sp.integrate(M, x) 
    print(f"Integrated M : {int_M_dx}")
    eqn = sp.Eq(int_M_dx, C1)
    print(f"The equation : {eqn}")

    steps = [
        {C.STEP: "Identify", C.OP: "Find M : ", C.RESULT: f"M(x, y) = {sp.latex(M)}"},
        {C.STEP: "Integrate", C.OP: "Integrate M with respect to x : ", C.RESULT: sp.latex(int_M_dx)},
    ]

    soln = sp.solve(eqn, y)
    return "Exact", sp.latex(ode), steps, [sp.latex(s) for s in soln]


def main():
    parser = argparse.ArgumentParser(description="Generate ODE Step-by-Step Dataset")
    parser.add_argument("--output", default="ode_dataset.json", help="Output JSON filename")
    parser.add_argument("--samples", type=int, default=100, help="Number of samples to generate")
    args = parser.parse_args()

    dataset = []
    generators = [generate_exact]

    for _ in range(args.samples):
        try:
            gen_func = random.choice(generators)
            family, ode, steps, soln = gen_func()
            
            dataset.append({
                C.FAMILY: family,
                C.EQUATION: sp.latex(ode),
                C.Q_STEPS: steps,
                C.SOLUTION: sp.latex(sp.dsolve(ode, y))
            })
        except Exception as e: print(e)

    with open(args.output, 'w') as f:
        json.dump(dataset, f, indent=4)
    print(f"Successfully generated {len(dataset)} samples to {args.output}")

if __name__ == "__main__":
    main()