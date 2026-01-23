import json
import sympy as sp
import random
import sys

filename = "training_data.json"

def generate_ode_data(iterations=1000):
    dataset = []
    x = sp.Symbol('x')
    y = sp.Function('y')(x)

    for i in range(iterations):
        try:
            # 1. Randomly choose a family: 0 = Separable, 1 = Linear
            family_type = random.choice(["Separable", "Linear"])
            
            if family_type == "Separable":
                f_x = random.choice([x, x**2, sp.sin(x), sp.exp(x)])
                g_y = random.choice([y, y**2])
                ode = sp.Eq(y.diff(x), f_x * g_y)
                
                # Step-by-step logic
                steps = [
                    {"step_name": "Separate Variables", "result": f"\\frac{{1}}{{{sp.latex(g_y)}}} dy = {sp.latex(f_x)} dx"},
                    {"step_name": "Integrate", "result": f"\\int \\frac{{1}}{{{sp.latex(g_y)}}} dy = \\int {sp.latex(f_x)} dx"}
                ]
            else:
                p_x = random.choice([1, x, 1/x])
                q_x = random.choice([x, sp.exp(x), sp.cos(x)])
                ode = sp.Eq(y.diff(x) + p_x * y, q_x)
                mu = sp.exp(sp.integrate(p_x, x))
                
                steps = [
                    {"step_name": "Find Integrating Factor", "result": f"\\mu(x) = e^{{\\int {sp.latex(p_x)} dx}} = {sp.latex(mu)}"},
                    {"step_name": "Multiply ODE by \\mu(x)", "result": f"{sp.latex(mu)}(y' + {sp.latex(p_x)}y) = {sp.latex(mu * q_x)}"}
                ]

            sol = sp.dsolve(ode, y)
            
            dataset.append({
                "family": family_type,
                "question": sp.latex(ode),
                "steps": steps,
                "final_result": sp.latex(sol)
            })
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error generating sample {i}: {e}")
            continue
        print(f"Generated {i+1}/{iterations} samples", end='\r')

    with open('training_data.json', 'w') as f:
        json.dump(dataset, f, indent=4)
    print(f"Generated {len(dataset)} samples.")


if __name__ == "__main__":
    sample_size = 250
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    if len(sys.argv) > 2:
        sample_size = int(sys.argv[2])
    generate_ode_data(sample_size)

