# PyTorch HUD Demo

A Streamlit dashboard for monitoring PyTorch workflow runs.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Setup Instructions

1. Clone or download this repository:
```bash
git clone <repository-url>
# or download and extract the zip file
```

2. Navigate to the project directory:
```bash
cd pytorch-hud-demo
```

3. Create a virtual environment:
```bash
# On Windows
python -m venv venv

# On macOS/Linux
python3 -m venv venv
```

4. Activate the virtual environment:
```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

5. Install the required packages:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Make sure your virtual environment is activated (you should see `(venv)` in your terminal prompt)

2. Run the Streamlit application:
```bash
streamlit run src/main.py
```

3. The application should automatically open in your default web browser. If it doesn't, you can access it at the URL shown in the terminal (typically `http://localhost:8501`)

## Project Structure

```
pytorch-hud-demo/
│
├── README.md
├── requirements.txt
│
└── src/
    └── pytorch-hud-backend.py
```

## Features

- Real-time workflow monitoring
- Status filtering
- Auto-refresh capability
- Detailed job information
- Branch and author filtering

## Development

To modify the sample data or add new features, edit the `src/pytorch-hud-backend.py` file. The application will automatically reload when you save changes.
