#!/usr/bin/env python3
"""
Nubot Setup Script
Installs dependencies and sets up the Nubot system
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

class NubotSetup:
    def __init__(self):
        self.system = platform.system().lower()
        self.is_raspberry_pi = self._detect_raspberry_pi()
        self.project_root = Path(__file__).parent
        
    def _detect_raspberry_pi(self):
        """Detect if running on Raspberry Pi"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                return 'Raspberry Pi' in f.read()
        except:
            return False
    
    def log(self, message, level="INFO"):
        """Log setup messages"""
        levels = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌"
        }
        print(f"{levels.get(level, 'ℹ️')} {message}")
    
    def run_command(self, command, description=""):
        """Run a system command"""
        try:
            self.log(f"Running: {description or command}")
            result = subprocess.run(command, shell=True, check=True, 
                                 capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {e}", "ERROR")
            if e.stderr:
                print(f"Error: {e.stderr}")
            return False
    
    def install_system_dependencies(self):
        """Install system-level dependencies"""
        self.log("Installing system dependencies...")
        
        if self.system == "linux":
            if self.is_raspberry_pi:
                # Raspberry Pi specific packages
                commands = [
                    "sudo apt update",
                    "sudo apt install -y python3-pip python3-venv espeak espeak-data",
                    "sudo apt install -y portaudio19-dev python3-pyaudio",
                    "sudo apt install -y libasound2-dev",
                    "sudo apt install -y git"
                ]
            else:
                # General Linux packages
                commands = [
                    "sudo apt update",
                    "sudo apt install -y python3-pip python3-venv espeak espeak-data",
                    "sudo apt install -y portaudio19-dev python3-pyaudio",
                    "sudo apt install -y libasound2-dev"
                ]
        elif self.system == "darwin":  # macOS
            commands = [
                "brew install espeak",
                "brew install portaudio"
            ]
        elif self.system == "windows":
            self.log("Windows detected - please install espeak manually", "WARNING")
            return True
        else:
            self.log(f"Unsupported system: {self.system}", "ERROR")
            return False
        
        for command in commands:
            if not self.run_command(command):
                return False
        
        return True
    
    def create_virtual_environment(self):
        """Create Python virtual environment"""
        self.log("Creating virtual environment...")
        
        venv_path = self.project_root / "venv"
        if venv_path.exists():
            self.log("Virtual environment already exists", "WARNING")
            return True
        
        if not self.run_command(f"python3 -m venv {venv_path}", "Creating virtual environment"):
            return False
        
        self.log("Virtual environment created successfully", "SUCCESS")
        return True
    
    def install_python_dependencies(self):
        """Install Python dependencies"""
        self.log("Installing Python dependencies...")
        
        venv_python = self.project_root / "venv" / "bin" / "python"
        if self.system == "windows":
            venv_python = self.project_root / "venv" / "Scripts" / "python.exe"
        
        if not venv_python.exists():
            self.log("Virtual environment not found. Please run setup again.", "ERROR")
            return False
        
        # Upgrade pip first
        if not self.run_command(f"{venv_python} -m pip install --upgrade pip", "Upgrading pip"):
            return False
        
        # Install requirements
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            self.log("requirements.txt not found", "ERROR")
            return False
        
        if not self.run_command(f"{venv_python} -m pip install -r {requirements_file}", 
                              "Installing Python packages"):
            return False
        
        self.log("Python dependencies installed successfully", "SUCCESS")
        return True
    
    def setup_environment_file(self):
        """Setup environment configuration"""
        self.log("Setting up environment configuration...")
        
        env_example = self.project_root / "env_example.txt"
        env_file = self.project_root / ".env"
        
        if env_file.exists():
            self.log(".env file already exists", "WARNING")
            return True
        
        if not env_example.exists():
            self.log("env_example.txt not found", "ERROR")
            return False
        
        # Copy example to .env
        shutil.copy(env_example, env_file)
        self.log("Environment file created. Please edit .env with your API keys.", "SUCCESS")
        return True
    
    def setup_directories(self):
        """Create necessary directories"""
        self.log("Creating necessary directories...")
        
        directories = [
            "static",
            "static/sounds",
            "static/videos",
            "logs",
            "data"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(exist_ok=True)
        
        self.log("Directories created successfully", "SUCCESS")
        return True
    
    def setup_raspberry_pi(self):
        """Setup Raspberry Pi specific configurations"""
        if not self.is_raspberry_pi:
            return True
        
        self.log("Setting up Raspberry Pi specific configurations...")
        
        # Enable GPIO
        if not self.run_command("sudo usermod -a -G gpio $USER", "Adding user to gpio group"):
            return False
        
        # Setup audio
        if not self.run_command("sudo usermod -a -G audio $USER", "Adding user to audio group"):
            return False
        
        self.log("Raspberry Pi setup completed", "SUCCESS")
        return True
    
    def create_startup_script(self):
        """Create startup script"""
        self.log("Creating startup script...")
        
        if self.system == "windows":
            script_content = """@echo off
cd /d "%~dp0"
venv\\Scripts\\python.exe app.py
pause
"""
            script_file = self.project_root / "start_nubot.bat"
        else:
            script_content = """#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python app.py
"""
            script_file = self.project_root / "start_nubot.sh"
        
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        if self.system != "windows":
            os.chmod(script_file, 0o755)
        
        self.log(f"Startup script created: {script_file}", "SUCCESS")
        return True
    
    def run_setup(self):
        """Run complete setup"""
        self.log("🤖 Starting Nubot Setup...")
        self.log(f"System: {self.system}")
        self.log(f"Raspberry Pi: {self.is_raspberry_pi}")
        print("=" * 50)
        
        steps = [
            ("Installing system dependencies", self.install_system_dependencies),
            ("Creating virtual environment", self.create_virtual_environment),
            ("Installing Python dependencies", self.install_python_dependencies),
            ("Setting up environment file", self.setup_environment_file),
            ("Creating directories", self.setup_directories),
            ("Setting up Raspberry Pi", self.setup_raspberry_pi),
            ("Creating startup script", self.create_startup_script)
        ]
        
        for step_name, step_func in steps:
            self.log(f"Step: {step_name}")
            if not step_func():
                self.log(f"Setup failed at: {step_name}", "ERROR")
                return False
            print()
        
        self.log("🎉 Setup completed successfully!", "SUCCESS")
        self.log("Next steps:")
        self.log("1. Edit .env file with your OpenAI API key")
        self.log("2. Run: python test_system.py (to test the system)")
        self.log("3. Run: python app.py (to start the server)")
        if self.system != "windows":
            self.log("4. Or run: ./start_nubot.sh")
        
        return True


def main():
    """Main function"""
    setup = NubotSetup()
    success = setup.run_setup()
    
    if success:
        print("\n✅ Setup completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Setup failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
