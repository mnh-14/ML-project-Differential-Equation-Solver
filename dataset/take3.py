import json
import random
from multiprocessing import Pool, cpu_count
import re
import sympy as sp
from gen_ode import *
import argparse
import constants as C

# Assuming your symbols and generator functions are defined here
x = sp.Symbol('x')
y = sp.Function('y')(x)

def generate_single_sample(index):
    """Generates one sample. The 'index' argument is just for the Pool.map."""
    try:
        # Choose a generator family (Separable or Linear)
        # Ensure these functions are defined and return (family, ode, steps)
        family, ode, steps = random.choice([generate_separable, generate_linear])()
        
        # Optimize dsolve: disable expensive simplification if needed
        # and provide a hint to skip classification overhead
        hint = '1st_linear' if family == "First-Order Linear" else 'separable'
        print("Solving ODE:", index)
        if ode is None:
            return None
        solution = sp.dsolve(ode, y, hint=hint, simplify=True)
        
        return {
            "id": index,
            C.FAMILY: family,
            C.EQUATION: sp.latex(ode),
            C.Q_STEPS: steps,
            C.SOLUTION: sp.latex(solution)
        }
    except Exception:
        # Silently skip equations that are too complex to solve
        return None

def main_parallel(num_samples=1000, output_file="fast_dataset.json", timeout=15):
    print(f"Starting parallel generation for {num_samples} samples...")
    
    # Using Pool as a context manager ensures proper cleanup
    dataset = []
    with Pool(processes=cpu_count()) as pool:
        # map() handles the distribution across your CPU cores
        async_result = [pool.apply_async(generate_single_sample, args=(i,)) for i in range(num_samples)]
        for res in async_result:
            try:
                val = res.get(timeout=timeout)
                if val is not None:
                    dataset.append(val)
            except Exception as e:
                print(f"Timeout or error occurred: {e}")
    
    
    with open(output_file, 'w') as f:
        json.dump(dataset, f, indent=4)
        
    print(f"Success: {len(dataset)}/{num_samples} samples saved to {output_file}")

if __name__ == "__main__":
    # Always run the parallel function inside this guard
    # take input parameters for number of samples and output file if needed
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="manual_dataset.json")
    parser.add_argument("--samples", type=int, default=50)
    parser.add_argument("--timeout", type=int, default=15)
    args = parser.parse_args()
    main_parallel(num_samples=args.samples, output_file=args.output)