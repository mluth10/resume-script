from openai import OpenAI
import json
import os
from dotenv import load_dotenv
import subprocess
import sys
import time
import threading

# Get input file from command line argument
if len(sys.argv) != 2:
    print("Usage: python combo.py <company_name>")
    print("Example: python combo.py instagram")
    sys.exit(1)

company_name = sys.argv[1]

base_name = 'Manith_Luthria_Resume_' + company_name

# Create output directory structure: Desktop/resume/company_name
resume_path = os.path.expanduser("./resume")
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

# Build prompt
prompt = f"""
Given the following resume (in JSON format) and the following job description, rewrite the resume JSON to better match the keywords, skills, and requirements in the job description.
Only output optimized JSON — do not add explanations. Do not add any other text or comments. Keep the original formatting and structure of the resume. The output should be a similar length to the original resume.
Do not format the json, return the json as a raw string so that json.loads() can be used to parse it.
Make sure not to make up any information, only modify the resume to match the job description. You can change the ordering and add more detail, but do not claim I did anything I didn't do or have skills I don't have.
Remember that achievements should start with active verbs like 'Led', 'Built', etc and should show a clear impact, numerically if possible.
Each experience should never have more then five achievements.
Remember that you are optimizing for an ATS, so make sure to include the keywords from the job description in the resume in order to achieve 95%+ ATS score.
DO NOT under any circumstances return anything other than a raw string of JSON.

RESUME JSON:
{json.dumps(resume)}

JOB DESCRIPTION:
{job_desc}

OPTIMIZED RESUME JSON:
"""

# Loading animation function
def loading_animation():
    animation = "|/-\\"
    idx = 0
    while not hasattr(loading_animation, 'stop'):
        print(f"\rOptimizing resume for {company_name}... {animation[idx % len(animation)]}", end='', flush=True)
        time.sleep(0.1)
        idx += 1

# Start loading animation in a separate thread
loading_thread = threading.Thread(target=loading_animation)
loading_thread.start()

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Cheaper alternative to gpt-4o
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000  # Adjust as needed
    )
finally:
    # Stop the loading animation
    loading_animation.stop = True
    loading_thread.join()
    print("\r" + " " * 50 + "\r", end='', flush=True)  # Clear the loading line

# Parse and save new resume
optimized_json = response.choices[0].message.content
# print(optimized_json)
try:
    optimized_resume = json.loads(optimized_json)
except Exception as e:
    print("Error parsing optimized_json:", e)
    print("optimized_json value:", optimized_json)
    raise
optimized_resume_path = os.path.join(output_dir, 'optimized_resume.json')
with open(optimized_resume_path, 'w') as f:
    json.dump(optimized_resume, f, indent=2)

print(f"Optimized resume saved to: {optimized_resume_path}")

# Use the optimized resume that was already loaded
resume = optimized_resume


def clean_resume_latex(obj):
    """
    Recursively escape only & and % characters in string fields for LaTeX.
    """
    if isinstance(obj, dict):
        return {k: clean_resume_latex(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_resume_latex(item) for item in obj]
    elif isinstance(obj, str):
        # Only escape & and % characters
        return obj.replace("&", "\\&").replace("%", "\\%")
    else:
        return obj


resume = clean_resume_latex(resume)

# Create LaTeX content based on the template
resume_latex_content = (
    """%-------------------------
% Resume in Latex
% Generated from JSON data
%------------------------

\\documentclass[letterpaper,11pt]{article}

\\usepackage{latexsym}
\\usepackage[empty]{fullpage}
\\usepackage{titlesec}
\\usepackage{marvosym}
\\usepackage[usenames,dvipsnames]{color}
\\usepackage{verbatim}
\\usepackage{enumitem}
\\usepackage[pdftex]{hyperref}
\\usepackage{fancyhdr}

\\pagestyle{fancy}
\\fancyhf{} % clear all header and footer fields
\\fancyfoot{}
\\renewcommand{\\headrulewidth}{0pt}
\\renewcommand{\\footrulewidth}{0pt}

% Adjust margins
\\addtolength{\\oddsidemargin}{-0.375in}
\\addtolength{\\evensidemargin}{-0.375in}
\\addtolength{\\textwidth}{1in}
\\addtolength{\\topmargin}{-.5in}
\\addtolength{\\textheight}{1.0in}

\\urlstyle{same}

\\raggedbottom
\\raggedright
\\setlength{\\tabcolsep}{0in}

% Sections formatting
\\titleformat{\\section}{
  \\vspace{-4pt}\\scshape\\raggedright\\large
}{}{0em}{}[\\color{black}\\titlerule \\vspace{-5pt}]

%-------------------------
% Custom commands
\\newcommand{\\resumeItem}[2]{
  \\item\\small{
    \\textbf{#1}{: #2 \\vspace{-2pt}}
  }
}

\\newcommand{\\resumeSubheading}[4]{
  \\vspace{-1pt}\\item
    \\begin{tabular*}{0.97\\textwidth}{l@{\\extracolsep{\\fill}}r}
      \\textbf{#1} & #2 \\\\
      \\textit{\\small#3} & \\textit{\\small #4} \\\\
    \\end{tabular*}\\vspace{-5pt}
}

\\newcommand{\\resumeSubItem}[2]{\\resumeItem{#1}{#2}\\vspace{-4pt}}

\\renewcommand{\\labelitemii}{$\\circ$}

\\newcommand{\\resumeSubHeadingListStart}{\\begin{itemize}[leftmargin=*]}
\\newcommand{\\resumeSubHeadingListEnd}{\\end{itemize}}
\\newcommand{\\resumeItemListStart}{\\begin{itemize}}
\\newcommand{\\resumeItemListEnd}{\\end{itemize}\\vspace{-5pt}}

%-------------------------------------------
%%%%%%  CV STARTS HERE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%

\\begin{document}

%----------HEADING-----------------
\\begin{tabular*}{\\textwidth}{l@{\\extracolsep{\\fill}}r}
  \\textbf{\\Large """
    + resume["name"]
    + """} & Email : \\href{mailto:"""
    + resume["contact"]["email"]
    + """}{"""
    + resume["contact"]["email"]
    + """}\\\\
  \\href{"""
    + resume["contact"]["linkedin"]
    + """}{"""
    + resume["contact"]["linkedin"]
    + """} & Mobile : """
    + resume["contact"]["phone"]
    + """ \\\\
\\end{tabular*}

%-----------SUMMART-----------------
\\section{Summary}

"""
    + resume["summary"]
    + """

%-----------EXPERIENCE-----------------
\\section{Experience}
  \\resumeSubHeadingListStart
"""
)

# Add experience entries
for exp in resume["experience"]:
    resume_latex_content += (
        """
    \\resumeSubheading
      {"""
        + exp["company"]
        + """}{"""
        + exp["location"]
        + """}
      {"""
        + exp["title"]
        + """}{"""
        + exp["date"]
        + """}
      \\resumeItemListStart
"""
    )
    for ach in exp["achievements"]:
        # Split achievement into key and description if possible
        if ": " in ach:
            parts = ach.split(": ", 1)
            key = parts[0]
            description = parts[1]
            resume_latex_content += (
                """        \\resumeItem{"""
                + key
                + """}
          {"""
                + description
                + """}
"""
            )
        else:
            # If no colon, use the whole achievement as description
            resume_latex_content += (
                """        \\item\\small{"""
                + ach
                + """ \\vspace{-2pt}}
"""
            )
    resume_latex_content += """      \\resumeItemListEnd
"""

resume_latex_content += """  \\resumeSubHeadingListEnd

%-----------PROJECTS-----------------
\\section{Projects}
  \\resumeSubHeadingListStart
"""

# Add experience entries
for proj in resume["projects"]:
    resume_latex_content += (
        """
    \\resumeSubheading
      {"""
        + proj["name"]
        + """}{}
      {"""
        + proj["subtitle"]
        + """}{}
      \\resumeItemListStart
"""
    )
    for detail in proj["details"]:
        # Split achievement into key and description if possible
        if ": " in detail:
            parts = detail.split(": ", 1)
            key = parts[0]
            description = parts[1]
            resume_latex_content += (
                """        \\resumeItem{"""
                + key
                + """}
          {"""
                + description
                + """}
"""
            )
        else:
            # If no colon, use the whole achievement as description
            resume_latex_content += (
                """        \\item\\small{"""
                + detail
                + """ \\vspace{-2pt}}
"""
            )
    resume_latex_content += """      \\resumeItemListEnd
"""

resume_latex_content += """  \\resumeSubHeadingListEnd

%-----------EDUCATION-----------------
\\section{Education}
  \\resumeSubHeadingListStart
"""

# Add education entries
for edu in resume["education"]:
    resume_latex_content += (
        """    \\resumeSubheading
      {"""
        + edu["school"]
        + """}{"""
        + edu["location"]
        + """}
      {"""
        + edu["degree"]
        + """;  GPA: """
        + edu["gpa"]
        + """}{"""
        + edu["year"]
        + """}
"""
    )

resume_latex_content += (
    """  \\resumeSubHeadingListEnd

%--------PROGRAMMING SKILLS------------
\\section{Skills}
 \\resumeSubHeadingListStart
   \\item{
     \\textbf{Languages}{: """
    + ", ".join(resume["skills"]["languages"])
    + """}
   }
   \\item{
     \\textbf{Tools and Technologies}{: """
    + ", ".join(resume["skills"]["tools_and_technologies"])
    + """}
   }
 \\resumeSubHeadingListEnd

%-------------------------------------------
\\end{document}
"""
)

# Save LaTeX file
tex_file_path = os.path.join(output_dir, base_name + ".tex")
with open(tex_file_path, "w") as f:
    f.write(resume_latex_content)

print("Resume LaTeX file generated successfully!")

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
- Do not include Dear Hiring Team, or any other salutation, just start with the first paragraph.
- Do not include Sincerely, or any other closing, just end with the last paragraph.

Return only the cover letter content - no additional formatting or explanations.
"""

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

print("Cover Letter LaTeX file generated successfully!")

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

# Delete all files in the output directory that are not .pdf, .tex, or .json files
for filename in os.listdir(output_dir):
    if not (filename.endswith('.pdf') or filename.endswith('.tex') or filename.endswith('.json')):
        file_path = os.path.join(output_dir, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")
