import json
import random
import argparse
from multiprocessing import Pool, cpu_count
import sympy as sp
import constants as C
from sympy import Piecewise

# Global symbols
x = sp.Symbol('x')
y = sp.Function('y')(x)
Y = sp.Symbol('y')  # Dummy variable for separation integration
C1 = sp.Symbol('C1')

piecewise_log = Piecewise(
    (sp.log(x), x>0),
    (sp.log(-x), x<0)
)

def get_random_expr(var, complexity=2):
    """Generates unique math expressions to ensure diversity."""
    basics = [var, var**2, sp.sin(var), sp.cos(var), sp.tan(var), sp.exp(var), sp.acos(var), sp.asin(var), sp.atan(var), piecewise_log]
    expr = random.choice(basics) * random.randint(1, 5)
    for _ in range(complexity - 1):
        other = random.choice(basics) + random.randint(1, 3)
        expr = random.choice([expr + other, expr * other])
    return sp.simplify(expr)

def solve_separable_manual():
    """Manual Policy: dy/g(y) = f(x)dx"""
    f = get_random_expr(x, complexity=2)
    g_raw = random.choice([Y, Y**2, sp.exp(Y)])
    
    ode = sp.Eq(y.diff(x), f * g_raw.subs(Y, y))
    
    # Manual Trace
    steps = [
        {C.STEP: "identify family", C.RESULT: "Separable"},
        {C.STEP: "separate", C.RESULT: f"dy / ({sp.latex(g_raw)}) = ({sp.latex(f)}) dx"},
        {C.STEP: "integrate lhs", C.RESULT: sp.latex(sp.integrate(1/g_raw, Y))},
        {C.STEP: "integrate rhs", C.RESULT: f"{sp.latex(sp.integrate(f, x))} + C_1"}
    ]
    
    # Final algebraic solve for y
    lhs_int = sp.integrate(1/g_raw, Y)
    rhs_int = sp.integrate(f, x) + C1
    sol = sp.solve(sp.Eq(lhs_int, rhs_int), Y)
    
    return "Separable", ode, steps, [sp.latex(s) for s in sol]

def solve_linear_manual():
    """Manual Policy: Integrating Factor Method"""
    P = get_random_expr(x, complexity=1)
    Q = get_random_expr(x, complexity=1)
    ode = sp.Eq(y.diff(x) + P*y, Q)
    
    # Manual Trace
    mu_expr = sp.integrate(P, x)
    mu = sp.exp(mu_expr)
    
    steps = [
        {C.STEP: "identify family", C.RESULT: "First-Order Linear"},
        {C.STEP: "find P Q", C.RESULT: f"P(x)={sp.latex(P)}, Q(x)={sp.latex(Q)}"},
        {C.STEP: "calc mu", C.RESULT: f"\\mu(x) = e^{{\\int {sp.latex(P)} dx}} = {sp.latex(mu)}"},
        {C.STEP: "integrate product", C.RESULT: f"\\mu y = \\int {sp.latex(sp.simplify(mu*Q))} dx"}
    ]
    
    rhs_integrated = sp.integrate(mu * Q, x) + C1
    final_y = sp.simplify(rhs_integrated / mu)
    
    return "Linear", ode, steps, [sp.latex(final_y)]

def worker(_):
    """The task performed by each processor."""
    try:
        family_func = random.choice([solve_separable_manual, solve_linear_manual])
        fam, ode, steps, sol_list = family_func()
        return {
            C.FAMILY: fam,
            C.EQUATION: sp.latex(ode),
            C.Q_STEPS: steps,
            C.SOLUTION: sol_list
        }
    except:
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="manual_dataset.json")
    parser.add_argument("--samples", type=int, default=50)
    args = parser.parse_args()

    print(f"Generating {args.samples} samples on {cpu_count()} cores...")
    
    with Pool(cpu_count()) as p:
        results = p.map(worker, range(args.samples))
    
    dataset = [r for r in results if r is not None]
    
    with open(args.output, 'w') as f:
        json.dump(dataset, f, indent=4)
    print(f"Finished. Saved {len(dataset)} valid samples to {args.output}")

if __name__ == "__main__":
    main()