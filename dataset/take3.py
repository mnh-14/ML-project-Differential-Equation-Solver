import json
import random
from multiprocessing import Pool, cpu_count
import time, datetime
import sympy as sp
from gen_ode import *
import argparse
import constants as C

# Assuming your symbols and generator functions are defined here
x = sp.Symbol('x')
y = sp.Function('y')(x)

start = time.time()

dataset = []
count = 0
total_sample = 0


def print_status():
    elapsed = time.time() - start
    eta = (elapsed / count) * (total_sample-count) if count > 0 else 999999
    print("Generated samples: ", count, "/", total_sample,
          ", elapsed time (s): ", datetime.timedelta(seconds=round(elapsed)), 
          " ETA : ", datetime.timedelta(seconds=round(eta)), end='\r')

def generate_single_sample(index):
    """Generates one sample. The 'index' argument is just for the Pool.map."""
    try:
        family, ode, steps = random.choices([generate_separable, generate_linear], weights=[1,2.5], k=1)[0]()
        
        hint = '1st_linear' if family == "First-Order Linear" else 'separable'
        print("Solving ODE:", index, " "* 100, end='\r')
        if ode is None:
            return None
        solution = sp.dsolve(ode, y, hint=hint, simplify=True)
        
        return {
            # "id": index,
            C.FAMILY: family,
            C.EQUATION: sp.latex(ode),
            C.Q_STEPS: steps,
            C.SOLUTION: sp.latex(solution)
        }
    except Exception:
        return None

def main_parallel(num_samples=1000, timeout=15):
    length = len(dataset)
    global count
    print(f"Current dataset length: {length}. Generating {num_samples} more samples.")
    with Pool(processes=cpu_count()) as pool:
        async_result = [pool.apply_async(generate_single_sample, args=(i,)) for i in range(len(dataset)+1, length+num_samples+1)]
        for res in async_result:
            try:
                val = res.get(timeout=timeout)
                if val is not None:
                    dataset.append(val)
                    count += 1
                print_status()
            except Exception as e:
                print(f"Timeout or error occurred: {e}", " "*100, end='\r')
    
        

if __name__ == "__main__":
    # Always run the parallel function inside this guard
    # take input parameters for number of samples and output file if needed
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="manual_dataset.json")
    parser.add_argument("--samples", type=int, default=50)
    parser.add_argument("--timeout", type=int, default=15)
    args = parser.parse_args()
    length = len(dataset)
    total_sample = args.samples
    while length < int(args.samples * 0.91):
        main_parallel(num_samples=args.samples-length, timeout=args.timeout)
        length = len(dataset)
        print(f"\nSuccess: {length}/{args.samples} samples generated.")
        with open(C.DATA_LOC + args.output, 'w') as f:
            json.dump(dataset, f, indent=4)
    print(f"\nFinished. Saved {len(dataset)}/{args.samples} valid samples to {args.output}")