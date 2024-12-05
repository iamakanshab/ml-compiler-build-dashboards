# Build Dashboard 

A Streamlit dashboard for monitoring PyTorch CI/CD workflow runs in real-time. This application provides a clean, intuitive interface for tracking workflow status, build progress, and test results.

## Features

- Real-time workflow monitoring
- Status-based filtering (Success, Failed, Running, Pending, Warning)
- Branch and author filtering
- Auto-refresh capability
- Detailed job information for each workflow
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
    ├── main.py
    ├── models.py
    └── schema.py
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

1. **Viewing Workflows**
   - The main page displays all recent workflow runs
   - Expandable cards show detailed information for each workflow
   - Failed and running workflows are automatically expanded

2. **Filtering**
   - Use the Filters expander to filter by:
     - Branch (main, nightly)
     - Status (success, failed, running, pending, warning)
     - Author

3. **Auto-refresh**
   - Toggle auto-refresh to automatically update the display every 30 seconds
   - Use the Refresh button for manual updates

## Development

To modify the demo data or add new features:
1. Update sample workflows in `schema.py`
2. Modify data models in `models.py`
3. Update the UI components in `main.py`

## Troubleshooting

If you encounter import errors:
- Make sure you're running the application from the project root directory
- Verify that all required packages are installed
- Check that the virtual environment is activated
- Try running with the full path to the streamlit executable in the virtual environment

## License

This project is licensed under the MIT License - see the LICENSE file for details.
