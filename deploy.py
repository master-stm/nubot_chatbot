#!/usr/bin/env python3
"""
Nubot Deployment Script
Handles production deployment and configuration
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path
from datetime import datetime

class NubotDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.deployment_config = {
            "production": {
                "host": "0.0.0.0",
                "port": 8080,
                "debug": False,
                "offline_mode": True
            },
            "development": {
                "host": "127.0.0.1", 
                "port": 8080,
                "debug": True,
                "offline_mode": False
            }
        }
    
    def log(self, message, level="INFO"):
        """Log deployment messages"""
        levels = {
            "INFO": "ℹ️",
            "SUCCESS": "✅", 
            "WARNING": "⚠️",
            "ERROR": "❌"
        }
        print(f"{levels.get(level, 'ℹ️')} {message}")
    
    def create_production_config(self):
        """Create production configuration"""
        self.log("Creating production configuration...")
        
        # Create production .env
        prod_env = {
            "FLASK_ENV": "production",
            "FLASK_DEBUG": "False",
            "PORT": "8080",
            "OFFLINE_MODE": "True",
            "NOTIFICATION_ENABLED": "True",
            "EMOTION_SENSITIVITY": "0.7"
        }
        
        env_content = "\n".join([f"{k}={v}" for k, v in prod_env.items()])
        with open(self.project_root / ".env.production", "w") as f:
            f.write(env_content)
        
        self.log("Production configuration created", "SUCCESS")
        return True
    
    def create_systemd_service(self):
        """Create systemd service for Raspberry Pi"""
        self.log("Creating systemd service...")
        
        service_content = f"""[Unit]
Description=Nubot Child-Friendly Robot
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory={self.project_root}
Environment=PATH={self.project_root}/venv/bin
ExecStart={self.project_root}/venv/bin/python {self.project_root}/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_file = self.project_root / "nubot.service"
        with open(service_file, "w") as f:
            f.write(service_content)
        
        self.log("Systemd service created", "SUCCESS")
        return True
    
    def create_startup_scripts(self):
        """Create startup scripts for different platforms"""
        self.log("Creating startup scripts...")
        
        # Linux/macOS startup script
        linux_script = f"""#!/bin/bash
cd "{self.project_root}"
source venv/bin/activate
export FLASK_ENV=production
python app.py
"""
        
        with open(self.project_root / "start_production.sh", "w") as f:
            f.write(linux_script)
        os.chmod(self.project_root / "start_production.sh", 0o755)
        
        # Windows startup script
        windows_script = f"""@echo off
cd /d "{self.project_root}"
venv\\Scripts\\activate
set FLASK_ENV=production
python app.py
pause
"""
        
        with open(self.project_root / "start_production.bat", "w") as f:
            f.write(windows_script)
        
        self.log("Startup scripts created", "SUCCESS")
        return True
    
    def create_logging_config(self):
        """Create logging configuration"""
        self.log("Setting up logging...")
        
        logs_dir = self.project_root / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Create log rotation script
        logrotate_script = f"""#!/bin/bash
# Log rotation for Nubot
LOG_DIR="{logs_dir}"
MAX_SIZE="10M"
MAX_FILES=5

for log_file in $LOG_DIR/*.log; do
    if [ -f "$log_file" ]; then
        # Check file size
        size=$(stat -c%s "$log_file" 2>/dev/null || echo 0)
        if [ $size -gt 10485760 ]; then  # 10MB in bytes
            # Rotate log file
            mv "$log_file" "$log_file.old"
            touch "$log_file"
            
            # Keep only MAX_FILES old logs
            ls -t $LOG_DIR/*.old | tail -n +$((MAX_FILES + 1)) | xargs -r rm
        fi
    fi
done
"""
        
        with open(self.project_root / "rotate_logs.sh", "w") as f:
            f.write(logrotate_script)
        os.chmod(self.project_root / "rotate_logs.sh", 0o755)
        
        self.log("Logging configuration created", "SUCCESS")
        return True
    
    def create_backup_script(self):
        """Create backup script for data and configuration"""
        self.log("Creating backup script...")
        
        backup_script = f"""#!/bin/bash
# Nubot Backup Script
BACKUP_DIR="{self.project_root}/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="nubot_backup_$DATE.tar.gz"

mkdir -p $BACKUP_DIR

# Create backup
tar -czf "$BACKUP_DIR/$BACKUP_FILE" \\
    --exclude="venv" \\
    --exclude="__pycache__" \\
    --exclude="*.pyc" \\
    --exclude="logs/*.log" \\
    --exclude="static/response_*.mp3" \\
    --exclude="static/response_*.wav" \\
    "{self.project_root}"

echo "Backup created: $BACKUP_FILE"

# Keep only last 7 backups
cd $BACKUP_DIR
ls -t nubot_backup_*.tar.gz | tail -n +8 | xargs -r rm

echo "Backup completed"
"""
        
        with open(self.project_root / "backup.sh", "w") as f:
            f.write(backup_script)
        os.chmod(self.project_root / "backup.sh", 0o755)
        
        self.log("Backup script created", "SUCCESS")
        return True
    
    def create_health_check(self):
        """Create health check script"""
        self.log("Creating health check script...")
        
        health_script = f"""#!/bin/bash
# Nubot Health Check Script
URL="http://localhost:8080/api/status"
LOG_FILE="{self.project_root}/logs/health_check.log"

# Check if service is running
response=$(curl -s -o /dev/null -w "%{{http_code}}" $URL)

if [ $response -eq 200 ]; then
    echo "$(date): Service is healthy" >> $LOG_FILE
    exit 0
else
    echo "$(date): Service is unhealthy (HTTP $response)" >> $LOG_FILE
    exit 1
fi
"""
        
        with open(self.project_root / "health_check.sh", "w") as f:
            f.write(health_script)
        os.chmod(self.project_root / "health_check.sh", 0o755)
        
        self.log("Health check script created", "SUCCESS")
        return True
    
    def create_cron_jobs(self):
        """Create cron job configuration"""
        self.log("Creating cron job configuration...")
        
        cron_config = f"""# Nubot Cron Jobs
# Add these to crontab with: crontab -e

# Health check every 5 minutes
*/5 * * * * {self.project_root}/health_check.sh

# Log rotation daily at 2 AM
0 2 * * * {self.project_root}/rotate_logs.sh

# Backup daily at 3 AM
0 3 * * * {self.project_root}/backup.sh

# Restart service if unhealthy (every 10 minutes)
*/10 * * * * {self.project_root}/health_check.sh || systemctl restart nubot
"""
        
        with open(self.project_root / "cron_jobs.txt", "w") as f:
            f.write(cron_config)
        
        self.log("Cron job configuration created", "SUCCESS")
        return True
    
    def create_docker_config(self):
        """Create Docker configuration for containerized deployment"""
        self.log("Creating Docker configuration...")
        
        # Dockerfile
        dockerfile = """FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    espeak espeak-data \\
    portaudio19-dev \\
    libasound2-dev \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p static logs data

# Expose port
EXPOSE 8080

# Set environment variables
ENV FLASK_ENV=production
ENV OFFLINE_MODE=True

# Run application
CMD ["python", "app.py"]
"""
        
        with open(self.project_root / "Dockerfile", "w") as f:
            f.write(dockerfile)
        
        # Docker Compose
        docker_compose = """version: '3.8'

services:
  nubot:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
      - ./notifications.json:/app/notifications.json
    environment:
      - FLASK_ENV=production
      - OFFLINE_MODE=True
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/api/status"]
      interval: 30s
      timeout: 10s
      retries: 3
"""
        
        with open(self.project_root / "docker-compose.yml", "w") as f:
            f.write(docker_compose)
        
        self.log("Docker configuration created", "SUCCESS")
        return True
    
    def run_deployment(self, environment="production"):
        """Run complete deployment"""
        self.log(f"🚀 Starting Nubot Deployment ({environment})...")
        print("=" * 50)
        
        steps = [
            ("Creating production configuration", self.create_production_config),
            ("Creating systemd service", self.create_systemd_service),
            ("Creating startup scripts", self.create_startup_scripts),
            ("Setting up logging", self.create_logging_config),
            ("Creating backup script", self.create_backup_script),
            ("Creating health check", self.create_health_check),
            ("Creating cron jobs", self.create_cron_jobs),
            ("Creating Docker config", self.create_docker_config)
        ]
        
        for step_name, step_func in steps:
            self.log(f"Step: {step_name}")
            if not step_func():
                self.log(f"Deployment failed at: {step_name}", "ERROR")
                return False
            print()
        
        self.log("🎉 Deployment configuration completed!", "SUCCESS")
        self.log("Next steps:")
        self.log("1. Configure your .env file with production settings")
        self.log("2. Test the system: python test_system.py")
        self.log("3. Start production: ./start_production.sh")
        self.log("4. (Raspberry Pi) Install service: sudo cp nubot.service /etc/systemd/system/")
        self.log("5. (Raspberry Pi) Enable service: sudo systemctl enable nubot")
        self.log("6. (Docker) Deploy: docker-compose up -d")
        
        return True


def main():
    """Main function"""
    environment = sys.argv[1] if len(sys.argv) > 1 else "production"
    
    deployer = NubotDeployer()
    success = deployer.run_deployment(environment)
    
    if success:
        print("\n✅ Deployment completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Deployment failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
