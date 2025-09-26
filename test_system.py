#!/usr/bin/env python3
"""
Nubot System Testing Script
Tests all major components of the Nubot system
"""

import requests
import time
import json
import os
import sys
from datetime import datetime

class NubotTester:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.test_results = []
        self.start_time = datetime.now()
    
    def log_test(self, test_name, success, message="", duration=0):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if duration > 0:
            print(f"    Duration: {duration:.2f}s")
    
    def test_server_connection(self):
        """Test if server is running"""
        try:
            start = time.time()
            response = requests.get(f"{self.base_url}/", timeout=5)
            duration = time.time() - start
            
            if response.status_code == 200:
                self.log_test("Server Connection", True, "Server is running", duration)
                return True
            else:
                self.log_test("Server Connection", False, f"HTTP {response.status_code}", duration)
                return False
        except Exception as e:
            self.log_test("Server Connection", False, str(e))
            return False
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        endpoints = [
            ("/api/status", "GET"),
            ("/api/notifications", "GET"),
            ("/api/test-led", "GET"),
        ]
        
        for endpoint, method in endpoints:
            try:
                start = time.time()
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                else:
                    response = requests.post(f"{self.base_url}{endpoint}", timeout=5)
                
                duration = time.time() - start
                
                if response.status_code == 200:
                    self.log_test(f"API {endpoint}", True, "Endpoint accessible", duration)
                else:
                    self.log_test(f"API {endpoint}", False, f"HTTP {response.status_code}", duration)
                    
            except Exception as e:
                self.log_test(f"API {endpoint}", False, str(e))
    
    def test_voice_response(self):
        """Test voice response system"""
        test_messages = [
            "Hello Nubot",
            "I want to play a game",
            "I'm feeling sad",
            "Tell me a story"
        ]
        
        for message in test_messages:
            try:
                start = time.time()
                response = requests.post(
                    f"{self.base_url}/get_response",
                    json={"text": message, "lang": "en"},
                    timeout=10
                )
                duration = time.time() - start
                
                if response.status_code == 200:
                    data = response.json()
                    if "text" in data and data["text"]:
                        self.log_test(f"Voice Response: '{message}'", True, 
                                    f"Response: {data['text'][:50]}...", duration)
                    else:
                        self.log_test(f"Voice Response: '{message}'", False, 
                                    "No response text", duration)
                else:
                    self.log_test(f"Voice Response: '{message}'", False, 
                                f"HTTP {response.status_code}", duration)
                    
            except Exception as e:
                self.log_test(f"Voice Response: '{message}'", False, str(e))
    
    def test_game_routing(self):
        """Test game routing functionality"""
        game_requests = [
            ("I want to play guess the animal", "/games/guess-animal"),
            ("Let's play tic tac toe", "/games/tic-tac-toe"),
            ("I want to do magic math", "/games/magic-math"),
            ("Tell me a story", "/games/story-spinner")
        ]
        
        for message, expected_redirect in game_requests:
            try:
                start = time.time()
                response = requests.post(
                    f"{self.base_url}/get_response",
                    json={"text": message, "lang": "en"},
                    timeout=10
                )
                duration = time.time() - start
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("redirect") == expected_redirect:
                        self.log_test(f"Game Routing: '{message}'", True, 
                                    f"Correctly routed to {expected_redirect}", duration)
                    else:
                        self.log_test(f"Game Routing: '{message}'", False, 
                                    f"Expected {expected_redirect}, got {data.get('redirect')}", duration)
                else:
                    self.log_test(f"Game Routing: '{message}'", False, 
                                f"HTTP {response.status_code}", duration)
                    
            except Exception as e:
                self.log_test(f"Game Routing: '{message}'", False, str(e))
    
    def test_emotion_detection(self):
        """Test emotion detection and LED control"""
        emotion_tests = [
            ("I'm so happy!", "happy"),
            ("I feel sad", "sad"),
            ("I'm angry", "angry"),
            ("Wow, that's amazing!", "surprise")
        ]
        
        for message, expected_emotion in emotion_tests:
            try:
                start = time.time()
                response = requests.post(
                    f"{self.base_url}/get_response",
                    json={"text": message, "lang": "en"},
                    timeout=10
                )
                duration = time.time() - start
                
                if response.status_code == 200:
                    data = response.json()
                    detected_emotion = data.get("emotion", "unknown")
                    if detected_emotion == expected_emotion:
                        self.log_test(f"Emotion Detection: '{message}'", True, 
                                    f"Correctly detected {expected_emotion}", duration)
                    else:
                        self.log_test(f"Emotion Detection: '{message}'", False, 
                                    f"Expected {expected_emotion}, got {detected_emotion}", duration)
                else:
                    self.log_test(f"Emotion Detection: '{message}'", False, 
                                f"HTTP {response.status_code}", duration)
                    
            except Exception as e:
                self.log_test(f"Emotion Detection: '{message}'", False, str(e))
    
    def test_offline_mode(self):
        """Test offline mode functionality"""
        try:
            # Test offline mode toggle
            start = time.time()
            response = requests.post(
                f"{self.base_url}/api/offline-mode",
                json={"offline": True},
                timeout=5
            )
            duration = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                if data.get("offline_mode") == True:
                    self.log_test("Offline Mode Toggle", True, "Successfully enabled offline mode", duration)
                else:
                    self.log_test("Offline Mode Toggle", False, "Failed to enable offline mode", duration)
            else:
                self.log_test("Offline Mode Toggle", False, f"HTTP {response.status_code}", duration)
                
        except Exception as e:
            self.log_test("Offline Mode Toggle", False, str(e))
    
    def test_notification_system(self):
        """Test notification system"""
        try:
            # Get current notifications
            start = time.time()
            response = requests.get(f"{self.base_url}/api/notifications", timeout=5)
            duration = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Notification System", True, 
                            f"Retrieved {len(data)} notifications", duration)
            else:
                self.log_test("Notification System", False, f"HTTP {response.status_code}", duration)
                
        except Exception as e:
            self.log_test("Notification System", False, str(e))
    
    def run_all_tests(self):
        """Run all tests"""
        print("🤖 Starting Nubot System Tests...")
        print("=" * 50)
        
        # Test server connection first
        if not self.test_server_connection():
            print("\n❌ Server is not running. Please start the server first.")
            return False
        
        print("\n📡 Testing API Endpoints...")
        self.test_api_endpoints()
        
        print("\n🎤 Testing Voice Response System...")
        self.test_voice_response()
        
        print("\n🎮 Testing Game Routing...")
        self.test_game_routing()
        
        print("\n😊 Testing Emotion Detection...")
        self.test_emotion_detection()
        
        print("\n🔧 Testing Offline Mode...")
        self.test_offline_mode()
        
        print("\n🔔 Testing Notification System...")
        self.test_notification_system()
        
        # Generate summary
        self.generate_summary()
        return True
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        total_duration = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⏱️  Total Duration: {total_duration:.2f}s")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        # Save results to file
        with open("test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n💾 Detailed results saved to test_results.json")


def main():
    """Main function"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8080"
    
    tester = NubotTester(base_url)
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests completed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
