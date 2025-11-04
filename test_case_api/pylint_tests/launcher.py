#!/usr/bin/env python3
"""
Pylint Test Results Launcher
Opens the latest pylint report in the default browser
"""

import os
import sys
import webbrowser
from pathlib import Path
from datetime import datetime


def find_latest_report():
    """Find the most recent HTML report"""
    results_dir = Path(__file__).parent / "results"
    
    if not results_dir.exists():
        print("❌ Results directory not found. Run pylint tests first.")
        return None
    
    # Find all HTML reports
    html_reports = list(results_dir.glob("pylint_report_*.html"))
    
    if not html_reports:
        print("❌ No HTML reports found. Run 'python run_pylint_tests.py' first.")
        return None
    
    # Get the newest report
    latest_report = max(html_reports, key=lambda p: p.stat().st_mtime)
    return latest_report


def open_report(report_path: Path):
    """Open the report in the default browser"""
    try:
        file_url = f"file:///{report_path.absolute().as_posix()}"
        webbrowser.open(file_url)
        print(f"✅ Opened report: {report_path.name}")
        return True
    except Exception as e:
        print(f"❌ Failed to open report: {e}")
        print(f"   Manual path: {report_path.absolute()}")
        return False


def list_all_reports():
    """List all available reports"""
    results_dir = Path(__file__).parent / "results"
    
    if not results_dir.exists():
        print("❌ Results directory not found.")
        return
    
    html_reports = list(results_dir.glob("pylint_report_*.html"))
    json_reports = list(results_dir.glob("pylint_results_*.json"))
    
    if not html_reports and not json_reports:
        print("📭 No reports found. Run tests first:")
        print("   python run_pylint_tests.py")
        return
    
    print("📊 Available Reports:")
    print("=" * 50)
    
    if html_reports:
        print("🌐 HTML Reports:")
        for report in sorted(html_reports, key=lambda p: p.stat().st_mtime, reverse=True):
            timestamp = datetime.fromtimestamp(report.stat().st_mtime)
            size_kb = report.stat().st_size // 1024
            print(f"   📄 {report.name}")
            print(f"      Created: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"      Size: {size_kb} KB")
            print()
    
    if json_reports:
        print("📋 JSON Reports:")
        for report in sorted(json_reports, key=lambda p: p.stat().st_mtime, reverse=True):
            timestamp = datetime.fromtimestamp(report.stat().st_mtime)
            size_kb = report.stat().st_size // 1024
            print(f"   📄 {report.name}")
            print(f"      Created: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"      Size: {size_kb} KB")
            print()


def main():
    """Main launcher function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "list":
            list_all_reports()
            return
        elif command == "help":
            print("🚀 Pylint Test Results Launcher")
            print("Usage:")
            print("   python launcher.py          # Open latest HTML report")
            print("   python launcher.py list     # List all reports")
            print("   python launcher.py help     # Show this help")
            return
    
    # Default: Open latest report
    print("🚀 Pylint Test Results Launcher")
    
    latest_report = find_latest_report()
    if latest_report:
        print(f"📊 Latest report: {latest_report.name}")
        open_report(latest_report)
    else:
        print("\n💡 To generate a new report:")
        print("   python run_pylint_tests.py")


if __name__ == "__main__":
    main()