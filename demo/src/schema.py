from datetime import datetime, timedelta
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from models import StatusEnum, Job, Workflow

def get_sample_workflows():
    return [
        Workflow(
            id="1234567",
            name="pull / linux-focal-py3.8-gcc7 / build",
            branch="main",
            commit="a1b2c3d",
            author="pytorch-bot",
            status=StatusEnum.RUNNING,
            start_time=datetime.now() - timedelta(minutes=25),
            duration="25m",
            jobs=[
                Job(name="setup", status=StatusEnum.SUCCESS, duration="2m"),
                Job(name="build", status=StatusEnum.RUNNING, duration="23m"),
                Job(name="test_python", status=StatusEnum.PENDING, duration="-"),
            ]
        ),
        Workflow(
            id="1234568",
            name="trunk / win-vs2019-cuda11.8-py3 / test",
            branch="main",
            commit="e4f5g6h",
            author="contributor",
            status=StatusEnum.FAILED,
            start_time=datetime.now() - timedelta(minutes=40),
            duration="40m",
            jobs=[
                Job(name="setup", status=StatusEnum.SUCCESS, duration="3m"),
                Job(name="build", status=StatusEnum.SUCCESS, duration="25m"),
                Job(name="test_python", status=StatusEnum.FAILED, duration="12m", 
                    error="Test failures in distributed tests"),
            ]
        )
    ]