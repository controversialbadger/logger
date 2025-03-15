# Mouse Curve Analyzer

A professional application that analyzes your mouse movements and suggests optimal DPI settings and acceleration curves for your gaming or productivity needs.

## Overview

Mouse Curve Analyzer tracks your mouse movements for a specified period (default: 60 seconds), analyzes the data, and provides recommendations for:

- Optimal DPI (Dots Per Inch) settings
- Appropriate acceleration curve based on your movement patterns

The application visualizes the suggested acceleration curve, allowing you to understand how mouse sensitivity should change based on movement speed.

## Features

- **Real-time mouse movement tracking**: Records position data at high frequency
- **Comprehensive analysis**: Calculates average velocity, standard deviation, and maximum velocity
- **Personalized recommendations**: Suggests DPI settings based on your movement patterns
- **Visual curve representation**: Displays the recommended acceleration curve
- **Results saving**: Saves analysis results and graphs for future reference
- **Customizable settings**: Adjust recording time and input your current DPI

## Requirements

- Python 3.6 or higher
- Required Python packages (see requirements.txt):
  - pynput
  - numpy
  - matplotlib
  - tkinter (usually comes with Python)

## Installation

1. Clone or download this repository
2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:

```bash
python mouse_curve.py
```

2. Enter your current mouse DPI (if known) or use the default value
3. Adjust the recording time if needed (default is 60 seconds)
4. Click "Start Recording" and use your mouse normally for the specified duration
5. Once recording completes, the application will analyze your movements and display:
   - Statistical data about your mouse movements
   - Suggested DPI range
   - Recommended acceleration curve type
   - Visual representation of the suggested curve
6. Click "Save Results" to store the analysis and curve image for future reference

## Understanding the Results

### DPI Recommendations

- **400-600 DPI**: Suggested for users with slow, precise movements
- **800-1000 DPI**: Recommended for average movement speeds
- **1200-1600 DPI**: Ideal for fast, sweeping movements

### Acceleration Curve Types

- **Linear**: Constant sensitivity regardless of movement speed (recommended for consistent, predictable movements)
- **Moderate**: Sensitivity increases moderately with speed (balanced approach for mixed usage)
- **Significant**: Sensitivity increases substantially with speed (ideal for users who alternate between precise and fast movements)

## How It Works

The application:
1. Records mouse position data at regular intervals
2. Calculates movement velocities between consecutive points
3. Analyzes velocity patterns to determine your typical movement profile
4. Converts pixel-based velocities to "dots per millisecond" using your DPI setting
5. Generates recommendations based on statistical analysis of your movement patterns
6. Creates a visual representation of the suggested acceleration curve

## Troubleshooting

- **No data collected**: Ensure your mouse is moving during the recording period
- **Inaccurate results**: Try a longer recording period or ensure you're using the mouse naturally
- **Application not responding**: Restart the application and try again with a shorter recording period

## License

This project is open source and available under the MIT License.