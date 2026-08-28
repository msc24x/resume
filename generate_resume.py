#!/usr/bin/env python3
import json
import re

PLACEHOLDER = re.compile(r'\{\{(\w+)\}\}')

def escape_latex(text):
    chars = {
        '\\': r'\textbackslash{}',
        '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#',
        '_': r'\_', '{': r'\{', '}': r'\}',
        '~': r'\textasciitilde{}', '^': r'\textasciicircum{}',
    }
    for char, replacement in chars.items():
        text = text.replace(char, replacement)
    return text

def format_date(start, end):
    return f"{start} -- {end}"

def format_bullet(text):
    parts = text.split(': ', 1)
    if len(parts) == 2:
        return (r'\resumeItem{\textbf{' + escape_latex(parts[0]) + ':} '
                + escape_latex(parts[1]) + '}')
    return r'\resumeItem{' + escape_latex(text) + '}'

def build_header(personal):
    name = escape_latex(personal['name'])
    email = escape_latex(personal['email'])
    phone = escape_latex(personal['phone']) if 'phone' in personal else ''
    portfolio = personal['portfolio']
    github = personal['github']
    linkedin = personal['linkedin']

    contact = [
        f'    \\href{{mailto:{email}}}{{\\underline{{{email}}}}} $|$',
    ]

    if phone:
        contact.append(
            f'    \\href{{tel:{phone}}}{{\\underline{{{phone}}}}} $|$'
        )

    return '\n'.join([
        r'\begin{center}',
        f'    \\textbf{{\\Huge \\scshape {name}}} \\\\ \\vspace{{1pt}}',
        *contact,
        f'    \\href{{https://{portfolio}}}{{\\underline{{{escape_latex(portfolio)} (portfolio)}}}} $|$',
        f'    \\href{{https://{github}}}{{\\underline{{{escape_latex(github)}}}}} $|$',
        f'    \\href{{https://{linkedin}}}{{\\underline{{{escape_latex(linkedin)}}}}}',
        r'\end{center}',
    ])

def build_education(education):
    lines = [r'  \resumeSubHeadingListStart']
    for edu in education:
        date_range = format_date(edu['start_date'], edu['end_date'])
        dept_degree = f"{edu['department']} | {edu['degree']}"
        lines.append(f'    \\resumeSubheading{{{escape_latex(edu["institution"])}}}{{{escape_latex(edu["score"])}}}')
        lines.append(f'      {{{escape_latex(dept_degree)}}}{{{escape_latex(date_range)}}}')
    lines.append(r'  \resumeSubHeadingListEnd')
    return '\n'.join(lines)

def build_experience(experience):
    lines = [r'  \resumeSubHeadingListStart']
    for exp in experience:
        date_range = format_date(exp['start_date'], exp['end_date'])
        lines.append(f'  \\resumeSubheading{{{escape_latex(exp["company"])}}}{{{escape_latex(date_range)}}}')
        lines.append(f'    {{{escape_latex(exp["role"])}}}{{{escape_latex(exp["location"])}}}')
        lines.append(r'    \resumeItemListStart')
        for resp in exp['responsibilities']:
            lines.append('      ' + format_bullet(resp))
        lines.append(r'    \resumeItemListEnd')
    lines.append(r'  \resumeSubHeadingListEnd')
    return '\n'.join(lines)

def build_links(links):
    parts = []
    for link in links:
        label = escape_latex(link['label'])
        url = link['url']
        parts.append(f'\\href{{{url}}}{{\\emph{{\\underline{{{label}}}}}}}')
    return ', '.join(parts)

def build_projects(projects):
    lines = [r'    \resumeSubHeadingListStart']
    for proj in projects:
        date_range = format_date(proj['start_date'], proj['end_date'])
        title = f"{proj['name']} - {proj['description']}"
        lines.append(f'      \\resumeProjectHeading{{{{\\textbf{{{escape_latex(title)}}}}}}}{{{escape_latex(date_range)}}}')
        links = proj.get('links', [])
        if links:
            lines.append('      \\resumeProjectHeading{' + build_links(links) + '}{}')
        lines.append(r'          \resumeItemListStart')
        for detail in proj['details']:
            lines.append('            ' + format_bullet(detail))
        lines.append(r'          \resumeItemListEnd')
    lines.append(r'    \resumeSubHeadingListEnd')
    return '\n'.join(lines)

def build_skills(skills):
    lang = ', '.join(skills['programming_scripting_languages'])
    tools = ', '.join(skills['tools_frameworks'])
    tech = ', '.join(skills['technical'])
    soft = ', '.join(skills['soft_skills'])
    return '\n'.join([
        r' \begin{itemize}[leftmargin=0.15in, label={}]',
        r'    \small{\item{',
        f'      \\textbf{{Languages:}} {escape_latex(lang)} \\\\',
        f'      \\textbf{{Tools/Frameworks:}} {escape_latex(tools)} \\\\',
        f'      \\textbf{{Core Competencies:}} {escape_latex(tech)} \\\\',
        f'      \\textbf{{Soft Skills:}} {escape_latex(soft)}',
        r'    }}',
        r' \end{itemize}',
    ])

def main():
    with open('resume_data.json') as f:
        data = json.load(f)
    with open('resume_template.tex') as f:
        template = f.read()

    context = {
        'HEADER': build_header(data['personal_information']),
        'EDUCATION': build_education(data['education']),
        'EXPERIENCE': build_experience(data['experience']),
        'PROJECTS': build_projects(data['projects']),
        'SKILLS': build_skills(data['technical_skills']),
    }

    result = PLACEHOLDER.sub(lambda m: context.get(m.group(1), m.group(0)), template)

    with open('resume.tex', 'w') as f:
        f.write(result)

    print("Generated resume.tex successfully!")

if __name__ == '__main__':
    main()
