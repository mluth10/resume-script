from openai import OpenAI
import json
import os
import subprocess
import sys
import time
import threading
from dotenv import load_dotenv

# Get company name from command line argument
if len(sys.argv) != 2:
    print("Usage: python cover_gen.py <company_name>")
    print("Example: python cover_gen.py glossgenius")
    sys.exit(1)

company_name = sys.argv[1]

# Create output directory structure: Desktop/resume/company_name
resume_path = os.path.expanduser("~/Desktop/resume")
output_dir = os.path.join(resume_path, company_name)

# Create the directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created output directory: {output_dir}")
else:
    print(f"Using existing directory: {output_dir}")

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Load your resume and job description
with open('resume.json') as f:
    resume = json.load(f)
with open('job_description.txt') as f:
    job_desc = f.read()

# Build prompt for cover letter generation
cover_prompt = f"""
Given the following resume (in JSON format) and job description, write a compelling cover letter for the position.

The cover letter should:
1. Be professional and tailored to the specific company and role
2. Highlight relevant experience and skills from the resume that match the job requirements
3. Show enthusiasm for the company and position
4. Be concise but impactful (2-3 paragraphs)
5. Include specific examples of achievements that relate to the job description
6. Address the key requirements mentioned in the job description

RESUME JSON:
{json.dumps(resume)}

JOB DESCRIPTION:
{job_desc}

Please provide the cover letter content in the following format:
- Opening paragraph (introduction and interest in the role)
- Body paragraph(s) (relevant experience and achievements)
- Closing paragraph (enthusiasm and call to action)

Return only the cover letter content - no additional formatting or explanations.
"""

# Loading animation function
def loading_animation():
    animation = "|/-\\"
    idx = 0
    while not hasattr(loading_animation, 'stop'):
        print(f"\rGenerating cover letter for {company_name}... {animation[idx % len(animation)]}", end='', flush=True)
        time.sleep(0.1)
        idx += 1

# Start loading animation in a separate thread
loading_thread = threading.Thread(target=loading_animation)
loading_thread.start()

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": cover_prompt}],
        max_tokens=1000
    )
finally:
    # Stop the loading animation
    loading_animation.stop = True
    loading_thread.join()
    print("\r" + " " * 60 + "\r", end='', flush=True)  # Clear the loading line

# Get the generated cover letter content
cover_letter_content = response.choices[0].message.content

# Clean the content for LaTeX (escape special characters)
def clean_latex_cover(text):
    """Escape LaTeX special characters"""
    replacements = {
        '&': '\\&',
        '%': '\\%',
        '$': '\\$',
        '#': '\\#',
        '_': '\\_',
        '{': '\\{',
        '}': '\\}',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

cover_letter_content = clean_latex_cover(cover_letter_content)

# Create LaTeX content based on the template
latex_content = f"""%-------------------------
% Cover Letter in LaTeX
%------------------------

\\documentclass[letterpaper,11pt]{{article}}

\\usepackage{{latexsym}}
\\usepackage[empty]{{fullpage}}
\\usepackage{{titlesec}}
\\usepackage[usenames,dvipsnames]{{color}}
\\usepackage{{enumitem}}
\\usepackage[pdftex]{{hyperref}}
\\usepackage{{fancyhdr}}

\\pagestyle{{fancy}}
\\fancyhf{{}}
\\renewcommand{{\\headrulewidth}}{{0pt}}
\\renewcommand{{\\footrulewidth}}{{0pt}}

% Adjust margins
\\addtolength{{\\oddsidemargin}}{{-0.375in}}
\\addtolength{{\\evensidemargin}}{{-0.375in}}
\\addtolength{{\\textwidth}}{{1in}}
\\addtolength{{\\topmargin}}{{-.5in}}
\\addtolength{{\\textheight}}{{1.0in}}

\\urlstyle{{same}}
\\setlength{{\\parindent}}{{0pt}}
\\setlength{{\\parskip}}{{6pt}}

%-------------------------
% Custom commands
\\newcommand{{\\contactInfo}}[4]{{
  \\begin{{tabular*}}{{\\textwidth}}{{l@{{\\extracolsep{{\\fill}}}}r}}
    \\textbf{{\\Large #1}} & Email: \\href{{mailto:#2}}{{#2}} \\\\
    #3 & Phone: #4 \\\\
  \\end{{tabular*}}
}}

%-------------------------------------------
%%%%%%  COVER LETTER STARTS HERE  %%%%%%%%%%
\\begin{{document}}

%----------HEADING-----------------
\\contactInfo{{{resume['name']}}}{{{resume['contact']['email']}}}{{LinkedIn: {resume['contact']['linkedin']}}}{{{resume['contact']['phone']}}}

\\vspace{{1em}}

\\today

\\vspace{{1em}}

\\vspace{{1em}}

Dear Hiring Team,

\\vspace{{1em}}

{cover_letter_content}

\\vspace{{1em}}

Sincerely,\\\\
Manith Luthria

\\end{{document}}
"""

# Save LaTeX file
base_name = f'Cover_Letter_{company_name}'
tex_file_path = os.path.join(output_dir, base_name + ".tex")
with open(tex_file_path, "w") as f:
    f.write(latex_content)

print("LaTeX file generated successfully!")

# Compile LaTeX to PDF
print("Compiling LaTeX to PDF...")
try:
    # Run pdflatex to compile the document from the output directory
    result = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", base_name + ".tex"],
        capture_output=True,
        text=True,
        cwd=output_dir,
    )

    if result.returncode == 0:
        print("PDF generated successfully!")
        pdf_file_path = os.path.join(output_dir, base_name + ".pdf")
        print("Output file: " + pdf_file_path)
    else:
        print("LaTeX compilation failed!")
        print("Error output:")
        print(result.stderr)

except FileNotFoundError:
    print(
        "pdflatex not found. Please install a LaTeX distribution (like TeX Live or MiKTeX)"
    )
    print(
        f"You can still compile manually by running: cd {output_dir} && pdflatex "
        + base_name
        + ".tex"
    )
except Exception as e:
    print(f"Error during compilation: {e}")
    print(
        f"You can still compile manually by running: cd {output_dir} && pdflatex "
        + base_name
        + ".tex"
    )

