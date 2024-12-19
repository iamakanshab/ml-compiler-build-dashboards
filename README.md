# ML Compiler Build Dashboard

A real-time build monitoring system for ML compiler projects using secure WebSocket connections. Track build status, failures, and progress across torch-mlir, ieee-mlir, and LLVM-MLIR projects through a unified interface.

## Features

- 🔄 Real-time WebSocket-based build monitoring
- 🔒 Secure bidirectional communication (no webhooks)
- 🏗️ ML compiler project support:
  - torch-mlir
  - ieee-mlir
  - LLVM-MLIR
- 📊 Build metrics and failure analysis
- 📦 S3-based artifact management
- 📧 Email notifications via SendGrid
- 🔐 JWT-based authentication
- 📝 Comprehensive build logs
- 📈 Historical data analysis

## Architecture

The system uses a WebSocket-based architecture for real-time communication:
<link from design doc>

## Prerequisites

### System Requirements
- Python 3.8+
- Node.js 18+
- MySQL
- AWS Account

### Dependencies

```bash
# Backend
pip install flask flask-cors gitpython pymongo boto3 python-jose[cryptography] 

# Frontend
npm install aws-sdk bcrypt jsonwebtoken
```

## Configuration

### Environment Setup

Create a `.env` file:

```env
# WebSocket Configuration
WS_ENDPOINT=wss://your-api-gateway-url
WS_REGION=us-east-1

# Database
MYSQL_URI=mongodb://localhost:27017/
DB_NAME=build_dashboard

# AWS Services
AWS_ACCESS_KEY=your_key
AWS_SECRET_KEY=your_secret
AWS_REGION=us-east-1
S3_BUCKET=build-artifacts

# Authentication
JWT_SECRET_KEY=your_jwt_secret
JWT_ALGORITHM=HS256

# Notifications
SECRET_API_KEY=your_enter_key
NOTIFICATION_EMAIL=builds@your-domain.com
```

### Project Configuration

Create `config.yaml`:

```yaml
projects:
  torch-mlir:
    repo_url: https://github.com/llvm/torch-mlir
    build_command: python setup.py build
    build_dir: ./torch-mlir-build
    notification_emails:
      - team@example.com
    websocket:
      reconnect_attempts: 5
      reconnect_interval: 1000
    
  ieee-mlir:
    repo_url: https://github.com/ieee-mlir/ieee-mlir
    build_command: cmake . && make
    build_dir: ./ieee-mlir-build
    websocket:
      reconnect_attempts: 3
      reconnect_interval: 2000

  llvm-mlir:
    repo_url: https://github.com/llvm/llvm-project
    build_command: |
      cmake -G Ninja ../llvm \
        -DLLVM_ENABLE_PROJECTS=mlir \
        -DLLVM_BUILD_EXAMPLES=ON && ninja
    build_dir: ./llvm-mlir-build
```

## Implementation

### Build Agent Setup

```python
from build_dashboard import BuildAgent

agent = BuildAgent(
    project_name="torch-mlir",
    api_key="your_api_key",
    ws_endpoint="wss://your-api-gateway-url"
)

@agent.on_build_start
def handle_build_start(build_id):
    print(f"Build {build_id} started")

@agent.on_build_complete
def handle_build_complete(build_id, status):
    print(f"Build {build_id} completed with status: {status}")

agent.start()
```

### WebSocket Message Protocol

```typescript
// Build Event Message
interface BuildMessage {
    type: 'BUILD_START' | 'BUILD_UPDATE' | 'BUILD_COMPLETE';
    buildId: string;
    project: string;
    data: {
        status: string;
        progress?: number;
        metrics?: BuildMetrics;
        error?: string;
    };
    timestamp: number;
}

// Subscription Message
interface SubscriptionMessage {
    type: 'SUBSCRIBE';
    projects: string[];
    events: string[];
}
```

### API Routes

```typescript
// WebSocket Routes
const routes = {
    $connect: handleConnect,
    $disconnect: handleDisconnect,
    build_update: handleBuildUpdate,
    subscribe: handleSubscribe
};

// REST API Routes
app.get('/api/builds', listBuilds);
app.get('/api/builds/:id', getBuildDetails);
app.get('/api/builds/:id/logs', getBuildLogs);
app.get('/api/builds/:id/artifacts', listArtifacts);
app.post('/api/auth/login', login);
```

## Development

### Local Setup

1. Start local services:
```bash
docker-compose up -d mysql
```

2. Install dependencies:
```bash
pip install -r requirements.txt
npm install
```

3. Run the development server:
```bash
python server.py
```

4. Start the dashboard:
```bash
npm run dev
```

### Testing

```bash
# Backend tests
python -m pytest

# Frontend tests
npm run test
```

## Deployment

### AWS Deployment

1. Deploy infrastructure:
```bash
terraform init
terraform apply
```

2. Configure API Gateway:
```bash
aws apigateway create-websocket-api \
  --name "BuildDashboardAPI" \
  --protocol-type WEBSOCKET
```

3. Deploy application:
```bash
./deploy.sh
```

## Monitoring

### CloudWatch Metrics
- WebSocket connection count
- Message processing latency
- Build duration
- Error rates

### Logging
- Build logs in CloudWatch
- Agent connection logs
- Build state transitions

## Security

### WebSocket Security
- API key authentication
- JWT for client connections
- Message validation
- Rate limiting

### Data Protection
- In-transit encryption (WSS)
- At-rest encryption (S3/DynamoDB)
- Access logging

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add feature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- pytorch HUD
- AWS WebSocket API
- ML Compiler Communities
