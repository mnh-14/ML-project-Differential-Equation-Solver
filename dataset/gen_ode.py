import json
import sympy as sp
import random
import argparse
import sys

# Define symbols
x = sp.Symbol('x')
y = sp.Function('y')(x)
C1 = sp.Symbol('C1')

def get_complex_expr(var, complexity=2):
    """Generates varied mathematical expressions to avoid duplicates."""
    basics = [var, var**2, sp.sin(var), sp.exp(var), sp.cos(var), sp.log(sp.Abs(var) + 1)]
    expr = random.choice(basics) * random.randint(1, 5)
    for _ in range(complexity - 1):
        other = random.choice(basics) + random.randint(1, 3)
        op = random.choice(['add', 'mul'])
        expr = expr + other if op == 'add' else expr * other
    return sp.simplify(expr)

def generate_separable():
    """Expert for Separable ODEs: dy/dx = f(x)g(y)"""
    f_x = get_complex_expr(x, complexity=2)
    g_y_sym = random.choice([sp.Symbol('y'), sp.Symbol('y')**2, sp.exp(sp.Symbol('y'))])
    ode = sp.Eq(y.diff(x), f_x * g_y_sym.subs(sp.Symbol('y'), y))
    
    steps = [
        {"step": "Classify", "op": "Separate Variables", "res": f"\\frac{{1}}{{{sp.latex(g_y_sym)}}} dy = {sp.latex(f_x)} dx"},
        {"step": "Integrate_LHS", "op": "Integrate Left Side", "res": sp.latex(sp.integrate(1/g_y_sym, sp.Symbol('y')))},
        {"step": "Integrate_RHS", "op": "Integrate Right Side", "res": f"{sp.latex(sp.integrate(f_x, x))} + C_1"},
        {"step": "Solve", "op": "Isolate y", "res": sp.latex(sp.dsolve(ode, y).rhs)}
    ]
    return "Separable", ode, steps

def generate_linear():
    """Expert for First-Order Linear: y' + P(x)y = Q(x)"""
    P_x = get_complex_expr(x, complexity=1)
    Q_x = get_complex_expr(x, complexity=1)
    ode = sp.Eq(y.diff(x) + P_x * y, Q_x)
    
    mu_int = sp.integrate(P_x, x)
    mu = sp.exp(mu_int)
    
    steps = [
        {"step": "Identify", "op": "Find P(x)", "res": f"P(x) = {sp.latex(P_x)}"},
        {"step": "Int_Factor_Setup", "op": "Set mu = exp(int P dx)", "res": f"\\mu(x) = e^{{\\int {sp.latex(P_x)} dx}}"},
        {"step": "Int_Factor_Calc", "op": "Calculate mu", "res": f"\\mu(x) = {sp.latex(mu)}"},
        {"step": "Multiply", "op": "Apply mu to ODE", "res": f"\\frac{{d}}{{dx}}({sp.latex(mu)}y) = {sp.latex(sp.simplify(mu*Q_x))}"},
        {"step": "Integrate", "op": "Integrate both sides", "res": f"{sp.latex(mu)}y = {sp.latex(sp.integrate(mu*Q_x, x))} + C_1"}
    ]
    return "First-Order Linear", ode, steps

def main():
    parser = argparse.ArgumentParser(description="Generate ODE Step-by-Step Dataset")
    parser.add_argument("--output", default="ode_dataset.json", help="Output JSON filename")
    parser.add_argument("--samples", type=int, default=100, help="Number of samples to generate")
    args = parser.parse_args()

    dataset = []
    generators = [generate_separable, generate_linear]

    for _ in range(args.samples):
        try:
            gen_func = random.choice(generators)
            family, ode, steps = gen_func()
            
            dataset.append({
                "family": family,
                "question": sp.latex(ode),
                "steps": steps,
                "final_result": sp.latex(sp.dsolve(ode, y))
            })
        except: continue

    with open(args.output, 'w') as f:
        json.dump(dataset, f, indent=4)
    print(f"Successfully generated {len(dataset)} samples to {args.output}")

if __name__ == "__main__":
    main()