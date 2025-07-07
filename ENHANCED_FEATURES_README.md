# 🤖 Enhanced Browser Automation

Advanced browser automation with interactive prompting, file attachments, and intelligent context awareness.

## ✨ New Enhanced Features

### 💬 Interactive Prompting During Execution
- **Real-time user interaction**: The automation can pause and ask for your input during execution
- **Dynamic direction changes**: Alter the automation flow based on what you see happening
- **Smart decision points**: The AI will ask for guidance when it encounters ambiguous situations
- **Timeout protection**: Prompts automatically timeout after 5 minutes to prevent hanging

**Example Usage:**
```
Command: "Apply to software engineer jobs on LinkedIn"
AI: "I found 15 job listings. Which specific position would you like me to apply to?"
You: "Apply to the Senior Python Developer role at TechCorp"
AI: "Proceeding with application to TechCorp position..."
```

### 📁 File Attachment & Context Integration
- **Multi-format support**: Upload PDFs, Word docs, text files, and images
- **Intelligent content extraction**: Automatically extracts text from various file types
- **OCR for images**: Extracts text from screenshots and scanned documents
- **Natural language references**: Use phrases like "my resume" or "the cover letter"
- **Context-aware automation**: AI uses file content to fill forms and make decisions

**Supported File Types:**
- **Documents**: PDF, Word (.docx, .doc), Text (.txt, .md)
- **Images**: PNG, JPG, JPEG (with OCR text extraction)
- **Code**: Python, JavaScript, HTML, CSS files

**Example Usage:**
```
1. Upload your resume (resume.pdf) and cover letter (cover_letter.docx)
2. Command: "Apply to jobs using my resume and customize the cover letter"
3. AI automatically uses resume data to fill application forms
4. AI references cover letter content for personalized applications
```

### 🎯 Automatic Browser Positioning
- **Auto-focus**: Browser window automatically comes to front when automation starts
- **Smart positioning**: Centers browser window on screen for optimal viewing
- **Cross-platform support**: Works on Linux (wmctrl), macOS (AppleScript), and Windows
- **Non-intrusive**: Only activates when automation begins

### 🔄 Real-time Execution Monitoring
- **Live status updates**: See current execution state in real-time
- **Progress screenshots**: Automatic screenshots at key decision points
- **Session persistence**: Maintains state across multiple commands
- **Error recovery**: Smart retry logic with user notification

## 🚀 Quick Start

### 1. Installation
```bash
# Make setup script executable
chmod +x enhanced-setup.sh

# Run the enhanced setup
./enhanced-setup.sh
```

### 2. Configuration
The setup will prompt you for:
- **Anthropic API Key**: Get one from https://console.anthropic.com/
- **System dependencies**: Installs OCR and window management tools

### 3. Launch Interface
```bash
# Start the enhanced interface
cd ~/enhanced-browser-automation
./start_enhanced_automation.sh

# Or run directly
python enhanced_browser_interface.py
```

### 4. Access Web Interface
Open your browser to: http://127.0.0.1:7789

## 📖 Usage Guide

### Basic Automation
1. Enter your command in the main text area
2. Optionally provide credentials if needed
3. Click "🚀 Execute Interactive Command"
4. Monitor progress and respond to prompts as needed

### File Upload Workflow
1. Go to the "📁 File Management" tab
2. Upload your files (resume, cover letter, etc.)
3. Files are automatically processed and content extracted
4. Return to automation tab and reference files naturally in commands

### Interactive Prompting
1. Start any automation command
2. When the AI needs input, a prompt will appear in the "💬 Interactive Prompts" section
3. Type your response and click "📤 Send Response"
4. Automation continues with your guidance

## 🎯 Example Use Cases

### Job Application Automation
```
Files: Upload resume.pdf and cover_letter.docx
Command: "Go to LinkedIn Jobs, search for Python developer roles, and apply to the top 3 positions using my resume and customizing my cover letter for each"

The AI will:
- Search for jobs
- Ask which specific positions to target
- Use resume data to fill application forms
- Customize cover letter content for each application
- Ask for approval before submitting each application
```

### Profile Updates
```
Files: Upload updated_resume.pdf
Command: "Update my LinkedIn profile with the latest information from my resume"

The AI will:
- Extract skills, experience, and education from resume
- Navigate to LinkedIn profile edit pages
- Ask which sections to update
- Fill in new information
- Ask for confirmation before saving changes
```

### Form Filling
```
Files: Upload personal_info.txt, certificates.pdf
Command: "Fill out the job application form on this website using my personal information and certificates"

The AI will:
- Extract relevant data from uploaded files
- Identify form fields on the page
- Ask for clarification on ambiguous fields
- Fill forms with appropriate information
- Request review before submission
```

## ⚙️ Configuration Options

### Environment Variables
```bash
# API Configuration
ANTHROPIC_API_KEY=your_api_key_here

# Feature Toggles
ENABLE_INTERACTIVE_PROMPTS=true
ENABLE_FILE_ATTACHMENTS=true
ENABLE_AUTO_POSITIONING=true
ENABLE_OCR=true

# File Settings
MAX_FILE_SIZE=10MB
UPLOAD_DIR=/tmp/browser_automation_files

# Browser Settings
BROWSER_HEADLESS=false
WINDOW_SIZE=1920x1080
```

### System Dependencies
- **Linux**: `wmctrl` for window management, `tesseract-ocr` for OCR
- **macOS**: Built-in AppleScript support, `tesseract` via Homebrew
- **Windows**: Built-in window management, `tesseract` via installer

## 🔧 Troubleshooting

### Common Issues

**Interactive prompts not appearing:**
- Check that `ENABLE_INTERACTIVE_PROMPTS=true` in configuration
- Ensure the automation is actually running (check status indicator)

**File upload not working:**
- Verify file size is under the limit (default 10MB)
- Check that file type is supported
- Ensure upload directory has write permissions

**Browser not positioning correctly:**
- Install system dependencies (`wmctrl` on Linux)
- Check that browser is actually running
- Verify window management permissions

**OCR not extracting text from images:**
- Install Tesseract OCR: `sudo apt-get install tesseract-ocr`
- Ensure image quality is sufficient for text recognition

### Debug Mode
```bash
# Run with debug output
DEBUG=true python enhanced_browser_interface.py
```

## 🔒 Security & Privacy

- **Local file processing**: All files are processed locally, not sent to external services
- **Temporary storage**: Uploaded files are stored in temporary directories
- **Credential handling**: Passwords are not logged or stored permanently
- **API key protection**: API keys are stored in environment variables only

## 🤝 Contributing

To add new features or improve existing ones:

1. Fork the repository
2. Create a feature branch
3. Add your enhancements to `enhanced-browser-interface.py`
4. Update this README with new features
5. Test thoroughly with the demo script
6. Submit a pull request

## 📝 License

This enhanced browser automation tool is provided as-is for educational and personal use.

---

**🎉 Enjoy your enhanced browser automation experience!**

For support or questions, please check the troubleshooting section or create an issue in the repository.
