#this script runs 2 other scripts in parallel and after both of these are done it will run a third script

import multiprocessing
import subprocess
from time import process_time 

def run_script(script_name):
    subprocess.run(["python", script_name])


# Start the stopwatch / counter  
t1_start = process_time()  

if __name__ == "__main__":
    # Define the scripts to run
    scripts_to_run = ["calibrateIntrinsics.py", "imgsubtrcontours.py", "calibrateExtrinsics.py", "silhouetteReconstruction.py"]

    # Create processes for the first two scripts
    processes = [multiprocessing.Process(target=run_script, args=(script,)) for script in scripts_to_run[:2]]

    # Start the processes for the first two scripts
    for process in processes:
        process.start()

    # Wait for the first two processes to finish
    for process in processes:
        process.join()

    # Run the third and fourth script
    subprocess.run(["python", scripts_to_run[2]])
    subprocess.run(["python", scripts_to_run[3]])
    
# Stop the stopwatch / counter 
t1_stop = process_time() 

   
print("Elapsed time:", t1_stop, t1_start)  
   
print("Elapsed time during the whole program in seconds:", t1_stop-t1_start)  