import json
import subprocess
import os

# Load JSON resume
with open("Manith_Luthria_Resume.json", "r") as f:
    resume = json.load(f)

def clean_latex(obj):
    """
    Recursively escape only & and % characters in string fields for LaTeX.
    """
    if isinstance(obj, dict):
        return {k: clean_latex(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_latex(item) for item in obj]
    elif isinstance(obj, str):
        # Only escape & and % characters
        return obj.replace('&', '\\&').replace('%', '\\%')
    else:
        return obj

resume = clean_latex(resume)

# Create LaTeX content based on the template
latex_content = """%-------------------------
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
  \\textbf{\\Large """ + resume["name"] + """} & Email : \\href{mailto:""" + resume["contact"]["email"] + """}{""" + resume["contact"]["email"] + """}\\\\
  \\href{""" + resume["contact"]["linkedin"] + """}{""" + resume["contact"]["linkedin"] + """} & Mobile : """ + resume["contact"]["phone"] + """ \\\\
\\end{tabular*}

%-----------SUMMART-----------------
\\section{Summary}

""" + resume["summary"] + """

%-----------EXPERIENCE-----------------
\\section{Experience}
  \\resumeSubHeadingListStart
"""

# Add experience entries
for exp in resume["experience"]:
    latex_content += """
    \\resumeSubheading
      {""" + exp["company"] + """}{""" + exp["location"] + """}
      {""" + exp["title"] + """}{""" + exp["date"] + """}
      \\resumeItemListStart
"""
    for ach in exp["achievements"]:
        # Split achievement into key and description if possible
        if ": " in ach:
            parts = ach.split(": ", 1)
            key = parts[0]
            description = parts[1]
            latex_content += """        \\resumeItem{""" + key + """}
          {""" + description + """}
"""
        else:
            # If no colon, use the whole achievement as description
            latex_content += """        \\item\\small{""" + ach + """ \\vspace{-2pt}}
"""
    latex_content += """      \\resumeItemListEnd
"""

latex_content += """  \\resumeSubHeadingListEnd

%-----------PROJECTS-----------------
\\section{Projects}
  \\resumeSubHeadingListStart
"""

# Add experience entries
for proj in resume["projects"]:
    latex_content += """
    \\resumeSubheading
      {""" + proj["name"] + """}{}
      {""" + proj["subtitle"] + """}{}
      \\resumeItemListStart
"""
    for detail in proj["details"]:
        # Split achievement into key and description if possible
        if ": " in detail:
            parts = detail.split(": ", 1)
            key = parts[0]
            description = parts[1]
            latex_content += """        \\resumeItem{""" + key + """}
          {""" + description + """}
"""
        else:
            # If no colon, use the whole achievement as description
            latex_content += """        \\item\\small{""" + detail + """ \\vspace{-2pt}}
"""
    latex_content += """      \\resumeItemListEnd
"""

latex_content += """  \\resumeSubHeadingListEnd

%-----------EDUCATION-----------------
\\section{Education}
  \\resumeSubHeadingListStart
"""

# Add education entries
for edu in resume["education"]:
    latex_content += """    \\resumeSubheading
      {""" + edu["school"] + """}{""" + edu["location"] + """}
      {""" + edu["degree"] + """;  GPA: """ + edu["gpa"] + """}{""" + edu["year"] + """}
"""

latex_content += """  \\resumeSubHeadingListEnd

%--------PROGRAMMING SKILLS------------
\\section{Skills}
 \\resumeSubHeadingListStart
   \\item{
     \\textbf{Languages}{: """ + ", ".join(resume["skills"]["languages"]) + """}
   }
   \\item{
     \\textbf{Tools and Technologies}{: """ + ", ".join(resume["skills"]["tools_and_technologies"]) + """}
   }
 \\resumeSubHeadingListEnd

%-------------------------------------------
\\end{document}
"""

# Save LaTeX file
with open("Manith_Luthria_Resume_Template.tex", "w") as f:
    f.write(latex_content)

print("LaTeX file generated successfully!")

# Compile LaTeX to PDF
print("Compiling LaTeX to PDF...")
try:
    # Run pdflatex to compile the document
    result = subprocess.run(['pdflatex', '-interaction=nonstopmode', 'Manith_Luthria_Resume_Template.tex'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("PDF generated successfully!")
        print("Output file: Manith_Luthria_Resume_Template.pdf")
    else:
        print("LaTeX compilation failed!")
        print("Error output:")
        print(result.stderr)
        
except FileNotFoundError:
    print("pdflatex not found. Please install a LaTeX distribution (like TeX Live or MiKTeX)")
    print("You can still compile manually by running: pdflatex Manith_Luthria_Resume_Template.tex")
except Exception as e:
    print(f"Error during compilation: {e}")
    print("You can still compile manually by running: pdflatex Manith_Luthria_Resume_Template.tex")
