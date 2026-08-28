#!/usr/bin/env python3
import json
import sys

def escape_latex(text):
    chars = {'&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'}
    for char, replacement in chars.items():
        text = text.replace(char, replacement)
    return text

def format_date(start, end):
    return f"{start} -- {end}"

def main():
    with open('resume_data.json', 'r') as f:
        data = json.load(f)
    
    personal = data['personal_information']
    education = data['education']
    experience = data['experience']
    projects = data['projects']
    skills = data['technical_skills']
    
    latex = []
    latex.append(r'\documentclass[letterpaper,11pt]{article}')
    latex.append('')
    latex.append(r'\usepackage{latexsym}')
    latex.append(r'\usepackage[empty]{fullpage}')
    latex.append(r'\usepackage{titlesec}')
    latex.append(r'\usepackage{marvosym}')
    latex.append(r'\usepackage[usenames,dvipsnames]{color}')
    latex.append(r'\usepackage{verbatim}')
    latex.append(r'\usepackage{enumitem}')
    latex.append(r'\usepackage[hidelinks]{hyperref}')
    latex.append(r'\usepackage{fancyhdr}')
    latex.append(r'\usepackage[english]{babel}')
    latex.append(r'\usepackage{tabularx}')
    latex.append(r'\input{glyphtounicode}')
    latex.append('')
    latex.append(r'\pagestyle{fancy}')
    latex.append(r'\fancyhf{}')
    latex.append(r'\fancyfoot{}')
    latex.append(r'\renewcommand{\headrulewidth}{0pt}')
    latex.append(r'\renewcommand{\footrulewidth}{0pt}')
    latex.append('')
    latex.append(r'\addtolength{\oddsidemargin}{-0.5in}')
    latex.append(r'\addtolength{\evensidemargin}{-0.2in}')
    latex.append(r'\addtolength{\textwidth}{1in}')
    latex.append(r'\addtolength{\topmargin}{-.6in}')
    latex.append(r'\addtolength{\textheight}{1.0in}')
    latex.append('')
    latex.append(r'\urlstyle{same}')
    latex.append('')
    latex.append(r'\raggedbottom')
    latex.append(r'\raggedright')
    latex.append(r'\setlength{\tabcolsep}{0in}')
    latex.append('')
    latex.append(r'\titleformat{\section}{')
    latex.append(r'  \vspace{-4pt}\scshape\raggedright\large')
    latex.append(r'}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]')
    latex.append('')
    latex.append(r'\pdfgentounicode=1')
    latex.append('')
    latex.append(r'\newcommand{\resumeItem}[1]{')
    latex.append(r'  \item\small{')
    latex.append(r'    {#1 \vspace{-2pt}}')
    latex.append(r'  }')
    latex.append(r'}')
    latex.append('')
    latex.append(r'\newcommand{\resumeSubheading}[4]{')
    latex.append(r'  \vspace{-2pt}\item')
    latex.append(r'    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}')
    latex.append(r'      \textbf{#1} & #2 \\')
    latex.append(r'      \textit{\small#3} & \textit{\small #4} \\')
    latex.append(r'    \end{tabular*}\vspace{-7pt}')
    latex.append(r'}')
    latex.append('')
    latex.append(r'\newcommand{\resumeSubSubheading}[2]{')
    latex.append(r'    \item')
    latex.append(r'    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}')
    latex.append(r'      \textit{\small#1} & \textit{\small #2} \\')
    latex.append(r'    \end{tabular*}\vspace{-7pt}')
    latex.append(r'}')
    latex.append('')
    latex.append(r'\newcommand{\resumeProjectHeading}[2]{')
    latex.append(r'    \item')
    latex.append(r'    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}')
    latex.append(r'      \small#1 & #2 \\')
    latex.append(r'    \end{tabular*}\vspace{-7pt}')
    latex.append(r'}')
    latex.append('')
    latex.append(r'\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}')
    latex.append('')
    latex.append(r'\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}')
    latex.append('')
    latex.append(r'\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}')
    latex.append(r'\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}')
    latex.append(r'\newcommand{\resumeItemListStart}{\begin{itemize}}')
    latex.append(r'\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}')
    latex.append('')
    latex.append(r'\begin{document}')
    latex.append('')
    
    latex.append(r'\begin{center}')
    latex.append(f'    \\textbf{{\\Huge \\scshape {escape_latex(personal["name"])}}} \\\\ \\vspace{{1pt}}')
    latex.append(f'    \\href{{mailto:{personal["email"]}}}{{\\underline{{{escape_latex(personal["email"])}}}}} $|$ ')
    latex.append(f'    \\href{{https://{personal["portfolio"]}}}{{\\underline{{{escape_latex(personal["portfolio"])} (portfolio)}}}} $|$ ')
    latex.append(f'    \\href{{https://{personal["github"]}}}{{\\underline{{{escape_latex(personal["github"])}}}}} $|$')
    latex.append(f'    \\href{{https://{personal["linkedin"]}}}{{\\underline{{{escape_latex(personal["linkedin"])}}}}}')
    latex.append(r'\end{center}')
    latex.append('')
    
    latex.append(r'\section{Education}')
    latex.append(r'  \resumeSubHeadingListStart')
    for edu in education:
        date_range = format_date(edu['start_date'], edu['end_date'])
        dept_degree = f"{edu['department']} | {edu['degree']}"
        latex.append(f'    \\resumeSubheading')
        latex.append(f'      {{{escape_latex(edu["institution"])}}}{{{escape_latex(edu["score"])}}}')
        latex.append(f'      {{{escape_latex(dept_degree)}}}{{{escape_latex(date_range)}}}')
    latex.append(r'  \resumeSubHeadingListEnd')
    latex.append('')
    
    latex.append(r'\section{Experience}')
    latex.append(r'  \resumeSubHeadingListStart')
    for exp in experience:
        date_range = format_date(exp['start_date'], exp['end_date'])
        latex.append(f'  \\resumeSubheading')
        latex.append(f'    {{{escape_latex(exp["company"])}}}{{{escape_latex(date_range)}}}')
        latex.append(f'    {{{escape_latex(exp["role"])}}}{{{escape_latex(exp["location"])}}}')
        latex.append(r'    \resumeItemListStart')
        for resp in exp['responsibilities']:
            parts = resp.split(': ', 1)
            if len(parts) == 2:
                bold_text = escape_latex(parts[0]) + ':'
                rest_text = escape_latex(parts[1])
                latex.append('      \\resumeItem{\\textbf{' + bold_text + '} ' + rest_text + '}')
            else:
                latex.append('      \\resumeItem{' + escape_latex(resp) + '}')
        latex.append(r'    \resumeItemListEnd')
    latex.append(r'  \resumeSubHeadingListEnd')
    latex.append('')
    
    latex.append(r'\section{Projects}')
    latex.append(r'    \resumeSubHeadingListStart')
    for proj in projects:
        date_range = format_date(proj['start_date'], proj['end_date'])
        title = f"{proj['name']} - {proj['description']}"
        latex.append(r'      \resumeProjectHeading')
        latex.append(f'          {{\\textbf{{{escape_latex(title)}}}}}{{{escape_latex(date_range)}}}')
        
        links = proj.get('links', [])
        if links:
            link_parts = []
            for link in links:
                if link == 'Repository':
                    repo_url = f"https://github.com/msc24x/{proj['name'].lower()}"
                    link_parts.append(f'\\href{{{repo_url}}}{{\\emph{{\\underline{{Repository}}}}}}')
                elif 'hunter.cambo.in' in link:
                    link_parts.append(f'Deployed at \\href{{https://hunter.cambo.in}}{{\\emph{{\\underline{{hunter.cambo.in}}}}}}')
                elif 'XDA Forum' in link:
                    link_parts.append(f'\\href{{https://forum.xda-developers.com/android/apps-games/5-0-contactless-whatsapp-t4151497}}{{\\emph{{\\underline{{XDA Forum}}}}}}')
                else:
                    link_parts.append(escape_latex(link))
            latex.append(f"      \\resumeProjectHeading{{{', '.join(link_parts)}}}{{}}")
        
        latex.append(r'          \resumeItemListStart')
        for detail in proj['details']:
            parts = detail.split(': ', 1)
            if len(parts) == 2:
                bold_text = escape_latex(parts[0]) + ':'
                rest_text = escape_latex(parts[1])
                latex.append('            \\resumeItem{\\textbf{' + bold_text + '} ' + rest_text + '}')
            else:
                latex.append('            \\resumeItem{' + escape_latex(detail) + '}')
        latex.append(r'          \resumeItemListEnd')
    latex.append(r'    \resumeSubHeadingListEnd')
    latex.append('')
    
    latex.append(r'\section{Technical Skills}')
    latex.append(r' \begin{itemize}[leftmargin=0.15in, label={}]')
    latex.append(r'    \small{\item{')
    
    lang_list = ', '.join(skills['programming_scripting_languages'])
    tools_list = ', '.join(skills['tools_frameworks'])
    tech_list = ', '.join(skills['technical'])
    soft_list = ', '.join(skills['soft_skills'])
    
    latex.append(f'      \\textbf{{Languages:}} {escape_latex(lang_list)} \\\\')
    latex.append(f'      \\textbf{{Tools/Frameworks:}} {escape_latex(tools_list)} \\\\')
    latex.append(f'      \\textbf{{Core Competencies:}} {escape_latex(tech_list)} \\\\')
    latex.append(f'      \\textbf{{Soft Skills:}} {escape_latex(soft_list)}')
    latex.append(r'    }}')
    latex.append(r' \end{itemize}')
    latex.append('')
    latex.append(r'\end{document}')
    
    with open('resume.tex', 'w') as f:
        f.write('\n'.join(latex))
    
    print("Generated resume.tex successfully!")

if __name__ == '__main__':
    main()
