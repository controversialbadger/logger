"""
Basic example of mouse movement analysis without GUI.
This script demonstrates the core functionality of the Mouse Curve Analyzer.
"""

from pynput.mouse import Listener
import time
import numpy as np
import matplotlib.pyplot as plt
import os

def analyze_mouse_movements(recording_time=10, dpi=800):
    """
    Record and analyze mouse movements for the specified time.
    
    Args:
        recording_time (int): Recording duration in seconds
        dpi (int): Mouse DPI setting
        
    Returns:
        dict: Analysis results
    """
    print(f"Recording mouse movements for {recording_time} seconds...")
    print("Move your mouse naturally...")
    
    # Data collection
    data = []
    start_time = time.time()
    
    def on_move(x, y):
        current_time = time.time() - start_time
        if current_time <= recording_time:
            data.append((current_time, x, y))
            return True
        else:
            return False  # Stop listener
    
    # Start recording
    with Listener(on_move=on_move) as listener:
        listener.join()
    
    print(f"Recording complete. Collected {len(data)} data points.")
    
    if len(data) <= 1:
        print("Not enough data collected. Please try again.")
        return None
    
    # Calculate velocities
    velocities = []
    for i in range(1, len(data)):
        t1, x1, y1 = data[i-1]
        t2, x2, y2 = data[i]
        distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        time_diff = t2 - t1
        if time_diff > 0:
            velocity = distance / time_diff  # pixels/s
            velocities.append(velocity)
    
    if not velocities:
        print("No valid velocity data. Please try again.")
        return None
    
    # Analyze data
    mean_velocity = np.mean(velocities)
    std_velocity = np.std(velocities)
    max_velocity = np.max(velocities)
    
    # Convert to dots per millisecond
    velocity_dots_ms = [v / (dpi * 1000) for v in velocities]
    max_velocity_dots_ms = max(velocity_dots_ms)
    
    # Generate suggestions
    if mean_velocity < 100:
        suggested_dpi = "400-600"
    elif mean_velocity < 300:
        suggested_dpi = "800-1000"
    else:
        suggested_dpi = "1200-1600"
    
    if std_velocity < 50:
        curve_type = "Linear"
        curve_description = "Linear (constant sensitivity, e.g., 1.0)"
    elif std_velocity < 100:
        curve_type = "Moderate"
        curve_description = "Moderate (sensitivity increases from 1.0 to 1.5)"
    else:
        curve_type = "Significant"
        curve_description = "Significant (sensitivity increases from 1.0 to 2.0)"
    
    # Print results
    print("\n--- Analysis Results ---")
    print(f"Average velocity: {mean_velocity:.2f} pixels/s")
    print(f"Standard deviation: {std_velocity:.2f} pixels/s")
    print(f"Maximum velocity: {max_velocity:.2f} pixels/s")
    print(f"\nSuggested DPI: {suggested_dpi}")
    print(f"Suggested acceleration curve: {curve_description}")
    
    # Generate curve
    velocities_range = np.linspace(0, max_velocity_dots_ms, 100)
    
    if curve_type == "Linear":
        sensitivities = [1.0] * len(velocities_range)
    elif curve_type == "Moderate":
        sensitivities = [1.0 + 0.5 * (v / max_velocity_dots_ms) for v in velocities_range]
    else:  # Significant
        sensitivities = [1.0 + 1.0 * (v / max_velocity_dots_ms) for v in velocities_range]
    
    # Plot curve
    plt.figure(figsize=(8, 6))
    plt.plot(velocities_range, sensitivities, label="Suggested curve")
    plt.xlabel("Dots per millisecond")
    plt.ylabel("Sensitivity")
    plt.title("Suggested Acceleration Curve")
    plt.grid(True)
    plt.legend()
    
    # Create results directory if it doesn't exist
    results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    os.makedirs(results_dir, exist_ok=True)
    
    # Save plot
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    plot_path = os.path.join(results_dir, f"basic_curve_{timestamp}.png")
    plt.savefig(plot_path)
    print(f"\nCurve saved to: {plot_path}")
    
    # Show plot
    plt.show()
    
    return {
        "data_points": len(data),
        "mean_velocity": mean_velocity,
        "std_velocity": std_velocity,
        "max_velocity": max_velocity,
        "suggested_dpi": suggested_dpi,
        "suggested_curve": curve_description,
        "curve_type": curve_type
    }

if __name__ == "__main__":
    # You can customize these parameters
    recording_seconds = 10  # Shorter time for demonstration
    mouse_dpi = 800
    
    print("Basic Mouse Curve Analysis Example")
    print("==================================")
    print(f"Using DPI: {mouse_dpi}")
    print(f"Recording time: {recording_seconds} seconds")
    print("\nPress Enter to start recording...")
    input()
    
    results = analyze_mouse_movements(recording_seconds, mouse_dpi)
    
    if results:
        print("\nAnalysis complete!")