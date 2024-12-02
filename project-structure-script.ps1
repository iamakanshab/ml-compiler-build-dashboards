# Create-MLBuildDashboard.ps1

# Define root directories
$projectRoot = "ml-build-dashboard"
$frontendRoot = "ml-build-dashboard-frontend"
$backendRoot = "ml-build-dashboard-backend"

# Directory structures
$frontendDirs = @(
    "src/components/common",
    "src/components/dashboard",
    "src/components/builds",
    "src/hooks",
    "src/services",
    "src/styles",
    "src/utils",
    "src/types",
    "src/context",
    "public",
    "tests/unit",
    "tests/integration",
    "docs"
)

$backendDirs = @(
    "src/api/routes",
    "src/api/middleware",
    "src/auth",
    "src/config",
    "src/models",
    "src/services/build",
    "src/services/notification",
    "src/services/storage",
    "src/utils",
    "src/types",
    "tests/unit",
    "tests/integration",
    "logs/builds",
    "artifacts",
    "docs"
)

# Create root project directory and README
Write-Host "Creating project structure..." -ForegroundColor Green
New-Item -ItemType Directory -Path $projectRoot
Set-Location $projectRoot

# Create frontend structure
Write-Host "Creating frontend directory structure..." -ForegroundColor Blue
New-Item -ItemType Directory -Path $frontendRoot
foreach ($dir in $frontendDirs) {
    New-Item -ItemType Directory -Path (Join-Path $frontendRoot $dir) -Force
    Write-Host "Created frontend directory: $dir" -ForegroundColor Yellow
}

# Create backend structure
Write-Host "Creating backend directory structure..." -ForegroundColor Blue
New-Item -ItemType Directory -Path $backendRoot
foreach ($dir in $backendDirs) {
    New-Item -ItemType Directory -Path (Join-Path $backendRoot $dir) -Force
    Write-Host "Created backend directory: $dir" -ForegroundColor Yellow
}

# Create necessary files
$files = @{
    # Root project files
    "README.md" = @"
# ML Build Dashboard

Monorepo for the ML Compiler Build Dashboard system.

## Structure
- `/ml-build-dashboard-frontend` - React frontend application
- `/ml-build-dashboard-backend` - Python Flask backend service

See individual project READMEs for setup and development instructions.
"@

    # Frontend files
    "$frontendRoot/.env.development" = @"
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_WS_URL=ws://localhost:5000/ws
"@

    "$frontendRoot/.env.production" = @"
REACT_APP_API_URL=/api
REACT_APP_WS_URL=/ws
"@

    "$frontendRoot/README.md" = @"
# ML Build Dashboard Frontend

React-based frontend for the ML Compiler Build Dashboard.

## Setup
1. Install dependencies: \`npm install\`
2. Start development server: \`npm start\`
3. Run tests: \`npm test\`
4. Build for production: \`npm run build\`

## Development
- \`/src/components\` - React components
- \`/src/services\` - API communication
- \`/src/hooks\` - Custom React hooks
- \`/src/context\` - React context providers
- \`/src/types\` - TypeScript type definitions
"@

    "$frontendRoot/package.json" = @"
{
  "name": "ml-build-dashboard-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "lint": "eslint src --ext .ts,.tsx",
    "format": "prettier --write \"src/**/*.{ts,tsx}\""
  },
  "dependencies": {
    "@sendgrid/mail": "^7.7.0",
    "aws-sdk": "^2.1359.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "recharts": "^2.5.0",
    "typescript": "^4.9.5"
  },
  "devDependencies": {
    "@testing-library/react": "^13.4.0",
    "@types/react": "^18.0.28",
    "@typescript-eslint/eslint-plugin": "^5.54.0",
    "eslint": "^8.35.0",
    "prettier": "^2.8.4"
  }
}
"@

    "$frontendRoot/.gitignore" = @"
# Dependencies
node_modules/
/.pnp
.pnp.js

# Testing
/coverage

# Production
/build

# Misc
.DS_Store
.env.local
.env.development.local
.env.test.local
.env.production.local

npm-debug.log*
yarn-debug.log*
yarn-error.log*
"@

    # Backend files
    "$backendRoot/.env.development" = @"
FLASK_ENV=development
FLASK_APP=src/app.py
DB_URI=mongodb://localhost:27017/
DB_NAME=build_dashboard_dev
"@

    "$backendRoot/.env.production" = @"
FLASK_ENV=production
FLASK_APP=src/app.py
DB_URI=mongodb://localhost:27017/
DB_NAME=build_dashboard_prod
"@

    "$backendRoot/README.md" = @"
# ML Build Dashboard Backend

Flask-based backend service for the ML Compiler Build Dashboard.

## Setup
1. Create virtual environment: \`python -m venv venv\`
2. Activate virtual environment: \`source venv/bin/activate\` (Linux/Mac) or \`.\venv\Scripts\Activate.ps1\` (Windows)
3. Install dependencies: \`pip install -r requirements.txt\`
4. Run development server: \`flask run\`
5. Run tests: \`pytest\`

## Development
- \`/src/api\` - API routes and middleware
- \`/src/services\` - Business logic
- \`/src/models\` - Data models
- \`/src/config\` - Configuration
"@

    "$backendRoot/requirements.txt" = @"
flask==2.0.1
flask-cors==3.0.10
python-jose[cryptography]==3.3.0
sendgrid==6.9.7
boto3==1.26.137
pymongo==4.3.3
pyyaml==6.0
gitpython==3.1.31
pytest==7.3.1
black==23.3.0
flake8==6.0.0
mypy==1.3.0
"@

    "$backendRoot/.gitignore" = @"
# Python
__pycache__/
*.py[cod]
*$py.class
venv/
.env
.env.*
!.env.example

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/

# Logs
logs/
*.log

# Build artifacts
artifacts/
"@

    "$backendRoot/src/config/config.yaml" = @"
projects:
  torch-mlir:
    repo_url: https://github.com/llvm/torch-mlir
    build_command: python setup.py build
    build_dir: ./torch-mlir-build
    notification_emails:
      - team@example.com
"@
}

Write-Host "Creating project files..." -ForegroundColor Green
foreach ($file in $files.Keys) {
    $filePath = Join-Path -Path $projectRoot -ChildPath $file
    $files[$file] | Out-File -FilePath $filePath -Encoding UTF8
    Write-Host "Created file: $file" -ForegroundColor Yellow
}

# Initialize git repositories
Write-Host "Initializing git repositories..." -ForegroundColor Green
git init

# Setup frontend
Write-Host "Setting up frontend..." -ForegroundColor Green
Set-Location $frontendRoot
git init
npm install

# Setup backend
Write-Host "Setting up backend..." -ForegroundColor Green
Set-Location ../$backendRoot
git init
python -m venv venv
./venv/Scripts/Activate.ps1
pip install -r requirements.txt

Write-Host "`nProject setup complete!" -ForegroundColor Green
Write-Host "`nDirectory structure:"
Set-Location ..
Get-ChildItem -Recurse -Directory | Select-Object FullName | Format-Table -AutoSize

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Frontend setup:"
Write-Host "   - cd $frontendRoot"
Write-Host "   - Update .env.development with your configuration"
Write-Host "   - npm start"
Write-Host "`n2. Backend setup:"
Write-Host "   - cd $backendRoot"
Write-Host "   - Update .env.development with your configuration"
Write-Host "   - flask run"
