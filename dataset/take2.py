import json
import sympy as sp
import random
import sys


filename = "complex_ode_dataset.json"

def get_random_function(x, complexity=2):
    """Generates complex nested functions like sin(x**2) or exp(x)*cos(x)."""
    basics = [x, sp.sin(x), sp.cos(x), sp.exp(x), sp.log(x + 2), sp.sqrt(x**2 + 1)]
    func = random.choice(basics)
    for _ in range(complexity - 1):
        op = random.choice(['add', 'mul', 'compose'])
        other = random.choice(basics)
        if op == 'add': func += other
        elif op == 'mul': func *= other
        elif op == 'compose': func = func.subs(x, other)
    return sp.simplify(func)

def generate_complex_dataset(num_samples=5000):
    dataset = []
    x = sp.Symbol('x')
    y = sp.Function('y')(x)

    for i in range(num_samples):
        try:
            family = random.choice(["Separable", "First-Order Linear"])
            print(" "*100, end='\r')  # Clear line
            print(f"Generating sample {i+1}/{num_samples} of family {family}...", end='\r')
            
            if family == "Separable":
                # Form: dy/dx = f(x) * g(y)
                f_x = get_random_function(x, complexity=random.randint(2, 3))
                g_y_val = random.choice([sp.Symbol('y'), sp.Symbol('y')**2, sp.exp(sp.Symbol('y'))])
                ode = sp.Eq(y.diff(x), f_x * g_y_val.subs(sp.Symbol('y'), y))
                print(" "*100, end='\r')  # Clear line
                print(f"Generated ODE{i+1}: {ode}", end='\r')
                
                steps = [
                    {"step": "Classify", "op": "Identify as Separable", "res": f"$\\frac{{dy}}{{{sp.latex(g_y_val)}}} = {sp.latex(f_x)} dx$"},
                    {"step": "Integrate_LHS", "op": "Integrate w.r.t y", "res": f"${sp.latex(sp.integrate(1/g_y_val, sp.Symbol('y')))}$"},
                    {"step": "Integrate_RHS", "op": "Integrate w.r.t x", "res": f"${sp.latex(sp.integrate(f_x, x))} + C$"}
                ]
                print(" "*100, end='\r')  # Clear line
                print(f"Generated Steps for ODE{i+1}", end='\r')

            else: # First-Order Linear: y' + P(x)y = Q(x)
                P_x = get_random_function(x, complexity=2)
                Q_x = get_random_function(x, complexity=2)
                ode = sp.Eq(y.diff(x) + P_x * y, Q_x)
                
                print(" "*100, end='\r')  # Clear line
                print(f"Generated ODE{i+1}: {ode}", end='\r')
                
                # Logic for Multi-Step Trace
                mu_int = sp.integrate(P_x, x)
                mu = sp.exp(mu_int)
                print(" "*100, end='\r')  # Clear line
                print(f"Calculated Integrating Factor for ODE{i+1}", end='\r')
                
                steps = [
                    {"step": "Standard_Form", "op": "Identify P(x) and Q(x)", "res": f"$P(x)={sp.latex(P_x)}, Q(x)={sp.latex(Q_x)}$"},
                    {"step": "Calc_Integrating_Factor", "op": "exp(Integral(P(x)dx))", "res": f"$\\mu(x) = {sp.latex(mu)}$"},
                    {"step": "Multiply_and_Integrate", "op": "d/dx(mu*y) = mu*Q", "res": f"$\\frac{{d}}{{dx}}({sp.latex(mu)}y) = {sp.latex(sp.simplify(mu*Q_x))}$"}
                ]
                print(" "*100, end='\r')  # Clear line
                print(f"Generated Steps for ODE{i+1}", end='\r')

            sol = sp.dsolve(ode, y)
            dataset.append({
                "family": family,
                "question": f"${sp.latex(ode)}$",
                "steps": steps,
                "final_result": f"${sp.latex(sol)}$"
            })
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error generating sample {i}: {e}")
            continue
        print(" "*100, end='\r')  # Clear line
        print(f"Generated {i+1}/{num_samples} samples", end='\r')

    with open(filename, 'w') as f:
        json.dump(dataset, f, indent=4)

if __name__ == "__main__":
    sample_size = 250
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    if len(sys.argv) > 2:
        sample_size = int(sys.argv[2])
    print(f"Generating dataset with {sample_size} samples into '{filename}'...")
    generate_complex_dataset(sample_size)