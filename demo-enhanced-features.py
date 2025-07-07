#!/usr/bin/env python3
"""
Demo script showing enhanced browser automation features
Demonstrates interactive prompting, file attachments, and auto-positioning
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

try:
    from enhanced_browser_interface import EnhancedBrowserInterface, WindowManager
    print("✅ Enhanced browser interface imported successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure enhanced-browser-interface.py is in the same directory")
    sys.exit(1)

async def demo_interactive_automation():
    """Demo interactive automation with prompting"""
    print("🎯 Demo: Interactive Browser Automation")
    print("=" * 50)
    
    # Initialize the enhanced interface
    interface = EnhancedBrowserInterface()
    
    if not interface.llm:
        print("❌ No Anthropic API key configured. Please set ANTHROPIC_API_KEY environment variable.")
        return
    
    # Demo command with interactive capabilities
    demo_command = """
    Go to a job search website like Indeed or LinkedIn Jobs.
    Search for 'Python developer' positions.
    When you find the search results, ask me which specific job I'd like to apply to.
    Wait for my response before proceeding.
    """
    
    print(f"🚀 Executing demo command: {demo_command}")
    print("💡 This will demonstrate interactive prompting during automation")
    print()
    
    try:
        result = await interface.execute_interactive_command(demo_command)
        print("✅ Demo completed!")
        print(f"Result: {result}")
    except Exception as e:
        print(f"❌ Demo failed: {e}")

def demo_file_management():
    """Demo file upload and context extraction"""
    print("📁 Demo: File Management and Context Extraction")
    print("=" * 50)
    
    # Initialize file manager
    interface = EnhancedBrowserInterface()
    file_manager = interface.file_manager
    
    # Create sample files for demo
    sample_files_dir = Path("demo_files")
    sample_files_dir.mkdir(exist_ok=True)
    
    # Create sample resume
    sample_resume = sample_files_dir / "sample_resume.txt"
    sample_resume.write_text("""
John Doe
Software Engineer

EXPERIENCE:
- 5 years Python development
- Full-stack web development
- Machine learning projects

SKILLS:
- Python, JavaScript, React
- Django, Flask, FastAPI
- PostgreSQL, MongoDB
- AWS, Docker, Kubernetes

EDUCATION:
- BS Computer Science, University of Technology
""")
    
    # Create sample cover letter
    sample_cover_letter = sample_files_dir / "sample_cover_letter.txt"
    sample_cover_letter.write_text("""
Dear Hiring Manager,

I am writing to express my interest in the Software Engineer position.
With 5 years of experience in Python development and full-stack web development,
I am confident I would be a valuable addition to your team.

My experience includes:
- Building scalable web applications using Django and React
- Implementing machine learning solutions for business problems
- Working with cloud infrastructure on AWS

I am excited about the opportunity to contribute to your team.

Best regards,
John Doe
""")
    
    print("📄 Created sample files:")
    print(f"   • Resume: {sample_resume}")
    print(f"   • Cover Letter: {sample_cover_letter}")
    print()
    
    # Process files
    print("🔄 Processing files...")
    resume_id = file_manager.save_file(str(sample_resume), "sample_resume.txt")
    cover_letter_id = file_manager.save_file(str(sample_cover_letter), "sample_cover_letter.txt")
    
    print(f"✅ Files processed:")
    print(f"   • Resume ID: {resume_id}")
    print(f"   • Cover Letter ID: {cover_letter_id}")
    print()
    
    # Show file list
    files = file_manager.list_files()
    print("📋 File List:")
    for file_info in files:
        print(f"   • {file_info['original_name']} ({file_info['size']} bytes)")
        print(f"     Content preview: {file_info['content'][:100]}...")
        print()
    
    # Show context
    context = file_manager.get_all_files_context()
    print("🎯 Generated Context:")
    print(context[:500] + "..." if len(context) > 500 else context)
    
    # Cleanup
    import shutil
    shutil.rmtree(sample_files_dir)
    print("🧹 Cleaned up demo files")

def demo_window_management():
    """Demo automatic window positioning"""
    print("🎪 Demo: Window Management and Auto-Positioning")
    print("=" * 50)
    
    print("🔄 Attempting to bring browser window to front and center...")
    
    try:
        WindowManager.bring_to_front_and_center()
        print("✅ Window management command executed")
        print("💡 If a browser window was open, it should now be in front and centered")
    except Exception as e:
        print(f"⚠️  Window management warning: {e}")
        print("💡 This feature requires system-specific tools (wmctrl on Linux, etc.)")

def demo_enhanced_commands():
    """Show examples of enhanced commands with file context"""
    print("💬 Demo: Enhanced Commands with File Context")
    print("=" * 50)
    
    enhanced_commands = [
        "Apply to software engineer jobs using my resume and cover letter",
        "Fill out a job application form with information from my resume",
        "Update my LinkedIn profile using details from my resume",
        "Search for jobs that match my skills from my resume",
        "Draft a personalized cover letter for a specific job posting"
    ]
    
    print("🎯 Example enhanced commands that use file context:")
    for i, command in enumerate(enhanced_commands, 1):
        print(f"   {i}. {command}")
    
    print()
    print("💡 These commands will:")
    print("   • Automatically reference uploaded resume/cover letter content")
    print("   • Pause for user input when clarification is needed")
    print("   • Position browser window for optimal viewing")
    print("   • Provide real-time feedback and screenshots")

def main():
    """Run all demos"""
    print("🤖 Enhanced Browser Automation - Feature Demos")
    print("=" * 60)
    print()
    
    # Check if API key is configured
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  No Anthropic API key found in environment variables")
        print("💡 Set ANTHROPIC_API_KEY to run interactive demos")
        print()
    
    print("🎯 Available Demos:")
    print("1. File Management and Context Extraction")
    print("2. Window Management and Auto-Positioning")
    print("3. Enhanced Commands Examples")
    print("4. Interactive Automation (requires API key)")
    print()
    
    choice = input("Enter demo number (1-4) or 'all' for all demos: ").strip()
    
    if choice == "1" or choice.lower() == "all":
        demo_file_management()
        print()
    
    if choice == "2" or choice.lower() == "all":
        demo_window_management()
        print()
    
    if choice == "3" or choice.lower() == "all":
        demo_enhanced_commands()
        print()
    
    if choice == "4" or choice.lower() == "all":
        if os.getenv("ANTHROPIC_API_KEY"):
            print("🚀 Starting interactive automation demo...")
            asyncio.run(demo_interactive_automation())
        else:
            print("❌ Cannot run interactive demo without API key")
    
    print()
    print("✅ Demo completed!")
    print("🚀 To start the full interface, run: python enhanced-browser-interface.py")

if __name__ == "__main__":
    main()
