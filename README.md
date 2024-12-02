# ML Compiler Build Dashboard

A comprehensive build monitoring system for ML compiler projects, tracking build status, failures, and progress across multiple projects including torch-mlir, ieee-mlir, and LLVM-MLIR.

## Features

- Real-time build status monitoring
- Multi-project support with unified interface
- Build failure tracking and analysis
- Email notifications for build status
- Artifact storage and management
- Authentication and user management
- Detailed build logs and history
- Git integration and repository management

## Installation

### Prerequisites

```bash
# Backend dependencies
pip install flask flask-cors gitpython pymongo sqlalchemy boto3 python-jose[cryptography] sendgrid

# Frontend dependencies
npm install @sendgrid/mail aws-sdk bcrypt jsonwebtoken
```

### Configuration

1. Create a `.env` file in the root directory:

```env
# Database
DB_URI=mongodb://localhost:27017/
DB_NAME=build_dashboard

# AWS S3 (for artifacts)
AWS_ACCESS_KEY=our_access_key
AWS_SECRET_KEY=our_secret_key
AWS_REGION=our_region
S3_BUCKET=our_bucket_name

# SendGrid (for email notifications)
SENDGRID_API_KEY=our_sendgrid_api_key
NOTIFICATION_FROM_EMAIL=builds@your-domain.com

# JWT Authentication
JWT_SECRET_KEY=our_secret_key
JWT_ALGORITHM=HS256
```

2. Update `config.yaml` with your project settings:

```yaml
projects:
  torch-mlir:
    repo_url: https://github.com/llvm/torch-mlir
    build_command: python setup.py build
    build_dir: ./torch-mlir-build
    notification_emails:
      - team@amd.com
    
  ieee-mlir:
    repo_url: https://github.com/ieee-mlir/ieee-mlir
    build_command: cmake . && make
    build_dir: ./ieee-mlir-build
    notification_emails:
      - <todo>@amd.com

  llvm-mlir:
    repo_url: https://github.com/llvm/llvm-project
    build_command: |
      cmake -G Ninja ../llvm \
        -DLLVM_ENABLE_PROJECTS=mlir \
        -DLLVM_BUILD_EXAMPLES=ON && ninja
    build_dir: ./llvm-mlir-build
    notification_emails:
      - <todo>@amd.com
```

## Extended Features Implementation

### 1. Project Configuration

Add new projects by updating `config.yaml`. Each project supports:

- Custom build commands
- Multiple build stages
- Branch-specific configurations
- Custom notification settings
- Artifact retention policies

Example addition:

```yaml
new-project:
  repo_url: https://github.com/org/project
  build_command: make all
  build_dir: ./project-build
  branches:
    main:
      notification_threshold: error_only
    develop:
      notification_threshold: all
  artifacts:
    retention_days: 30
    patterns:
      - "*.whl"
      - "*.tar.gz"
```

### 2. Authentication System

```python
# backend/auth.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

class Auth:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.SECRET_KEY = os.getenv("JWT_SECRET_KEY")
        self.ALGORITHM = os.getenv("JWT_ALGORITHM")

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=60)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except JWTError:
            return None
```

### 3. Build Artifacts Storage

```python
# backend/artifacts.py
import boto3
from botocore.exceptions import ClientError
import os

class ArtifactStorage:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        self.bucket = os.getenv('S3_BUCKET')

    def upload_artifact(self, build_id: str, file_path: str):
        try:
            file_name = os.path.basename(file_path)
            key = f"builds/{build_id}/{file_name}"
            self.s3.upload_file(file_path, self.bucket, key)
            return f"s3://{self.bucket}/{key}"
        except ClientError as e:
            return None

    def get_artifact_url(self, build_id: str, file_name: str):
        try:
            key = f"builds/{build_id}/{file_name}"
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': key},
                ExpiresIn=3600
            )
            return url
        except ClientError as e:
            return None
```

### 4. Email Notifications

```python
# backend/notifications.py
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

class NotificationSystem:
    def __init__(self):
        self.sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        self.from_email = os.getenv('NOTIFICATION_FROM_EMAIL')

    def send_build_notification(self, build_info: dict, recipients: list):
        status = build_info['status']
        project = build_info['project_name']
        
        subject = f"Build {status.upper()}: {project}"
        content = self._generate_email_content(build_info)
        
        message = Mail(
            from_email=self.from_email,
            to_emails=recipients,
            subject=subject,
            html_content=content
        )
        
        try:
            self.sg.send(message)
            return True
        except Exception as e:
            print(f"Failed to send notification: {e}")
            return False

    def _generate_email_content(self, build_info: dict) -> str:
        return f"""
        <h2>Build {build_info['status'].upper()}: {build_info['project_name']}</h2>
        <p>Branch: {build_info['branch']}</p>
        <p>Commit: {build_info['commit_hash']}</p>
        <p>Duration: {build_info['duration']} minutes</p>
        {'<p>Error: ' + build_info['error_message'] + '</p>' if build_info.get('error_message') else ''}
        <p><a href="{build_info['dashboard_url']}">View in Dashboard</a></p>
        """
```

### 5. Detailed Build Logs

```python
# backend/logging.py
import logging
from datetime import datetime
import os

class BuildLogger:
    def __init__(self, build_id: str):
        self.build_id = build_id
        self.log_dir = f"logs/builds/{build_id}"
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.logger = logging.getLogger(f"build_{build_id}")
        self.logger.setLevel(logging.DEBUG)
        
        # File handler for complete logs
        fh = logging.FileHandler(f"{self.log_dir}/full.log")
        fh.setLevel(logging.DEBUG)
        
        # File handler for errors only
        eh = logging.FileHandler(f"{self.log_dir}/errors.log")
        eh.setLevel(logging.ERROR)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        eh.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(eh)

    def log_build_step(self, step: str, status: str, message: str = None):
        self.logger.info(f"Step: {step} - Status: {status}" + (f" - {message}" if message else ""))

    def log_error(self, error_message: str):
        self.logger.error(error_message)

    def get_log_content(self, log_type: str = 'full') -> str:
        log_file = f"{self.log_dir}/{log_type}.log"
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                return f.read()
        return ""
```

### 6. Build Metrics and Analytics

```python
# backend/analytics.py
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd

class BuildAnalytics:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_build_metrics(self, days: int = 30) -> Dict:
        start_date = datetime.now() - timedelta(days=days)
        builds = self.db.get_builds_since(start_date)
        
        df = pd.DataFrame(builds)
        
        return {
            'total_builds': len(df),
            'success_rate': (df['status'] == 'success').mean() * 100,
            'average_duration': df['duration'].mean(),
            'failure_distribution': df[df['status'] == 'failed']['error_type'].value_counts().to_dict(),
            'builds_per_day': df.groupby(df['start_time'].dt.date).size().to_dict(),
            'projects_summary': self._get_projects_summary(df)
        }

    def _get_projects_summary(self, df: pd.DataFrame) -> Dict:
        return {
            project: {
                'total_builds': len(project_df),
                'success_rate': (project_df['status'] == 'success').mean() * 100,
                'average_duration': project_df['duration'].mean(),
                'last_successful_build': project_df[project_df['status'] == 'success']['end_time'].max()
            }
            for project, project_df in df.groupby('project_name')
        }

    def get_build_trends(self, days: int = 30) -> Dict:
        metrics = self.get_build_metrics(days)
        
        # Calculate trends
        return {
            'success_rate_trend': self._calculate_trend('success_rate', days),
            'duration_trend': self._calculate_trend('duration', days),
            'volume_trend': self._calculate_trend('builds_per_day', days)
        }

    def _calculate_trend(self, metric: str, days: int) -> float:
        # Implementation of trend calculation
        pass
```

## API Endpoints

### Build Management

```
GET /api/builds - List all builds
GET /api/builds/{id} - Get build details
POST /api/builds/trigger/{project} - Trigger new build
GET /api/builds/{id}/logs - Get build logs
GET /api/builds/{id}/artifacts - List build artifacts
```

### Authentication

```
POST /api/auth/login - User login
POST /api/auth/refresh - Refresh token
```

### Analytics

```
GET /api/analytics/metrics - Get build metrics
GET /api/analytics/trends - Get build trends
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
