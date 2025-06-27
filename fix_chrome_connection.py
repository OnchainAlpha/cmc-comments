#!/usr/bin/env python3
"""
Chrome Connection Fix Script
Resolves WinError 10061 and WebDriver connection issues
"""
import os
import psutil
import subprocess
import time
import sys

def kill_chrome_processes():
    """Kill all Chrome and ChromeDriver processes"""
    print("🔄 Killing existing Chrome processes...")
    
    processes_to_kill = ['chrome.exe', 'chromedriver.exe', 'msedgedriver.exe']
    killed_count = 0
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc_name = proc.info['name'].lower()
            if any(target in proc_name for target in processes_to_kill):
                print(f"   🗑️ Killing {proc.info['name']} (PID: {proc.info['pid']})")
                proc.kill()
                killed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    print(f"✅ Killed {killed_count} Chrome/WebDriver processes")
    time.sleep(2)  # Wait for processes to fully terminate

def clear_chrome_temp_data():
    """Clear Chrome temporary data that might cause issues"""
    print("🧹 Clearing Chrome temporary data...")
    
    temp_paths = [
        os.path.expanduser("~/AppData/Local/Temp"),
        os.path.expanduser("~/AppData/Local/Google/Chrome/User Data/Default/Cache"),
        os.path.expanduser("~/AppData/Local/Google/Chrome/User Data/SwReporter"),
    ]
    
    for temp_path in temp_paths:
        if os.path.exists(temp_path):
            try:
                for root, dirs, files in os.walk(temp_path):
                    for file in files:
                        if 'chrome' in file.lower() or 'webdriver' in file.lower():
                            try:
                                os.remove(os.path.join(root, file))
                            except:
                                pass
                print(f"   ✅ Cleaned: {temp_path}")
            except Exception as e:
                print(f"   ⚠️ Could not clean {temp_path}: {str(e)}")

def check_port_availability():
    """Check if common WebDriver ports are available"""
    print("🔍 Checking WebDriver port availability...")
    
    import socket
    common_ports = [9515, 9516, 9517, 9518, 9519]  # Common ChromeDriver ports
    
    available_ports = []
    for port in common_ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result != 0:  # Port is available
            available_ports.append(port)
            print(f"   ✅ Port {port}: Available")
        else:
            print(f"   ❌ Port {port}: In use")
    
    return available_ports

def test_chrome_startup():
    """Test if Chrome can start properly"""
    print("🧪 Testing Chrome startup...")
    
    try:
        # Try to start Chrome with minimal configuration
        chrome_cmd = [
            "chrome.exe",
            "--headless",
            "--no-sandbox", 
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--remote-debugging-port=9222",
            "--disable-extensions",
            "--disable-plugins"
        ]
        
        process = subprocess.Popen(chrome_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(3)
        
        if process.poll() is None:  # Process is still running
            process.terminate()
            print("   ✅ Chrome startup test: SUCCESS")
            return True
        else:
            print("   ❌ Chrome startup test: FAILED")
            return False
            
    except Exception as e:
        print(f"   ❌ Chrome startup test failed: {str(e)}")
        return False

def fix_chrome_permissions():
    """Fix Chrome permissions issues"""
    print("🔐 Checking Chrome permissions...")
    
    chrome_paths = [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        os.path.expanduser("~/AppData/Local/Google/Chrome/Application/chrome.exe")
    ]
    
    for chrome_path in chrome_paths:
        if os.path.exists(chrome_path):
            try:
                # Test if we can access the Chrome binary
                with open(chrome_path, 'rb') as f:
                    f.read(1024)  # Try to read first 1KB
                print(f"   ✅ Chrome binary accessible: {chrome_path}")
                return True
            except Exception as e:
                print(f"   ❌ Chrome binary access issue: {str(e)}")
    
    print("   ⚠️ No accessible Chrome binary found")
    return False

def main():
    print("🔧 CHROME CONNECTION FIX - COMPREHENSIVE REPAIR")
    print("="*70)
    print("Fixing WinError 10061 and WebDriver connection issues...")
    print("="*70)
    
    # Step 1: Kill existing processes
    kill_chrome_processes()
    
    # Step 2: Clear temporary data
    clear_chrome_temp_data()
    
    # Step 3: Check port availability
    available_ports = check_port_availability()
    
    # Step 4: Check Chrome permissions
    chrome_accessible = fix_chrome_permissions()
    
    # Step 5: Test Chrome startup
    chrome_starts = test_chrome_startup()
    
    # Final assessment
    print("\n" + "="*70)
    print("🏁 REPAIR RESULTS:")
    print("="*70)
    print(f"Available WebDriver ports: {len(available_ports)}")
    print(f"Chrome binary accessible: {'✅' if chrome_accessible else '❌'}")
    print(f"Chrome startup test: {'✅' if chrome_starts else '❌'}")
    
    if available_ports and chrome_accessible and chrome_starts:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Chrome connection issues should be resolved")
        print("🚀 You can now restart your CMC automation")
        
        print(f"\n💡 RECOMMENDED NEXT STEPS:")
        print(f"1. Run: python run_cmc_automation.py")
        print(f"2. Monitor for connection stability")
        print(f"3. If issues persist, restart your computer")
        
    else:
        print("\n⚠️ SOME ISSUES REMAIN:")
        if not available_ports:
            print("❌ No available WebDriver ports - restart computer")
        if not chrome_accessible:
            print("❌ Chrome binary issues - reinstall Chrome")
        if not chrome_starts:
            print("❌ Chrome startup issues - check antivirus/firewall")
    
    return available_ports and chrome_accessible and chrome_starts

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 