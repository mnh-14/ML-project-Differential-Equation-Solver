from ast import parse
import json
import random
from multiprocessing import cpu_count
from pebble import ProcessPool
from concurrent.futures import TimeoutError, as_completed
import time, datetime
import sympy as sp
from equation_generator import *
import argparse
import cProfile, pstats
from previous_resources.Previous_Codes import constants as C

# Assuming your symbols and generator functions are defined here
# x = sp.Symbol('x')
# y = sp.Function('y')(x)

start = time.time()

dataset = []
count = 0
total_sample = 0
current_function = None


def print_status():
    elapsed = time.time() - start
    eta = (elapsed / count) * (total_sample-count) if count > 0 else 999999
    print("Generated samples: ", count, "/", total_sample,
          ", elapsed time (s): ", datetime.timedelta(seconds=round(elapsed)), 
          " ETA : ", datetime.timedelta(seconds=round(eta)), end="\r")

# def print_batch_status(gen_count, batch_no, batch_size, batch_start_time):
#     elapsed = time.time() - batch_start_time
#     eta = (elapsed / gen_count) * (batch_size - gen_count) if gen_count > 0 else 999999
#     print(f"Batch {batch_no} : Generated {gen_count}/{batch_size} samples"
#           f", elapsed time (s): {datetime.timedelta(seconds=round(elapsed))}"
#           f" ETA : {datetime.timedelta(seconds=round(eta))}")

def generate_single_sample(index, target_func):
    """Generates one sample. The 'index' argument is just for the Pool.map."""
    try:
        ode, family, reasoning, steps, soln = target_func()
        
        # hint = '1st_linear' if family == "First-Order Linear" else 'separable'
        print("Solving ODE:", index, " "* 100, end='\r')
        if ode is None:
            return None
        
        return {
            # "id": index,
            C.FAMILY: family,
            C.REASONONG: reasoning,
            C.EQUATION: ode,
            C.Q_STEPS: steps,
            C.SOLUTION: ", ".join(["y(x) = " + s for s in soln])
        }
    except Exception:
        return None


def main_parallel(target_func, num_samples=1000, timeout=15):
    length = len(dataset)
    global count
    func_args = [target_func] * num_samples
    print(f"Current dataset length: {length}. Generating {num_samples} more samples.")
    with ProcessPool(max_workers=max(1, cpu_count()-1)) as pool:
        future = pool.map(generate_single_sample, range(length+1, length+num_samples+1), func_args, timeout=timeout)
        iterator = future.result()
        print("Started parallel generation with some", "workers.")
        while True:
            try:
                res = iterator.next()
                if res is not None:
                    dataset.append(res)
                    count += 1
                print_status()
            except StopIteration:
                break
            except TimeoutError:
                print("A task took too long and was terminated.")
            except Exception:
                continue
    
        

if __name__ == "__main__":
    # Always run the parallel function inside this guard
    # take input parameters for number of samples and output file if needed
    funcs = {
        "separable": generate_separable,
        "linear": generate_linear,
        "exact": generate_exact
    }
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="manual_dataset.json")
    parser.add_argument("--samples", type=int, default=50)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--func", default="exact", choices=["separable", "linear", "exact"])
    args = parser.parse_args()
    length = len(dataset)
    total_sample = args.samples
    current_function = funcs.get(args.func)
    pr = cProfile.Profile()
    pr.enable()
    while length < int(args.samples * 0.95):
    # while length <= 0:
        main_parallel(current_function, num_samples=args.samples-length, timeout=args.timeout)
        length = len(dataset)
        print(f"\nSuccess: {length}/{args.samples} samples generated.")
        with open(args.output, 'w') as f:
            json.dump(dataset, f, indent=4)
    print(f"\nFinished. Saved {len(dataset)}/{args.samples} valid samples to {args.output}")
    pr.disable()
    ps = pstats.Stats(pr).sort_stats('cumulative')
    ps.print_stats(20)
