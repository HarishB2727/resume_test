from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import tempfile
import subprocess
import re
import os
import base64
import uuid

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STORAGE_DIR = "/Users/bejawadaharish/Desktop/ATSResumeOptimizerStorage"
os.makedirs(STORAGE_DIR, exist_ok=True)

MASTER_RESUME_PATH = os.path.join(STORAGE_DIR, "master_resume.tex")

DEEPSEEK_API_KEY = "sk-0a19442e1f1141f3bc5616db1e6af0be"

def call_deepseek_api(latex_resume, job_description, prompt):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Resume:\n{latex_resume}\n\nJob Description:\n{job_description}"}
        ],
        "temperature": 0.2,
        "max_tokens": 4096
    }
    resp = requests.post(url, json=data, headers=headers)
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content']

def clean_latex_output(text):
    lines = text.strip().splitlines()
    forbidden = [
        '\\input{glyphtounicode}',
        '\\fontspec',
        '\\xunicode',
        '\\pdfgentounicode',
        'fontspec.sty',
        'xunicode.sty',
        'glyphtounicode',
    ]
    def is_forbidden(line):
        for key in forbidden:
            if key in line:
                return True
        return False
    lines = [line for line in lines if not line.strip().startswith('```')]
    lines = [line for line in lines if not is_forbidden(line)]
    cleaned = '\n'.join(lines)
    match = re.search(r'(\\documentclass[\s\S]+?\\end{document})', cleaned)
    if match:
        return match.group(1)
    return cleaned

def extract_job_description_from_url(url):
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    # Fallback: get all visible text (tune this per site as needed!)
    text = soup.get_text(separator='\n')
    return text

@app.post("/upload_master_resume/")
async def upload_master_resume(latex_file: UploadFile = File(...)):
    """Upload your resume.tex ONCE. This is your master file and will never be overwritten."""
    content = (await latex_file.read()).decode("utf-8")
    with open(MASTER_RESUME_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    return {"message": "Master resume uploaded and stored successfully."}

@app.post("/optimize_resume/")
async def optimize_resume(
    job_url: str = Form(None),
    job_description: str = Form(None),
    prompt: str = Form(None),
    company_name: str = Form(None),
    location: str = Form(None)
):
    if not os.path.exists(MASTER_RESUME_PATH):
        return JSONResponse({"error": "No master resume uploaded yet. Please upload resume.tex first!"}, status_code=400)
    with open(MASTER_RESUME_PATH, "r", encoding="utf-8") as f:
        latex_content = f.read()

    if job_url:
        job_description_text = extract_job_description_from_url(job_url)
    elif job_description:
        job_description_text = job_description
    else:
        return JSONResponse({"error": "Provide job_description or job_url!"}, status_code=400)

    if not company_name:
        return JSONResponse({"error": "Company name is required!"}, status_code=400)
    safe_company_name = re.sub(r'\W+', '', company_name)
    base_filename = f"{safe_company_name}_resume"

    FIXED_LAST_LINE = (
        "If you find any geographic, citizenship, or clearance requirements (e.g., 'US Citizens only'), respond ONLY with: BLOCKED: <reason>. Do NOT output any LaTeX code in that case. "
        "Do NOT use or output \\pdfgentounicode, \\input{glyphtounicode}, \\fontspec, \\xunicode, or any external or non-standard font or Unicode packages or commands. "
        "Only use standard LaTeX packages and commands that compile on Overleaf or TeX Live. "
        "Your output MUST be only the full, valid preserved LaTeX resume code, starting with \\documentclass and ending with \\end{document}. "
        "Do NOT include explanations, markdown, triple backticks, comments, or any text before or after the LaTeX. If you include anything except the raw, complete LaTeX code, you have failed the task."
    )
    location_instruction = f'Update location to this: "{location}"' if location else ''
    if prompt:
        full_prompt = prompt.strip()
        if location_instruction:
            full_prompt += "\n" + location_instruction
        full_prompt += "\n\n" + FIXED_LAST_LINE
    else:
        full_prompt = (location_instruction + "\n\n" if location_instruction else "") + FIXED_LAST_LINE

    ai_response = call_deepseek_api(latex_content, job_description_text, full_prompt)
    if ai_response.strip().startswith('BLOCKED:'):
        return JSONResponse({"error": ai_response.strip()}, status_code=400)
    optimized_latex = clean_latex_output(ai_response)

    if location:
        optimized_latex = replace_header_location(optimized_latex, location)

    # Use a unique temp directory for this session
    temp_id = str(uuid.uuid4())
    temp_dir = os.path.join(tempfile.gettempdir(), f"resumeopt_{temp_id}")
    os.makedirs(temp_dir, exist_ok=True)
    tex_path = os.path.join(temp_dir, base_filename + ".tex")
    pdf_path = os.path.join(temp_dir, base_filename + ".pdf")

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(optimized_latex)

    try:
        subprocess.run(["tectonic", tex_path, "--outdir", temp_dir], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        return JSONResponse({"error": f"PDF compilation failed: {e.stderr}"}, status_code=500)
    if not os.path.exists(pdf_path):
        return JSONResponse({"error": "PDF compilation failed - no output file generated"}, status_code=500)

    # Return download URLs for both files
    return JSONResponse({
        "success": True,
        "message": "Resume optimized successfully!",
        "pdf_url": f"/download_temp_file/{temp_id}/{base_filename}.pdf",
        "tex_url": f"/download_temp_file/{temp_id}/{base_filename}.tex",
        "pdf_filename": base_filename + ".pdf",
        "tex_filename": base_filename + ".tex"
    })

@app.get("/download_temp_file/{temp_id}/{filename}")
def download_temp_file(temp_id: str, filename: str):
    temp_dir = os.path.join(tempfile.gettempdir(), f"resumeopt_{temp_id}")
    file_path = os.path.join(temp_dir, filename)
    if not os.path.exists(file_path):
        return JSONResponse({"error": "File not found or expired."}, status_code=404)
    # Set correct media type
    if filename.endswith('.pdf'):
        media_type = "application/pdf"
    elif filename.endswith('.tex'):
        media_type = "application/x-tex"
    else:
        media_type = "application/octet-stream"
    return FileResponse(file_path, media_type=media_type, filename=filename)

# Helper function to replace location in LaTeX header
def replace_header_location(latex_code, new_location):
    # This function assumes the header location is set with something like \\location{...} or similar
    # You may need to adjust the regex depending on your LaTeX template
    return re.sub(r'(\\location\{)[^}]*\}', r'\\location{' + re.escape(new_location) + r'}', latex_code, count=1)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML UI."""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>UI file not found. Please ensure index.html exists.</h1>", status_code=404)

@app.post("/compile_tex/")
async def compile_tex(request: Request):
    form = await request.form()
    latex_code = form.get("latex_code")
    if not latex_code:
        return JSONResponse({"error": "No LaTeX code provided."}, status_code=400)

    tex_path = os.path.join(STORAGE_DIR, "latest_resume.tex")
    pdf_path = os.path.join(STORAGE_DIR, "latest_resume.pdf")

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_code)

    try:
        subprocess.run(["tectonic", tex_path, "--outdir", STORAGE_DIR], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        return JSONResponse({"error": f"PDF compilation failed: {e.stderr}"}, status_code=500)
    if not os.path.exists(pdf_path):
        return JSONResponse({"error": "PDF compilation failed - no output file generated"}, status_code=500)

    return JSONResponse({
        "success": True,
        "pdf_url": "/download_latest_pdf",
        "pdf_filename": "latest_resume.pdf"
    })

@app.get("/download_latest_pdf")
def download_latest_pdf():
    pdf_path = os.path.join(STORAGE_DIR, "latest_resume.pdf")
    if not os.path.exists(pdf_path):
        return JSONResponse({"error": "No latest PDF found."}, status_code=404)
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    headers = {
        "Content-Disposition": "inline; filename=latest_resume.pdf"
    }
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
