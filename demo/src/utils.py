# app/utils.py
def calculate_duration(start_time: datetime) -> str:
    duration = datetime.utcnow() - start_time
    minutes = duration.total_seconds() / 60
    return f"{int(minutes)}m"