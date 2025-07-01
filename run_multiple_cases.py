"""
Script to run the case generation pipeline multiple times.
Keeps the Mac from sleeping during execution.
"""
import subprocess
import time
import os
import datetime
from pathlib import Path

def run_pipeline(num_cases=50, delay_seconds=10):
    """Run the pipeline multiple times with a delay between runs"""
    
    # Create output directory for this batch
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    batch_dir = Path(f"Output/Generated_Cases_Batch_{timestamp}")
    batch_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🚀 Starting batch generation of {num_cases} cases")
    print(f"📁 Saving to: {batch_dir}")
    
    # Keep track of successful generations
    successful = 0
    
    # Prevent system sleep (macOS)
    # This runs the caffeinate command in the background
    caffeinate_process = subprocess.Popen(["caffeinate", "-i", "-s"])
    
    try:
        start_time = time.time()
        
        # Run the pipeline multiple times
        for i in range(1, num_cases + 1):
            print(f"\n{'='*80}")
            print(f"🔄 Running case generation {i}/{num_cases}")
            print(f"{'='*80}\n")
            
            # Set environment variable for output directory
            os.environ["CASE_OUTPUT_DIR"] = str(batch_dir)
            
            # Run the pipeline
            result = subprocess.run(
                ["python", "-m", "src.pipeline.runner"],
                check=False,  # Don't raise exception on non-zero exit
                capture_output=False  # Allow output to console
            )
            
            # Check if run was successful
            if result.returncode == 0:
                successful += 1
            else:
                print(f"⚠️ Case generation {i} failed with exit code {result.returncode}")
            
            # Progress update
            elapsed = time.time() - start_time
            avg_time_per_case = elapsed / i
            remaining_cases = num_cases - i
            estimated_time_left = avg_time_per_case * remaining_cases
            
            print(f"\n{'='*40}")
            print(f"📊 Progress: {i}/{num_cases} cases completed ({successful} successful)")
            print(f"⏱️ Elapsed time: {elapsed/60:.1f} minutes")
            print(f"⏳ Estimated time remaining: {estimated_time_left/60:.1f} minutes")
            print(f"{'='*40}\n")
            
            # Sleep between runs (skip delay after the last run)
            if i < num_cases:
                print(f"⏸️ Pausing for {delay_seconds} seconds...")
                time.sleep(delay_seconds)
        
        # Final summary
        total_time = time.time() - start_time
        print(f"\n{'='*80}")
        print(f"✅ Batch generation complete!")
        print(f"📊 Generated {successful}/{num_cases} cases successfully")
        print(f"⏱️ Total time: {total_time/60:.1f} minutes")
        print(f"📁 Cases saved to: {batch_dir}")
        print(f"{'='*80}\n")
        
    finally:
        # Stop the caffeinate process to allow sleep again
        if caffeinate_process:
            caffeinate_process.terminate()
            print("💤 Sleep prevention disabled")

if __name__ == "__main__":
    run_pipeline(num_cases=100, delay_seconds=10)