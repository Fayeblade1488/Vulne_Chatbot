# 🆘 Complete Troubleshooting Guide - "Help, I'm Stuck!"

## Table of Contents
1. [Common Installation Issues](#common-installation-issues)
2. [Runtime Errors](#runtime-errors)
3. [Model-Related Problems](#model-related-problems)
4. [Frontend Issues](#frontend-issues)
5. [Benchmarking Failures](#benchmarking-failures)
6. [Docker & Container Issues](#docker--container-issues)
7. [Network & API Problems](#network--api-problems)
8. [Database Issues](#database-issues)
9. [Performance Problems](#performance-problems)
10. [Security & Permission Errors](#security--permission-errors)
11. [CI/CD Pipeline Failures](#cicd-pipeline-failures)
12. [Emergency Recovery](#emergency-recovery)

---

## 🔧 Common Installation Issues

### Problem: "pip install fails with error"

**Symptoms:**
```
ERROR: Could not find a version that satisfies the requirement...
ERROR: No matching distribution found for...
```

**Solutions:**

1. **Update pip first:**
```bash
python -m pip install --upgrade pip
```

2. **Check Python version:**
```bash
python --version
# Should be 3.9 or higher
```

3. **Use specific Python version:**
```bash
python3.11 -m pip install -r requirements.txt
```

4. **Install from cache clear:**
```bash
pip cache purge
pip install --no-cache-dir -r requirements.txt
```

5. **Use different index:**
```bash
pip install -r requirements.txt --index-url https://pypi.org/simple
```

6. **Install dependencies one by one:**
```bash
# Create a script to install with error handling
cat > install_deps.py << 'EOF'
import subprocess
import sys

with open('requirements.txt') as f:
    packages = f.readlines()

failed = []
for package in packages:
    package = package.strip()
    if package and not package.startswith('#'):
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ Installed: {package}")
        except:
            print(f"❌ Failed: {package}")
            failed.append(package)

if failed:
    print("\nFailed packages:")
    for p in failed:
        print(f"  - {p}")
EOF

python install_deps.py
```

### Problem: "ModuleNotFoundError: No module named 'xxx'"

**Solutions:**

1. **Check virtual environment is activated:**
```bash
# Check if in venv
which python
# Should show path/to/venv/bin/python

# Activate if needed
source venv/bin/activate  # Unix/Mac
# or
venv\Scripts\activate  # Windows
```

2. **Reinstall the module:**
```bash
pip uninstall <module_name>
pip install <module_name>
```

3. **Check PYTHONPATH:**
```bash
echo $PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

4. **Install in development mode:**
```bash
pip install -e benchmarking/
```

### Problem: "npm install fails"

**Symptoms:**
```
npm ERR! code ERESOLVE
npm ERR! ERESOLVE unable to resolve dependency tree
```

**Solutions:**

1. **Clear npm cache:**
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

2. **Use legacy peer deps:**
```bash
npm install --legacy-peer-deps
```

3. **Update npm:**
```bash
npm install -g npm@latest
```

4. **Use yarn instead:**
```bash
npm install -g yarn
yarn install
```

5. **Manual resolution:**
```bash
# Edit package.json to fix version conflicts
npm install --force
```

---

## 🚨 Runtime Errors

### Problem: "Port 7000 is already in use"

**Solutions:**

1. **Find and kill the process:**
```bash
# Find process using port
lsof -i :7000  # Mac/Linux
netstat -ano | findstr :7000  # Windows

# Kill the process
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows
```

2. **Use different port:**
```bash
# Edit app/vulne_chat.py
PORT = 7001  # Change port

# Or use environment variable
export FLASK_PORT=7001
python app/vulne_chat.py
```

3. **Docker cleanup:**
```bash
docker ps  # Check running containers
docker stop $(docker ps -q)  # Stop all
docker system prune -a  # Clean everything
```

### Problem: "Flask app crashes immediately"

**Solutions:**

1. **Check for syntax errors:**
```bash
python -m py_compile app/vulne_chat.py
```

2. **Run in debug mode:**
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app/vulne_chat.py
```

3. **Check dependencies:**
```bash
pip list | grep -i flask
# Should show Flask installed
```

4. **Test minimal app:**
```python
# test_app.py
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Working!"

if __name__ == '__main__':
    app.run(port=7000)
```

### Problem: "Redis connection refused"

**Solutions:**

1. **Start Redis:**
```bash
# Using Docker
docker run -d -p 6379:6379 redis:alpine

# Using system package
sudo systemctl start redis  # Linux
brew services start redis  # Mac
```

2. **Check Redis is running:**
```bash
redis-cli ping
# Should return PONG
```

3. **Fix connection string:**
```python
# Check .env.real
REDIS_URL=redis://localhost:6379/0

# Test connection
import redis
r = redis.from_url("redis://localhost:6379/0")
r.ping()
```

---

## 🤖 Model-Related Problems

### Problem: "Ollama not responding"

**Solutions:**

1. **Check Ollama is running:**
```bash
curl http://localhost:11434/api/tags
# Should return JSON with models
```

2. **Start Ollama:**
```bash
ollama serve &
# Wait a few seconds
sleep 5
```

3. **Check Ollama logs:**
```bash
# Mac
tail -f ~/.ollama/logs/server.log

# Linux
journalctl -u ollama -f
```

4. **Reinstall Ollama:**
```bash
# Mac
brew reinstall ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh
```

5. **Pull models again:**
```bash
ollama pull mistral:latest
ollama pull llama2:latest
```

### Problem: "Model inference timeout"

**Solutions:**

1. **Increase timeout:**
```python
# In config
MODEL_TIMEOUT = 120  # Increase from 30

# Or in request
response = requests.post(url, timeout=120)
```

2. **Use smaller model:**
```bash
# Use 7B instead of 13B/70B
ollama pull llama2:7b
ollama pull mistral:7b
```

3. **Check system resources:**
```bash
# Check CPU/Memory
top  # or htop

# Check GPU (if using)
nvidia-smi
```

4. **Optimize model settings:**
```python
# Reduce context length
options = {
    "num_ctx": 2048,  # Reduce from 4096
    "num_thread": 4,   # Limit threads
    "num_gpu": 0       # Disable GPU if issues
}
```

### Problem: "API key invalid"

**Solutions:**

1. **Check environment variables:**
```bash
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
```

2. **Reload environment:**
```bash
source .env.real
# Or
export $(cat .env.real | xargs)
```

3. **Test API key:**
```python
import openai
openai.api_key = "your-key"
try:
    openai.Model.list()
    print("✅ API key valid")
except:
    print("❌ API key invalid")
```

---

## 💻 Frontend Issues

### Problem: "React app won't start"

**Solutions:**

1. **Check Node version:**
```bash
node --version
# Should be 18+ 

# Install correct version
nvm install 18
nvm use 18
```

2. **Clean install:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
npm start
```

3. **Check for port conflicts:**
```bash
# Default React port is 3000
lsof -i :3000
# Change port if needed
PORT=3001 npm start
```

4. **Fix permission issues:**
```bash
# Mac/Linux
sudo npm install -g npm@latest
# Or use npx
npx create-react-app --version
```

### Problem: "Module not found in React"

**Solutions:**

1. **Install missing module:**
```bash
npm install <module-name>
# For types
npm install @types/<module-name>
```

2. **Check imports:**
```javascript
// Wrong
import Component from 'component'
// Right
import Component from './components/Component'
```

3. **Clear webpack cache:**
```bash
rm -rf node_modules/.cache
npm start
```

### Problem: "CORS errors in browser"

**Solutions:**

1. **Fix Flask CORS:**
```python
# app/vulne_chat.py
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000'])
```

2. **Use proxy in React:**
```json
// frontend/package.json
{
  "proxy": "http://localhost:7000"
}
```

3. **Configure CORS headers:**
```python
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response
```

---

## 🧪 Benchmarking Failures

### Problem: "Garak benchmarks fail"

**Solutions:**

1. **Check Garak installation:**
```bash
pip show garak
# If not installed
pip install garak
```

2. **Run Garak directly:**
```bash
garak --model test --probes encoding
```

3. **Fix import issues:**
```python
# Add to Python path
import sys
sys.path.append('./benchmarking')
```

4. **Use verbose mode:**
```bash
python benchmarking/run_garak.py --verbose --debug
```

### Problem: "NeMo Guardrails not working"

**Solutions:**

1. **Check configuration:**
```yaml
# config_NeMo/config.yml
models:
  - type: main
    engine: openai
    model: gpt-3.5-turbo
```

2. **Test NeMo directly:**
```python
from nemoguardrails import RailsConfig, LLMRails

config = RailsConfig.from_path("./config_NeMo")
rails = LLMRails(config)
response = rails.generate(messages=[{"role": "user", "content": "Hello"}])
print(response)
```

3. **Check action registration:**
```python
# config_NeMo/actions.py
def init(app):
    @app.action("check_vulnerability")
    def check_vulnerability(context):
        return {"vulnerable": False}
```

### Problem: "Benchmarks run forever"

**Solutions:**

1. **Add timeouts:**
```python
# Set global timeout
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Benchmark timeout")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(300)  # 5 minute timeout
```

2. **Limit probe count:**
```bash
python benchmarking/run_all_benchmarks.py \
  --max-probes 10 \
  --quick-mode
```

3. **Use parallel execution:**
```python
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(run_test, probe) for probe in probes[:10]]
```

---

## 🐳 Docker & Container Issues

### Problem: "Docker build fails"

**Solutions:**

1. **Clean Docker system:**
```bash
docker system prune -a --volumes
docker builder prune
```

2. **Build with no cache:**
```bash
docker build --no-cache -t vulne-chatbot .
```

3. **Fix permission issues:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

4. **Use BuildKit:**
```bash
DOCKER_BUILDKIT=1 docker build -t vulne-chatbot .
```

5. **Debug build:**
```bash
# Build with verbose output
docker build --progress=plain -t vulne-chatbot .
```

### Problem: "Container exits immediately"

**Solutions:**

1. **Check logs:**
```bash
docker logs vulne-chatbot
docker logs --tail 50 -f vulne-chatbot
```

2. **Run interactively:**
```bash
docker run -it vulne-chatbot /bin/bash
# Then manually run the app
python app/vulne_chat.py
```

3. **Check entrypoint:**
```dockerfile
# Dockerfile
ENTRYPOINT ["python"]
CMD ["app/vulne_chat.py"]
```

4. **Keep container running:**
```bash
docker run -d vulne-chatbot tail -f /dev/null
docker exec -it <container_id> bash
```

### Problem: "Can't connect to container"

**Solutions:**

1. **Check port mapping:**
```bash
docker ps
# Look for port mapping like 0.0.0.0:7000->7000/tcp

# If missing, run with -p
docker run -p 7000:7000 vulne-chatbot
```

2. **Check container network:**
```bash
docker network ls
docker inspect vulne-chatbot | grep IPAddress
```

3. **Use host network:**
```bash
docker run --network host vulne-chatbot
```

---

## 🌐 Network & API Problems

### Problem: "Connection refused"

**Solutions:**

1. **Check service is running:**
```bash
# Check if app is listening
netstat -an | grep 7000
ss -tlnp | grep 7000  # Linux
```

2. **Check firewall:**
```bash
# Mac
sudo pfctl -d  # Disable firewall temporarily

# Linux
sudo ufw status
sudo ufw allow 7000

# Windows
netsh advfirewall firewall add rule name="Vulne" dir=in action=allow protocol=TCP localport=7000
```

3. **Use localhost instead of 127.0.0.1:**
```python
# Sometimes helps with IPv6 issues
app.run(host='0.0.0.0', port=7000)
```

### Problem: "SSL/TLS errors"

**Solutions:**

1. **Disable SSL verification (dev only):**
```python
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Or in requests
response = requests.get(url, verify=False)
```

2. **Update certificates:**
```bash
# Mac
brew install ca-certificates

# Linux
sudo apt-get update && sudo apt-get install ca-certificates

# Python
pip install --upgrade certifi
```

3. **Use HTTP instead:**
```python
# Change URLs from https:// to http://
url = "http://localhost:7000"
```

### Problem: "Rate limiting errors"

**Solutions:**

1. **Add delays:**
```python
import time
for probe in probes:
    response = test_probe(probe)
    time.sleep(1)  # 1 second delay
```

2. **Implement exponential backoff:**
```python
import time
import random

def retry_with_backoff(func, max_retries=5):
    for i in range(max_retries):
        try:
            return func()
        except RateLimitError:
            wait_time = (2 ** i) + random.uniform(0, 1)
            time.sleep(wait_time)
    raise Exception("Max retries exceeded")
```

3. **Use connection pooling:**
```python
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
```

---

## 🗄️ Database Issues

### Problem: "Database connection failed"

**Solutions:**

1. **Check PostgreSQL is running:**
```bash
# Check status
sudo systemctl status postgresql
pg_isready

# Start if needed
sudo systemctl start postgresql
```

2. **Fix connection string:**
```bash
# Test connection
psql postgresql://user:pass@localhost:5432/vulne_db

# Common formats
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
DATABASE_URL=postgres://user:pass@localhost:5432/dbname
DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/dbname
```

3. **Create database:**
```bash
createdb vulne_db
# Or
psql -U postgres -c "CREATE DATABASE vulne_db;"
```

4. **Fix permissions:**
```bash
# Edit pg_hba.conf
sudo nano /etc/postgresql/14/main/pg_hba.conf
# Change "peer" to "md5" for local connections
sudo systemctl restart postgresql
```

### Problem: "Migration errors"

**Solutions:**

1. **Reset migrations:**
```bash
# Remove migration files
rm -rf migrations/

# Reinitialize
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

2. **Fix migration conflicts:**
```bash
# Stamp current version
flask db stamp head

# Create new migration
flask db migrate
flask db upgrade
```

3. **Manual fix:**
```sql
-- Connect to database
psql vulne_db

-- Check current schema
\dt

-- Drop and recreate tables if needed
DROP TABLE IF EXISTS alembic_version CASCADE;
```

---

## ⚡ Performance Problems

### Problem: "Tests running very slowly"

**Solutions:**

1. **Profile the code:**
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# Your code here
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

2. **Use caching:**
```python
from functools import lru_cache
import joblib

# Memory cache
@lru_cache(maxsize=1000)
def expensive_function(param):
    return result

# Disk cache
@joblib.Memory("./cache").cache
def expensive_function(param):
    return result
```

3. **Optimize database queries:**
```python
# Bad - N+1 problem
for item in items:
    related = db.query(Related).filter_by(item_id=item.id).all()

# Good - eager loading
items = db.query(Item).options(joinedload(Item.related)).all()
```

4. **Use async operations:**
```python
import asyncio
import aiohttp

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

### Problem: "Out of memory"

**Solutions:**

1. **Monitor memory usage:**
```python
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB")
```

2. **Process in batches:**
```python
def process_in_batches(items, batch_size=100):
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        process_batch(batch)
        gc.collect()  # Force garbage collection
```

3. **Use generators:**
```python
# Bad - loads all in memory
data = [process(item) for item in huge_list]

# Good - generator
data = (process(item) for item in huge_list)
```

4. **Limit model context:**
```python
# Reduce context window
model_config = {
    "max_tokens": 1000,  # Reduce from 4000
    "max_context": 2048  # Reduce from 8192
}
```

---

## 🔒 Security & Permission Errors

### Problem: "Permission denied"

**Solutions:**

1. **Fix file permissions:**
```bash
# Make scripts executable
chmod +x scripts/*.py

# Fix ownership
sudo chown -R $USER:$USER .

# Standard permissions
find . -type f -exec chmod 644 {} \;
find . -type d -exec chmod 755 {} \;
```

2. **Run with sudo (carefully):**
```bash
# Only if absolutely necessary
sudo python app/vulne_chat.py

# Better: fix the specific permission
sudo chown $USER /path/to/problem/file
```

3. **Check SELinux/AppArmor:**
```bash
# Temporarily disable SELinux (RHEL/CentOS)
sudo setenforce 0

# Check AppArmor (Ubuntu)
sudo aa-status
```

### Problem: "SSL certificate verification failed"

**Solutions:**

1. **Update certificates:**
```bash
# Update system certificates
sudo update-ca-certificates  # Debian/Ubuntu
sudo update-ca-trust  # RHEL/CentOS

# Python certificates
pip install --upgrade certifi
```

2. **Set certificate bundle:**
```python
import os
import certifi

os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
```

3. **Corporate proxy issues:**
```bash
# Set proxy with auth
export HTTPS_PROXY=http://user:pass@proxy.company.com:8080
export HTTP_PROXY=http://user:pass@proxy.company.com:8080
export NO_PROXY=localhost,127.0.0.1

# For pip
pip config set global.proxy http://user:pass@proxy.company.com:8080
```

---

## 🔄 CI/CD Pipeline Failures

### Problem: "GitHub Actions workflow failing"

**Solutions:**

1. **Check workflow syntax:**
```bash
# Validate locally
act --dryrun  # Using act tool

# Or online
# Go to https://github.com/your/repo/actions
# Check syntax errors in workflow file
```

2. **Debug workflow:**
```yaml
# Add debug steps
- name: Debug
  run: |
    echo "Current directory: $(pwd)"
    echo "Files: $(ls -la)"
    echo "Python version: $(python --version)"
    echo "Env vars: $(env | sort)"
```

3. **Check secrets:**
```yaml
# Make sure secrets are set
- name: Check secrets
  run: |
    if [ -z "${{ secrets.API_KEY }}" ]; then
      echo "API_KEY secret not set"
      exit 1
    fi
```

4. **Use matrix strategy for debugging:**
```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    python: [3.9, 3.10, 3.11]
  fail-fast: false  # Don't stop on first failure
```

### Problem: "Docker build fails in CI"

**Solutions:**

1. **Use multi-stage builds:**
```dockerfile
# Dockerfile
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
```

2. **Cache Docker layers:**
```yaml
# GitHub Actions
- uses: docker/setup-buildx-action@v2
- uses: docker/build-push-action@v4
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

3. **Debug with tmate:**
```yaml
# Add debugging session
- name: Debug with tmate
  if: ${{ failure() }}
  uses: mxschmitt/action-tmate@v3
```

---

## 🚑 Emergency Recovery

### When Everything is Broken

**Complete Reset Procedure:**

```bash
#!/bin/bash
# emergency_reset.sh

echo "🚨 Starting Emergency Reset..."

# 1. Stop all services
echo "Stopping services..."
pkill -f vulne_chat
pkill -f ollama
docker stop $(docker ps -q) 2>/dev/null

# 2. Clean Python environment
echo "Cleaning Python environment..."
deactivate 2>/dev/null
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# 3. Clean Node environment
echo "Cleaning Node environment..."
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
cd ..

# 4. Clean Docker
echo "Cleaning Docker..."
docker system prune -a --volumes -f

# 5. Clean temporary files
echo "Cleaning temporary files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name ".DS_Store" -delete
rm -rf .pytest_cache
rm -rf .coverage
rm -rf htmlcov
rm -rf results/*

# 6. Reinstall dependencies
echo "Reinstalling dependencies..."
pip install -r requirements.txt
pip install -e benchmarking/
cd frontend && npm install && cd ..

# 7. Reset configuration
echo "Resetting configuration..."
cp .env.example .env.real
echo "⚠️  Please edit .env.real with your settings"

# 8. Test basic functionality
echo "Testing basic functionality..."
python -c "import flask; print('✅ Flask OK')"
python -c "import numpy; print('✅ NumPy OK')"
python -c "import pandas; print('✅ Pandas OK')"

echo "✅ Emergency reset complete!"
echo "Next steps:"
echo "1. Edit .env.real with your configuration"
echo "2. Start Ollama: ollama serve"
echo "3. Pull models: ollama pull mistral:latest"
echo "4. Start app: python app/vulne_chat.py"
echo "5. Start frontend: cd frontend && npm start"
```

### Diagnostic Script

```python
#!/usr/bin/env python3
# diagnose.py - Run this to check system status

import sys
import subprocess
import os
import json
import socket
import importlib.util

def check_python():
    print(f"Python version: {sys.version}")
    return sys.version_info >= (3, 9)

def check_module(name):
    spec = importlib.util.find_spec(name)
    return spec is not None

def check_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def check_command(cmd):
    try:
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
        return True
    except:
        return False

def run_diagnostics():
    print("🔍 Running System Diagnostics...\n")
    
    issues = []
    
    # Python version
    if check_python():
        print("✅ Python version OK")
    else:
        print("❌ Python version too old (need 3.9+)")
        issues.append("Update Python to 3.9+")
    
    # Required modules
    modules = ['flask', 'numpy', 'pandas', 'requests', 'aiohttp']
    for module in modules:
        if check_module(module):
            print(f"✅ {module} installed")
        else:
            print(f"❌ {module} not installed")
            issues.append(f"pip install {module}")
    
    # Services
    services = {
        7000: "Flask app",
        3000: "React frontend",
        11434: "Ollama",
        6379: "Redis",
        5432: "PostgreSQL"
    }
    
    for port, service in services.items():
        if check_port(port):
            print(f"✅ {service} running on port {port}")
        else:
            print(f"⚠️  {service} not running on port {port}")
    
    # Commands
    commands = {
        'docker --version': 'Docker',
        'node --version': 'Node.js',
        'npm --version': 'npm',
        'ollama --version': 'Ollama'
    }
    
    for cmd, name in commands.items():
        if check_command(cmd):
            print(f"✅ {name} available")
        else:
            print(f"⚠️  {name} not available")
    
    # Environment variables
    env_vars = ['OPENAI_API_KEY', 'FLASK_SECRET_KEY', 'DATABASE_URL']
    for var in env_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"⚠️  {var} not set")
    
    # File checks
    required_files = [
        'app/vulne_chat.py',
        'requirements.txt',
        '.env.real',
        'frontend/package.json'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            issues.append(f"Create {file}")
    
    print("\n" + "="*50)
    if issues:
        print("❌ Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ All systems operational!")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = run_diagnostics()
    sys.exit(0 if success else 1)
```

### Quick Fixes Cheatsheet

```bash
# Flask won't start
export FLASK_APP=app/vulne_chat.py
export FLASK_ENV=development
flask run --port 7000

# Ollama issues
ollama serve &
sleep 5
ollama list

# Permission denied
chmod +x scripts/*.py
sudo chown -R $USER:$USER .

# Port in use
lsof -ti:7000 | xargs kill -9

# Module not found
pip install -e .
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Docker issues
docker system prune -a
docker-compose down
docker-compose up --build

# Frontend won't build
cd frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps

# Database connection
psql -U postgres -c "CREATE DATABASE vulne_db;"
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/vulne_db"

# Redis not working
docker run -d -p 6379:6379 redis:alpine

# Git issues
git stash
git pull --rebase
git stash pop

# Memory issues
echo 1 > /proc/sys/vm/drop_caches  # Linux only, needs sudo
ulimit -n 4096  # Increase file descriptors

# SSL/Certificate issues
export PYTHONHTTPSVERIFY=0
export SSL_VERIFY=false
```

---

## 📞 Getting Help

If you're still stuck after trying these solutions:

1. **Collect diagnostic information:**
```bash
python diagnose.py > diagnostics.txt 2>&1
```

2. **Create detailed issue report:**
   - OS and version
   - Python version
   - Error messages (full traceback)
   - Steps to reproduce
   - What you've already tried

3. **Check logs:**
```bash
# Collect all logs
tar -czf logs.tar.gz \
  logs/ \
  *.log \
  frontend/npm-debug.log \
  ~/.ollama/logs/
```

4. **Community resources:**
   - GitHub Issues: [Report Issue](https://github.com/yourusername/Vulne_Chatbot/issues)
   - Discord: [Join Community](https://discord.gg/vulnechat)
   - Stack Overflow: Tag with `vulne-chatbot`

Remember: Most issues are common and have simple solutions. Take a break, then try again with fresh eyes!
