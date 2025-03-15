import tkinter as tk
from tkinter import ttk, messagebox
from pynput.mouse import Listener
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import os
import json

class MouseCurveAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Curve Analyzer")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Set application style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Variables
        self.data = []
        self.velocities = []
        self.velocity_dots_ms = []
        self.recording = False
        self.dpi_var = tk.StringVar(value="800")
        self.recording_time_var = tk.StringVar(value="60")
        self.status_var = tk.StringVar(value="Ready")
        self.progress_var = tk.DoubleVar(value=0)
        
        # Analysis results
        self.mean_velocity = 0
        self.std_velocity = 0
        self.max_velocity = 0
        self.suggested_dpi = ""
        self.suggested_curve = ""
        
        # Create UI
        self.create_ui()
        
        # Load previous settings if available
        self.load_settings()
    
    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # DPI setting
        ttk.Label(settings_frame, text="Current Mouse DPI:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(settings_frame, textvariable=self.dpi_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Recording time setting
        ttk.Label(settings_frame, text="Recording Time (seconds):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(settings_frame, textvariable=self.recording_time_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="Start Recording", command=self.start_recording)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Status and progress
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT, padx=5)
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=5)
        
        self.progress = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress.pack(fill=tk.X, padx=5, pady=5)
        
        # Results frame
        self.results_frame = ttk.LabelFrame(main_frame, text="Analysis Results", padding="10")
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Initially hide the results
        self.results_text = tk.Text(self.results_frame, height=5, width=50, state=tk.DISABLED)
        self.results_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Graph frame
        self.graph_frame = ttk.Frame(self.results_frame)
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Save button
        self.save_button = ttk.Button(main_frame, text="Save Results", command=self.save_results, state=tk.DISABLED)
        self.save_button.pack(side=tk.RIGHT, padx=5, pady=5)
    
    def start_recording(self):
        try:
            # Validate inputs
            dpi = int(self.dpi_var.get())
            recording_time = int(self.recording_time_var.get())
            
            if dpi <= 0 or recording_time <= 0:
                messagebox.showerror("Invalid Input", "DPI and recording time must be positive numbers.")
                return
            
            # Reset data
            self.data = []
            self.velocities = []
            self.velocity_dots_ms = []
            self.recording = True
            
            # Update UI
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_var.set("Recording...")
            self.progress_var.set(0)
            
            # Clear previous results
            self.clear_results()
            
            # Start recording in a separate thread
            self.recording_thread = threading.Thread(target=self.record_mouse_movements, args=(recording_time,))
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            # Start progress update
            self.update_progress(recording_time)
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for DPI and recording time.")
    
    def record_mouse_movements(self, recording_time):
        self.start_time = time.time()
        
        def on_move(x, y):
            if not self.recording:
                return False
            
            current_time = time.time() - self.start_time
            if current_time <= recording_time:
                self.data.append((current_time, x, y))
            else:
                self.recording = False
                return False
        
        with Listener(on_move=on_move) as listener:
            listener.join()
        
        # Process data after recording
        self.root.after(0, self.analyze_data)
    
    def update_progress(self, recording_time):
        if self.recording:
            elapsed = time.time() - self.start_time
            progress = min(100, (elapsed / recording_time) * 100)
            self.progress_var.set(progress)
            
            if elapsed < recording_time:
                self.root.after(100, lambda: self.update_progress(recording_time))
            else:
                self.progress_var.set(100)
    
    def stop_recording(self):
        self.recording = False
        self.status_var.set("Recording stopped")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        # Process data if we have any
        if len(self.data) > 1:
            self.analyze_data()
    
    def analyze_data(self):
        if len(self.data) <= 1:
            self.status_var.set("Not enough data collected")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            return
        
        self.status_var.set("Analyzing data...")
        
        # Calculate velocities
        self.velocities = []
        for i in range(1, len(self.data)):
            t1, x1, y1 = self.data[i-1]
            t2, x2, y2 = self.data[i]
            distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            time_diff = t2 - t1
            if time_diff > 0:
                velocity = distance / time_diff  # pixels/s
                self.velocities.append(velocity)
        
        if not self.velocities:
            self.status_var.set("No valid velocity data")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            return
        
        # Analyze data
        self.mean_velocity = np.mean(self.velocities)
        self.std_velocity = np.std(self.velocities)
        self.max_velocity = np.max(self.velocities)
        
        # Convert to dots per millisecond
        dpi = int(self.dpi_var.get())
        self.velocity_dots_ms = [v / (dpi * 1000) for v in self.velocities]
        max_velocity_dots_ms = max(self.velocity_dots_ms)
        
        # Generate suggestions
        if self.mean_velocity < 100:
            self.suggested_dpi = "400-600"
        elif self.mean_velocity < 300:
            self.suggested_dpi = "800-1000"
        else:
            self.suggested_dpi = "1200-1600"
        
        if self.std_velocity < 50:
            self.suggested_curve = "Linear (constant sensitivity, e.g., 1.0)"
            curve_type = "Linear"
        elif self.std_velocity < 100:
            self.suggested_curve = "Moderate (sensitivity increases from 1.0 to 1.5)"
            curve_type = "Moderate"
        else:
            self.suggested_curve = "Significant (sensitivity increases from 1.0 to 2.0)"
            curve_type = "Significant"
        
        # Display results
        self.display_results(max_velocity_dots_ms, curve_type)
        
        # Update UI
        self.status_var.set("Analysis complete")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.NORMAL)
    
    def display_results(self, max_velocity_dots_ms, curve_type):
        # Update results text
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        results = (
            f"Data points collected: {len(self.data)}\n"
            f"Average velocity: {self.mean_velocity:.2f} pixels/s\n"
            f"Standard deviation: {self.std_velocity:.2f} pixels/s\n"
            f"Maximum velocity: {self.max_velocity:.2f} pixels/s\n\n"
            f"Suggested DPI: {self.suggested_dpi}\n"
            f"Suggested acceleration curve: {self.suggested_curve}"
        )
        
        self.results_text.insert(tk.END, results)
        self.results_text.config(state=tk.DISABLED)
        
        # Create and display the graph
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        
        # Generate curve based on analysis
        velocities_range = np.linspace(0, max_velocity_dots_ms, 100)
        
        if curve_type == "Linear":
            sensitivities = [1.0] * len(velocities_range)
        elif curve_type == "Moderate":
            sensitivities = [1.0 + 0.5 * (v / max_velocity_dots_ms) for v in velocities_range]
        else:  # Significant
            sensitivities = [1.0 + 1.0 * (v / max_velocity_dots_ms) for v in velocities_range]
        
        ax.plot(velocities_range, sensitivities, label="Suggested curve")
        ax.set_xlabel("Dots per millisecond")
        ax.set_ylabel("Sensitivity")
        ax.set_title("Suggested Acceleration Curve")
        ax.grid(True)
        ax.legend()
        
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def clear_results(self):
        # Clear results text
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)
        
        # Clear graph
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        
        # Disable save button
        self.save_button.config(state=tk.DISABLED)
    
    def save_results(self):
        # Create results directory if it doesn't exist
        results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
        os.makedirs(results_dir, exist_ok=True)
        
        # Save settings
        settings = {
            "dpi": self.dpi_var.get(),
            "recording_time": self.recording_time_var.get()
        }
        
        with open(os.path.join(results_dir, "settings.json"), "w") as f:
            json.dump(settings, f)
        
        # Save analysis results
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        results_file = os.path.join(results_dir, f"analysis_{timestamp}.txt")
        
        with open(results_file, "w") as f:
            f.write(f"Mouse Curve Analysis Results - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"DPI: {self.dpi_var.get()}\n")
            f.write(f"Recording time: {self.recording_time_var.get()} seconds\n\n")
            f.write(f"Data points collected: {len(self.data)}\n")
            f.write(f"Average velocity: {self.mean_velocity:.2f} pixels/s\n")
            f.write(f"Standard deviation: {self.std_velocity:.2f} pixels/s\n")
            f.write(f"Maximum velocity: {self.max_velocity:.2f} pixels/s\n\n")
            f.write(f"Suggested DPI: {self.suggested_dpi}\n")
            f.write(f"Suggested acceleration curve: {self.suggested_curve}\n")
        
        # Save graph
        graph_file = os.path.join(results_dir, f"curve_{timestamp}.png")
        
        for widget in self.graph_frame.winfo_children():
            if isinstance(widget, FigureCanvasTkAgg):
                widget.figure.savefig(graph_file)
                break
        
        messagebox.showinfo("Save Complete", f"Results saved to:\n{results_file}\n{graph_file}")
    
    def load_settings(self):
        settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "settings.json")
        
        if os.path.exists(settings_file):
            try:
                with open(settings_file, "r") as f:
                    settings = json.load(f)
                
                if "dpi" in settings:
                    self.dpi_var.set(settings["dpi"])
                
                if "recording_time" in settings:
                    self.recording_time_var.set(settings["recording_time"])
            except:
                pass  # Ignore errors when loading settings

if __name__ == "__main__":
    root = tk.Tk()
    app = MouseCurveAnalyzer(root)
    root.mainloop()