import json
import math
import random
from multiprocessing import Pool, cpu_count
import time, datetime
import sympy as sp
from manual_gen_ode import *
import argparse
import cProfile, pstats
import constants as C

# Assuming your symbols and generator functions are defined here
# x = sp.Symbol('x')
# y = sp.Function('y')(x)

start = time.time()

dataset = []
count = 0
total_sample = 0


def print_status():
    elapsed = time.time() - start
    eta = (elapsed / count) * (total_sample-count) if count > 0 else 999999
    print("Generated samples: ", count, "/", total_sample,
          ", elapsed time (s): ", datetime.timedelta(seconds=round(elapsed)), 
          " ETA : ", datetime.timedelta(seconds=round(eta)))

def print_batch_status(gen_count, batch_no, batch_size, batch_start_time):
    elapsed = time.time() - batch_start_time
    eta = (elapsed / gen_count) * (batch_size - gen_count) if gen_count > 0 else 999999
    print(f"Batch {batch_no} : Generated {gen_count}/{batch_size} samples"
          f", elapsed time (s): {datetime.timedelta(seconds=round(elapsed))}"
          f" ETA : {datetime.timedelta(seconds=round(eta))}")

def generate_single_sample(index):
    """Generates one sample. The 'index' argument is just for the Pool.map."""
    try:
        family, ode, steps, soln = random.choices([generate_separable, generate_linear], weights=[1,2.5], k=1)[0]()
        
        # hint = '1st_linear' if family == "First-Order Linear" else 'separable'
        # print("Solving ODE:", index, " "* 100, end='\r')
        if ode is None:
            return None
        
        return {
            # "id": index,
            C.FAMILY: family,
            C.EQUATION: ode,
            C.Q_STEPS: steps,
            C.SOLUTION: ", ".join(["y(x) = " + s for s in soln])
        }
    except Exception:
        return None

def main_batch(num_samples=1000, batch_no=0):
    gen_count = 0
    batch_start_time = time.time()
    batch = []
    for i in range(num_samples):
        try:
            val = generate_single_sample(i)
            if val is not None:
                batch.append(val)
                gen_count += 1
            print_batch_status(gen_count, batch_no, num_samples, batch_start_time)
        except Exception as e:
            print(f"Error occurred: {e}", " "*100, end='\r')
    print(f"\nBatch {batch_no} completed: Generated {gen_count}/{num_samples} samples.", " "*15)
    return batch


def main_parallel(num_samples=1000, batch_size=50, timeout=15):
    length = len(dataset)
    batch_count = math.ceil(num_samples / batch_size)
    print(f"Current dataset length: {length}. Generating {num_samples-length} more samples, in {batch_count} batches of size {batch_size}.")
    # what next ?
    with Pool(processes=max(1, cpu_count())) as pool:
        jobs = [pool.apply_async(main_batch, args=(min(batch_size, num_samples - i*batch_size), i+1)) for i in range(batch_count)]
        for jn, job in enumerate(jobs):
            try:
                batch = job.get(timeout=timeout*batch_size)
                dataset.extend(batch)
                global count
                count += len(batch)
                # print_status()
            except Exception as e:
                print(f"Timeout or error occurred in batch {jn+1}: {e}", " "*100, end='\r')

    
        

if __name__ == "__main__":
    # Always run the parallel function inside this guard
    # take input parameters for number of samples and output file if needed
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="manual_dataset.json")
    parser.add_argument("--samples", type=int, default=50)
    parser.add_argument("--timeout", type=int, default=25)
    parser.add_argument("--batch", type=int, default=50)
    args = parser.parse_args()
    length = len(dataset)
    total_sample = args.samples
    pr = cProfile.Profile()
    pr.enable()
    # while length < int(args.samples * 0.91):
    while length <= 0:
        main_parallel(num_samples=args.samples-length, batch_size=args.batch, timeout=args.timeout)
        length = len(dataset)
        print(f"\nSuccess: {length}/{args.samples} samples generated.")
        with open(C.DATA_LOC + args.output, 'w') as f:
            json.dump(dataset, f, indent=4)
    print(f"\nFinished. Saved {len(dataset)}/{args.samples} valid samples to {args.output}")
    pr.disable()
    ps = pstats.Stats(pr).sort_stats('cumulative')
    ps.print_stats(20)