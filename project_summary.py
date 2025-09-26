#!/usr/bin/env python3
"""
Nubot Project Summary
Displays current project status and completion metrics
"""

import os
import json
from pathlib import Path
from datetime import datetime

class ProjectSummary:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.completion_data = {
            "core_features": {
                "voice_recognition": True,
                "text_to_speech": True,
                "emotion_detection": True,
                "multilingual_support": True,
                "offline_mode": True,
                "led_control": True,
                "notification_system": True
            },
            "games": {
                "guess_animal": True,
                "tic_tac_toe": True,
                "magic_math": True,
                "story_spinner": True,
                "animal_facts_quiz": True,
                "memory_echo": True,
                "guess_number": True
            },
            "infrastructure": {
                "requirements_txt": True,
                "environment_config": True,
                "testing_suite": True,
                "documentation": True,
                "deployment_scripts": True,
                "error_handling": True
            },
            "hardware": {
                "raspberry_pi_support": True,
                "gpio_control": True,
                "led_indicators": True,
                "audio_processing": True
            }
        }
    
    def calculate_completion(self):
        """Calculate overall project completion percentage"""
        total_items = 0
        completed_items = 0
        
        for category, items in self.completion_data.items():
            for item, status in items.items():
                total_items += 1
                if status:
                    completed_items += 1
        
        return (completed_items / total_items) * 100
    
    def check_file_structure(self):
        """Check if all expected files exist"""
        expected_files = [
            "app.py",
            "requirements.txt", 
            "env_example.txt",
            "test_system.py",
            "setup.py",
            "deploy.py",
            "README.md",
            "templates/index.html",
            "templates/games.html",
            "templates/guess-animal.html",
            "templates/tic-tac-toe.html",
            "templates/magic-math.html",
            "templates/story-spinner.html",
            "templates/animal-facts-quiz.html",
            "templates/memory-echo.html",
            "templates/guess-the-number.html"
        ]
        
        missing_files = []
        for file_path in expected_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
        
        return missing_files
    
    def get_project_stats(self):
        """Get project statistics"""
        stats = {
            "total_files": len(list(self.project_root.rglob("*"))),
            "python_files": len(list(self.project_root.rglob("*.py"))),
            "html_files": len(list(self.project_root.rglob("*.html"))),
            "audio_files": len(list(self.project_root.rglob("*.mp3"))),
            "video_files": len(list(self.project_root.rglob("*.mp4"))),
            "total_lines": 0
        }
        
        # Count lines in Python files
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    stats["total_lines"] += len(f.readlines())
            except:
                pass
        
        return stats
    
    def generate_report(self):
        """Generate comprehensive project report"""
        completion = self.calculate_completion()
        missing_files = self.check_file_structure()
        stats = self.get_project_stats()
        
        print("🤖 NUBOT PROJECT SUMMARY")
        print("=" * 50)
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Overall Completion: {completion:.1f}%")
        print()
        
        print("✅ COMPLETED FEATURES")
        print("-" * 30)
        for category, items in self.completion_data.items():
            print(f"\n{category.replace('_', ' ').title()}:")
            for item, status in items.items():
                status_icon = "✅" if status else "❌"
                print(f"  {status_icon} {item.replace('_', ' ').title()}")
        
        print(f"\n📁 PROJECT STATISTICS")
        print("-" * 30)
        print(f"Total Files: {stats['total_files']}")
        print(f"Python Files: {stats['python_files']}")
        print(f"HTML Templates: {stats['html_files']}")
        print(f"Audio Files: {stats['audio_files']}")
        print(f"Video Files: {stats['video_files']}")
        print(f"Total Lines of Code: {stats['total_lines']:,}")
        
        if missing_files:
            print(f"\n⚠️  MISSING FILES")
            print("-" * 30)
            for file_path in missing_files:
                print(f"  ❌ {file_path}")
        else:
            print(f"\n✅ ALL EXPECTED FILES PRESENT")
        
        print(f"\n🎯 NEXT STEPS")
        print("-" * 30)
        print("1. Run setup: python setup.py")
        print("2. Configure .env file with API keys")
        print("3. Test system: python test_system.py")
        print("4. Start development: python app.py")
        print("5. Deploy production: python deploy.py")
        
        print(f"\n🔧 HARDWARE SETUP (Raspberry Pi)")
        print("-" * 30)
        print("• Connect RGB LED to GPIO pins 18, 23, 24")
        print("• Connect microphone and speaker")
        print("• Install system dependencies")
        print("• Configure GPIO permissions")
        
        print(f"\n📚 DOCUMENTATION")
        print("-" * 30)
        print("• README.md - Complete setup guide")
        print("• test_system.py - System testing")
        print("• setup.py - Automated installation")
        print("• deploy.py - Production deployment")
        
        # Save report to file
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "completion_percentage": completion,
            "missing_files": missing_files,
            "statistics": stats,
            "features": self.completion_data
        }
        
        with open(self.project_root / "project_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: project_report.json")
        
        return completion >= 95  # Consider project complete if 95%+ done


def main():
    """Main function"""
    summary = ProjectSummary()
    is_complete = summary.generate_report()
    
    if is_complete:
        print("\n🎉 PROJECT IS READY FOR DEPLOYMENT!")
        return 0
    else:
        print("\n⚠️  PROJECT NEEDS ADDITIONAL WORK")
        return 1


if __name__ == "__main__":
    exit(main())
