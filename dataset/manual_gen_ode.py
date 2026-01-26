import json
import sympy as sp
import random
import argparse
import sys
import constants as C
from sympy import Piecewise
from sympy.diffgeom import Differential

# Define symbols
x = sp.Symbol('x')
# y = sp.Function('y')(x)
y = sp.Symbol('y')
dx = sp.Symbol('dx', commutative=False)
dy = sp.Symbol('dy', commutative=False)
# dx = Differential(x)
# dy = Differential(y)
C1 = sp.Symbol('C1')


# Generate expressions :
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
    vars_basic= [var1, var2]
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
    return "First-Order Linear", ode, steps, [sp.latex(s) for s in soln]

def generate_exact():
    """Expert for exact ODEs : M(x, y)dx + N(x, y)dy = 0"""
    M = get_complex_expr_doubled(x, y)
    g_y = random.choice([y**3, y**2, sp.exp(y)])
    int_M_dx = sp.integrate(M, x) 
    diffed_int_M = sp.diff(int_M_dx, y) 
    g__y = sp.diff(g_y, y)
    N = diffed_int_M + g__y

    ode = sp.Eq(M * dx + N * dy, 0)

    if int_M_dx.has(sp.Integral):
        return None, None, None, None

    # eqn = sp.Eq(N, diffed_int_M)

    steps = [
        {C.STEP: "Identify", C.OP: "Find M(x, y) : ", C.RESULT: f"M(x, y) = {sp.latex(M)}"},
        {C.STEP: "Identify", C.OP: "Find N(x, y) : ", C.RESULT: f"N(x, y) = {sp.latex(N)}"},
        {C.STEP: "Integrate M(x, y) wrt x --> [F(x, y)]:", C.OP: "Integrate", C.RESULT: sp.latex(int_M_dx) + " + g(y)"},
        {C.STEP: "Differentiate F(x, y) wrt y : ", C.OP: "Differentiate", C.RESULT: f"{sp.latex(diffed_int_M)} + g'(y)"},
        {C.STEP: "Solve N = diff(F) for g'(y)", C.OP: "Solve", C.RESULT: sp.latex(g__y)},
        {C.STEP: "Integrate g'(y) wrt y : ", C.OP: "Integrate", C.RESULT: sp.latex(g_y) + " + C"},
    ]

    soln = sp.Eq(int_M_dx + g_y, C1)
    return "Exact", ode, steps, [sp.latex(soln),]


def main():
    parser = argparse.ArgumentParser(description="Generate ODE Step-by-Step Dataset")
    parser.add_argument("--output", default="ode_dataset.json", help="Output JSON filename")
    parser.add_argument("--samples", type=int, default=20, help="Number of samples to generate")
    args = parser.parse_args()

    dataset = []
    generators = [generate_exact, generate_linear, generate_separable]

    for i in range(args.samples):
        try:
            print(f"case {i+1} : ")
            gen_func = random.choice(generators)
            family, ode, steps, soln = gen_func()
            latex_ode = sp.latex(ode)
            # latex_soln = sp.latex(soln)
            print(f"Function generated from: {family}\n")
            
            if family is not None:
                dataset.append({
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