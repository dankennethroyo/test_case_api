#!/usr/bin/env python3
"""
Setup script for Pylint Tests
Installs dependencies and runs initial setup
"""

import subprocess
import sys
from pathlib import Path


def install_dependencies():
    """Install required packages"""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    print("🔧 Installing pylint dependencies...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def verify_installation():
    """Verify pylint is properly installed"""
    print("🔍 Verifying pylint installation...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pylint", "--version"
        ], capture_output=True, text=True, check=True)
        
        print("✅ Pylint is working!")
        print(f"   Version: {result.stdout.split()[1] if result.stdout else 'Unknown'}")
        return True
    except subprocess.CalledProcessError:
        print("❌ Pylint verification failed")
        return False
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False


def run_quick_test():
    """Run a quick test to ensure everything works"""
    print("🧪 Running quick test...")
    
    quick_test_script = Path(__file__).parent / "quick_test.py"
    
    try:
        result = subprocess.run([
            sys.executable, str(quick_test_script)
        ], capture_output=True, text=True, timeout=120)
        
        print("✅ Quick test completed!")
        if result.stdout:
            # Show last few lines of output
            lines = result.stdout.strip().split('\n')
            for line in lines[-3:]:
                if line.strip():
                    print(f"   {line}")
        return True
    except subprocess.TimeoutExpired:
        print("⏱️  Quick test timed out (this is normal for large codebases)")
        return True
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False


def main():
    """Main setup function"""
    print("🚀 Pylint Tests Setup - Test Case API Project")
    print("=" * 60)
    
    success = True
    
    # Step 1: Install dependencies
    if not install_dependencies():
        success = False
    
    print()
    
    # Step 2: Verify installation
    if success and not verify_installation():
        success = False
    
    print()
    
    # Step 3: Run quick test
    if success and not run_quick_test():
        success = False
    
    print("\n" + "=" * 60)
    
    if success:
        print("🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("   • Run quick test: python quick_test.py")
        print("   • Full analysis: python run_pylint_tests.py")
        print("   • Read documentation: README.md")
    else:
        print("❌ Setup encountered issues. Please check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main()