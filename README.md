# 📄 LaTeX Resume Optimizer

An AI-powered web application that optimizes LaTeX resumes for Applicant Tracking Systems (ATS) compatibility. The application uses AI to tailor your resume to specific job descriptions, ensuring better chances of passing through ATS filters.

## ✨ Features

- **AI-Powered Optimization**: Uses DeepSeek AI to optimize resumes based on job descriptions
- **ATS Compatibility**: Ensures resumes are optimized for Applicant Tracking Systems
- **Modern Web UI**: Clean, responsive interface with tabbed navigation
- **PDF Generation**: Automatically compiles optimized LaTeX to PDF
- **Job URL Support**: Can extract job descriptions from URLs
- **Resume Management**: Upload once, optimize multiple times for different jobs

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed on your system
2. **Tectonic** (LaTeX compiler) installed
   - macOS: `brew install tectonic`
   - Linux: Download from [tectonic-typesetting.github.io](https://tectonic-typesetting.github.io/)
   - Windows: Download from the official website

### Installation

1. **Clone or download** this repository
2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Update API Key** (optional):
   - Open `main1.py`
   - Replace `DEEPSEEK_API_KEY` with your own DeepSeek API key
   - Get a free API key from [DeepSeek](https://platform.deepseek.com/)

### Running the Application

1. **Start the server**:
   ```bash
   python main1.py
   ```

2. **Open your browser** and go to:
   ```
   http://localhost:8000
   ```

## 📖 How to Use

### Step 1: Upload Your Master Resume
1. Click on the **"Upload Resume"** tab
2. Select your `.tex` file (LaTeX resume)
3. Click **"Upload Resume"**
4. This file will be your master template for all optimizations

### Step 2: Optimize Your Resume
1. Click on the **"Optimize Resume"** tab
2. Provide either:
   - **Job URL**: Paste the URL of the job posting
   - **Job Description**: Copy and paste the job description text
3. Click **"Optimize Resume"**
4. Wait for AI processing (may take a few moments)
5. The optimized PDF will automatically download

### Step 3: Download Optimized Resumes
1. Click on the **"Download Resumes"** tab
2. View all your optimized resumes
3. Click **"Download"** to get any previously optimized resume

## 🔧 Technical Details

### Backend (FastAPI)
- **Framework**: FastAPI with async support
- **AI Integration**: DeepSeek API for resume optimization
- **File Processing**: LaTeX to PDF compilation using Tectonic
- **Storage**: Local file system for resume storage

### Frontend (HTML/CSS/JavaScript)
- **Design**: Modern, responsive UI with gradient backgrounds
- **Features**: Tabbed interface, drag-and-drop file upload, real-time status updates
- **Compatibility**: Works on desktop and mobile browsers

### AI Optimization Features
- **Summary Rewriting**: Tailors summary to job requirements
- **Experience Optimization**: Rewrites bullet points for each role
- **Skills Enhancement**: Adds relevant skills from job description
- **Project Alignment**: Adds projects relevant to the job
- **Keyword Highlighting**: Bold formatting for ATS keywords

## 📁 File Structure

```
Latex_check_ui/
├── main1.py              # FastAPI backend server
├── index.html            # Web UI frontend
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── ATSResumeOptimizerStorage/  # Generated resumes (auto-created)
```

## 🔒 Security Notes

- The application stores files locally on your machine
- API keys are stored in the code (consider using environment variables for production)
- CORS is enabled for all origins (restrict in production)

## 🐛 Troubleshooting

### Common Issues

1. **"Tectonic not found" error**:
   - Install Tectonic LaTeX compiler
   - Ensure it's in your system PATH

2. **"UI file not found" error**:
   - Ensure `index.html` is in the same directory as `main1.py`

3. **Upload fails**:
   - Check that your file is a valid `.tex` file
   - Ensure the file is not corrupted

4. **Optimization fails**:
   - Check your internet connection (needed for AI API)
   - Verify your API key is valid
   - Ensure you've uploaded a master resume first

### LaTeX Requirements

Your LaTeX resume should:
- Use standard LaTeX packages (no custom fonts)
- Be compatible with Overleaf or TeX Live
- Have a proper document structure (`\documentclass` to `\end{document}`)

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the MIT License.

---

**Happy Resume Optimizing! 🎯** # Resume-Optimizer
