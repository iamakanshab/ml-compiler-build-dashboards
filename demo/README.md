# Build Dashboard

A Streamlit dashboard for monitoring PyTorch CI/CD workflows and metrics in real-time. This application provides a comprehensive view of both high-level metrics and detailed workflow status.

## Features

### Metrics Dashboard
- Real-time monitoring of key performance indicators
- Build success/failure rates and trends
- Queue time monitoring and alerts
- Visual trends with charts and graphs
- Automated alerts for:
  - Jobs exceeding queue time thresholds
  - High build failure rates

### Workflow Monitor
- Real-time workflow status tracking
- Status-based filtering (Success, Failed, Running, Pending, Warning)
- Branch and author filtering
- Auto-refresh capability
- Detailed job information
- Color-coded status indicators
- Duration tracking

## Project Structure

```
pytorch-hud-demo/
│
├── README.md
├── requirements.txt
│
└── src/
    ├── __init__.py
    ├── main.py        # Main application with UI components
    ├── models.py      # Data models and enums
    └── schema.py      # Sample data generator
```

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (optional)

## Installation

1. Clone or download this repository:
```bash
git clone <repository-url>
# or download and extract the zip file
```

2. Navigate to the project directory:
```bash
cd pytorch-hud-demo
```

3. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

4. Install required packages:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Make sure your virtual environment is activated (you should see `(venv)` in your terminal prompt)

2. Run using one of these commands:
```bash
# Option 1 - Using python -m
python -m streamlit run src/main.py

# Option 2 - Using streamlit directly (Windows)
venv\Scripts\streamlit.exe run src/main.py

# Option 2 - Using streamlit directly (macOS/Linux)
streamlit run src/main.py
```

3. The application should automatically open in your default web browser. If it doesn't, you can access it at the URL shown in the terminal (typically `http://localhost:8501`)

## Application Usage

### Metrics Dashboard (Tab 1)
1. View key metrics:
   - Current queued jobs
   - Average queue time
   - Build success rate
   - Average build time
2. Monitor trends:
   - Queue time trends (line chart)
   - Build success/failure trends (bar chart)
3. Automated alerts for:
   - Queue time threshold violations
   - High failure rates

### Workflow Monitor (Tab 2)
1. **Viewing Workflows**
   - Expandable cards show detailed information
   - Failed and running workflows auto-expand
   - Color-coded status indicators

2. **Filtering**
   - Filter by:
     - Branch (main, nightly)
     - Status (success, failed, running, pending, warning)
     - Author

3. **Auto-refresh**
   - Toggle auto-refresh for 30-second updates
   - Manual refresh button available

## Development

To modify the application:
1. Update metrics and sample data in `schema.py`
2. Modify data models in `models.py`
3. Update UI components in `main.py`

Current metrics include:
- Build metrics (success rates, failures)
- Queue metrics (wait times, thresholds)
- Historical trends

## Troubleshooting

Common issues and solutions:
- **Import errors**: Ensure you're running from the project root directory
- **Streamlit not found**: Verify virtual environment is activated
- **Module not found**: Check all required packages are installed
- **Streamlit command not recognized**: Use the full path to streamlit.exe in the virtual environment

## License

This project is licensed under the MIT License - see the LICENSE file for details.
