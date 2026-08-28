#!/usr/bin/env python3
import json
import re
import os
import sys
import argparse
from datetime import datetime
from difflib import SequenceMatcher
from collections import Counter

import Stemmer


MONTH_MAP = {
    "jan": 1, "january": 1, "feb": 2, "february": 2,
    "mar": 3, "march": 3, "apr": 4, "april": 4,
    "may": 5, "jun": 6, "june": 6,
    "jul": 7, "july": 7, "aug": 8, "august": 8,
    "sep": 9, "september": 9, "oct": 10, "october": 10,
    "nov": 11, "november": 11, "dec": 12, "december": 12,
}

STOPWORDS = set("""
a an the and or but in on at to for of is it its that this these
those with from by as are was were be been being have has had do does
did will would shall should may might can could not no nor so if then
than too very just about above after again all also am any because
before between both during each few more most other some such into
over own same through under until up we he she they their them
what which who whom how where when while your my his her our their
you we us our also
""".split())


def stem_word(stemmer, word):
    return stemmer.stemWord(word.lower())


def tokenize_text(text):
    text = text.lower()
    tokens = text.split()
    result = []
    for tok in tokens:
        result.append(tok)
        for part in re.split(r'[^a-z0-9]', tok):
            if part:
                result.append(part)
    return [t for t in result
            if t not in STOPWORDS and len(t) > 1 and re.search(r'[a-z0-9]', t)]


def extract_bigrams(tokens):
    return [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens) - 1)]


def parse_date(date_str):
    date_str = date_str.strip().lower().replace(".", "")
    if date_str in ("present", "current", "now"):
        return datetime.now()
    parts = date_str.split()
    if len(parts) == 2:
        month_str, year_str = parts
        month = MONTH_MAP.get(month_str[:3], 1)
        year = int(year_str)
        return datetime(year, month, 1)
    return None


def calc_experience(experience_list):
    ranges = []
    for exp in experience_list:
        start = parse_date(exp["start_date"])
        end = parse_date(exp["end_date"])
        if start and end:
            ranges.append((start, end))
    if not ranges:
        return 0, 0
    ranges.sort(key=lambda x: x[0])
    merged = [ranges[0]]
    for start, end in ranges[1:]:
        prev_start, prev_end = merged[-1]
        if start <= prev_end:
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    total_days = sum((end - start).days for start, end in merged)
    total_months = total_days // 30
    years = total_months // 12
    months = total_months % 12
    return years, months


def extract_required_years(jd_text):
    patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience)?',
        r'(\d+)\+\s*year',
        r'experience\s*:\s*(\d+)\+?\s*years?',
        r'minimum\s*(?:of\s*)?(\d+)\s*years?',
        r'at\s*least\s*(\d+)\s*years?',
    ]
    found = []
    for pat in patterns:
        for m in re.finditer(pat, jd_text.lower()):
            yr = int(m.group(1))
            if 1 <= yr <= 30:
                found.append(yr)
    return max(found) if found else None


def load_skills_map(path="skills_map.json"):
    with open(path) as f:
        return json.load(f)


def build_resume_skills(resume_data, stemmer, skills_map):
    def collect_texts(data):
        out = []
        if isinstance(data, dict):
            for v in data.values():
                out.extend(collect_texts(v))
        elif isinstance(data, list):
            for v in data:
                out.extend(collect_texts(v))
        elif isinstance(data, str):
            out.append(data)
        return out

    tokens = set()
    for text in collect_texts(resume_data):
        tokens.update(tokenize_text(text))

    stemmed = {stem_word(stemmer, t): t for t in tokens}

    skills_in_cat = {}
    skills_category = {}
    for cat, aliases in skills_map.items():
        alias_stems = {stem_word(stemmer, a) for a in aliases}
        cat_tokens = set()
        for t in tokens:
            if stem_word(stemmer, t) in alias_stems:
                cat_tokens.add(t)
                skills_category.setdefault(t, cat)
        skills_in_cat[cat] = cat_tokens

    return tokens, stemmed, skills_in_cat, skills_category


def find_category(term, skills_map):
    term_lower = term.lower()
    for category, aliases in skills_map.items():
        for alias in aliases:
            if term_lower == alias.lower():
                return category
    return None


def fuzzy_match(term, candidates, threshold=0.85):
    best_match = None
    best_score = 0
    for candidate in candidates:
        score = SequenceMatcher(None, term.lower(), candidate.lower()).ratio()
        if score > best_score and score >= threshold:
            best_score = score
            best_match = candidate
    return best_match, best_score


def score_resume(resume_data, jd_text, skills_map):
    stemmer = Stemmer.Stemmer("english")

    resume_skills, resume_stemmed, resume_skills_in_cat, resume_skills_category = build_resume_skills(
        resume_data, stemmer, skills_map
    )

    all_skill_aliases = set()
    for category, aliases in skills_map.items():
        for alias in aliases:
            all_skill_aliases.add(alias.lower())

    all_skill_stems = set()
    for alias in all_skill_aliases:
        all_skill_stems.add(stem_word(stemmer, alias))

    jd_tokens = tokenize_text(jd_text)
    jd_bigrams = extract_bigrams(jd_tokens)
    jd_stemmed_tokens = set(stem_word(stemmer, t) for t in jd_tokens)
    jd_stemmed_bigrams = set(stem_word(stemmer, b) for b in jd_bigrams)

    token_counts = Counter()
    for t in jd_tokens:
        token_counts[t] += 1
    for b in jd_bigrams:
        token_counts[b] += 1

    matched = []
    missing = []
    matched_categories = set()

    for jd_token in set(jd_tokens):
        jd_stem = stem_word(stemmer, jd_token)

        is_skill_term = False
        for alias in all_skill_aliases:
            if jd_token == alias:
                is_skill_term = True
                break
            alias_stem = stem_word(stemmer, alias)
            if jd_stem == alias_stem:
                ratio = SequenceMatcher(None, jd_token, alias).ratio()
                if ratio >= 0.75:
                    is_skill_term = True
                    break

        if not is_skill_term:
            continue

        if jd_stem in resume_stemmed:
            original = resume_stemmed[jd_stem]
            cat = resume_skills_category.get(original, find_category(jd_token, skills_map))
            matched.append({
                "term": jd_token,
                "matched_to": original,
                "match_type": "exact_stem",
                "category": cat,
                "count": token_counts[jd_token],
            })
            if cat:
                matched_categories.add(cat)
            continue

        fuzzy_result, fuzzy_score = fuzzy_match(jd_token, resume_skills, threshold=0.80)
        if fuzzy_result:
            cat = resume_skills_category.get(fuzzy_result, find_category(jd_token, skills_map))
            matched.append({
                "term": jd_token,
                "matched_to": fuzzy_result,
                "match_type": f"fuzzy({fuzzy_score:.0%})",
                "category": cat,
                "count": token_counts[jd_token],
            })
            if cat:
                matched_categories.add(cat)
            continue

        cat = find_category(jd_token, skills_map)
        if cat:
            resume_cat_skills = {s.lower() for s in resume_skills_in_cat.get(cat, set())}
            if resume_cat_skills:
                matched.append({
                    "term": jd_token,
                    "matched_to": f"category:{cat} ({', '.join(list(resume_cat_skills)[:3])})",
                    "match_type": "category",
                    "category": cat,
                    "count": token_counts[jd_token],
                })
                matched_categories.add(cat)
                continue

        missing.append({
            "term": jd_token,
            "category": cat,
            "count": token_counts[jd_token],
        })

    matched_term_set = set(m["term"] for m in matched)
    matched_deduped = []
    seen_matched = set()
    for m in matched:
        if m["term"] not in seen_matched:
            seen_matched.add(m["term"])
            matched_deduped.append(m)
    matched = matched_deduped

    missing_deduped = []
    seen_missing = set()
    for m in missing:
        if m["term"] not in seen_missing:
            seen_missing.add(m["term"])
            missing_deduped.append(m)
    missing_deduped.sort(key=lambda x: -x["count"])

    total_matched = len(matched)
    total_jd_skills = len(matched) + len(missing)
    if total_jd_skills > 0:
        score = round((total_matched / total_jd_skills) * 100)
    else:
        score = 0

    resume_skills_in_cat = {}
    for cat in skills_map:
        cat_skills = set()
        for rs in resume_skills:
            rs_cat = resume_skills_category.get(rs, "")
            if rs_cat == cat:
                cat_skills.add(rs.lower())
        resume_skills_in_cat[cat] = cat_skills

    return {
        "score": min(score, 100),
        "matched": matched,
        "missing": missing_deduped,
        "matched_categories": matched_categories,
        "total_jd_keywords": total_jd_skills,
        "total_matched": total_matched,
        "resume_skills_in_cat": resume_skills_in_cat,
    }


def gradient_bar(score, width=20):
    R = '\033[0m'
    filled = min(score // 5, width)
    empty = width - filled
    segments = []
    for i in range(width):
        if i < filled:
            ratio = i / max(width - 1, 1)
            if score < 30:
                r, g, b = 200, int(40 + ratio * 60), 40
            elif score < 50:
                r, g, b = 220, int(80 + ratio * 100), 40
            elif score < 70:
                r, g, b = int(220 - ratio * 100), 200, 40
            elif score < 90:
                r, g, b = int(100 - ratio * 50), 200, int(40 + ratio * 30)
            else:
                r, g, b = 40, int(100 + ratio * 100), 40
            segments.append(f"\033[38;2;{r};{g};{b}m█")
        else:
            segments.append(f"\033[38;2;80;80;80m░")
    return "".join(segments) + R


def format_report(result, experience_info, skills_map, verbose=False, report_path=None):
    lines = []
    w = 60

    stemmer = Stemmer.Stemmer("english")

    def term_covered_in_category(term, resume_skill_strings):
        term_stems = {stem_word(stemmer, t) for t in tokenize_text(term)}
        if not term_stems:
            return False
        resume_stems = set()
        for s in resume_skill_strings:
            resume_stems.update(stem_word(stemmer, t) for t in tokenize_text(s))
        return term_stems.issubset(resume_stems)

    score = result["score"]
    years, months = experience_info["your_experience"]

    if not verbose:
        lines.append(f"SCORE: {score}/100")
        lines.append(gradient_bar(score))
        lines.append("")

        if experience_info["jd_required"] is not None:
            jd_req = experience_info["jd_required"]
            meets = years >= jd_req
            status = "✓ Meets" if meets else "✗ Below"
            lines.append(f"  Experience: {years}y {months}m  |  JD wants: {jd_req}+y  |  {status}")

        all_gaps = []
        for m in result["matched"]:
            if m["match_type"] == "category":
                cat = m.get("category")
                if cat:
                    resume_lower = result.get("resume_skills_in_cat", {}).get(cat, set())
                    if not term_covered_in_category(m["term"], resume_lower):
                        all_gaps.append(m["term"])
        if all_gaps:
            lines.append("")
            lines.append(f"GAPS ({len(all_gaps)}) — matched by category but not in your resume:")
            lines.append(f"  {', '.join(sorted(set(all_gaps)))}")

        if result["missing"]:
            lines.append("")
            lines.append(f"MISSING ({len(result['missing'])}) — no match found:")
            missing_by_cat = {}
            uncategorized = []
            for m in result["missing"]:
                cat = m.get("category")
                if cat:
                    if cat not in missing_by_cat:
                        missing_by_cat[cat] = []
                    missing_by_cat[cat].append(m)
                else:
                    uncategorized.append(m)
            for cat in sorted(missing_by_cat.keys()):
                items = missing_by_cat[cat]
                cat_label = cat.replace("_", " ").title()
                terms = ", ".join(sorted(m["term"] for m in items))
                lines.append(f"  {cat_label}: {terms}")
            if uncategorized:
                terms = ", ".join(sorted(m["term"] for m in uncategorized))
                lines.append(f"  Other: {terms}")

        lines.append("")
        lines.append(f"  Run with -v for detailed report")
        return "\n".join(lines)

    lines.append("=" * w)
    lines.append("  RESUME SCORE REPORT".center(w))
    lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(w))
    lines.append("=" * w)
    lines.append("")

    exp_str = f"{years} year{'s' if years != 1 else ''} {months} month{'s' if months != 1 else ''}" if months else f"{years} year{'s' if years != 1 else ''}"
    lines.append("EXPERIENCE")
    lines.append(f"  Your experience:    {exp_str}")
    if experience_info["jd_required"] is not None:
        jd_req = experience_info["jd_required"]
        meets = years >= jd_req
        status = "✓ Meets requirement" if meets else "✗ Does NOT meet requirement"
        lines.append(f"  JD requires:        {jd_req}+ years")
        lines.append(f"  Status:             {status}")
    else:
        lines.append(f"  JD requires:        Not specified")
    lines.append("")

    filled = score // 5
    empty = 20 - filled
    bar = "█" * filled + "░" * empty
    lines.append(f"SCORE: {score}/100")
    lines.append(bar)
    lines.append("")

    lines.append(f"MATCHED KEYWORDS ({result['total_matched']}/{result['total_jd_keywords']})")
    by_category = {}
    for m in result["matched"]:
        cat = m.get("category") or "other"
        if cat not in by_category:
            by_category[cat] = {"jd_terms": set(), "resume_matches": set(), "types": set(),
                                "exact_terms": set(), "category_only_terms": set()}
        by_category[cat]["jd_terms"].add(m["term"])
        by_category[cat]["resume_matches"].add(m["matched_to"])
        by_category[cat]["types"].add(m["match_type"])
        if m["match_type"] in ("exact_stem",) or m["match_type"].startswith("fuzzy"):
            by_category[cat]["exact_terms"].add(m["term"])
        elif m["match_type"] == "category":
            by_category[cat]["category_only_terms"].add(m["term"])

    for cat, info in sorted(by_category.items()):
        cat_label = cat.replace("_", " ").title()
        jd_terms_str = ", ".join(sorted(info["jd_terms"]))
        resume_matches_str = ", ".join(sorted(info["resume_matches"]))
        types_str = ", ".join(sorted(info["types"]))
        lines.append(f"  {cat_label}:")
        lines.append(f"    JD terms:    {jd_terms_str}")
        lines.append(f"    Your skills: {resume_matches_str}")
        lines.append(f"    Match type:  {types_str}")
        if info["category_only_terms"]:
            resume_lower = result.get("resume_skills_in_cat", {}).get(cat, set())
            not_owned = [t for t in sorted(info["category_only_terms"])
                         if not term_covered_in_category(t, resume_lower)]
            if not_owned:
                lines.append(f"    Gap:        {', '.join(not_owned)} — not in your resume, consider adding")
    lines.append("")

    if result["missing"]:
        missing_by_cat = {}
        uncategorized = []
        for m in result["missing"]:
            cat = m.get("category")
            if cat:
                if cat not in missing_by_cat:
                    missing_by_cat[cat] = []
                missing_by_cat[cat].append(m)
            else:
                uncategorized.append(m)

        lines.append(f"MISSING KEYWORDS ({len(result['missing'])})")
        for cat in sorted(missing_by_cat.keys()):
            items = missing_by_cat[cat]
            cat_label = cat.replace("_", " ").title()
            terms_str = ", ".join(sorted(m["term"] for m in items))
            lines.append(f"  {cat_label}:")
            lines.append(f"    Missing:  {terms_str}")
            cat_aliases = skills_map.get(cat, [])
            resume_skills_cat = result.get("resume_skills_in_cat", {}).get(cat, set())
            candidates = [a for a in cat_aliases if a.lower() not in resume_skills_cat]
            if candidates:
                lines.append(f"    Consider: {', '.join(candidates[:5])}")
        if uncategorized:
            terms_str = ", ".join(sorted(m["term"] for m in uncategorized))
            lines.append(f"  Other:")
            lines.append(f"    Missing:  {terms_str}")
        lines.append("")

    lines.append("RECOMMENDATIONS")
    high_freq_missing = [m for m in result["missing"] if m["count"] >= 2]
    if high_freq_missing:
        for m in high_freq_missing[:5]:
            lines.append(f"  • \"{m['term']}\" is mentioned {m['count']}x in JD — consider adding if you have experience")
    if experience_info["jd_required"] and years < experience_info["jd_required"]:
        gap = experience_info["jd_required"] - years
        lines.append(f"  • JD requires {experience_info['jd_required']}+ years but you have ~{years} years (gap: ~{gap} year{'s' if gap != 1 else ''})")
    if not high_freq_missing and not (experience_info["jd_required"] and years < experience_info["jd_required"]):
        lines.append("  • Strong match! No major gaps identified.")
    lines.append("")
    lines.append("=" * w)
    if report_path:
        lines.append(f"  Report saved: {report_path}".center(w))
    lines.append("=" * w)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Score resume against a job description")
    parser.add_argument("resume", nargs="?", default="resume_data.json", help="Path to resume JSON")
    parser.add_argument("jd", nargs="?", default=None, help="Path to JD file (reads stdin if omitted)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed report")
    args = parser.parse_args()

    def log(msg):
        if args.verbose:
            print(f"  {msg}", flush=True)

    skills_map_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skills_map.json")

    log("⟳ Loading resume data...")
    with open(args.resume) as f:
        resume_data = json.load(f)

    log("⟳ Loading skills map...")
    skills_map = load_skills_map(skills_map_path)

    log("⟳ Calculating experience...")
    years, months = calc_experience(resume_data.get("experience", []))

    log("⟳ Reading job description...")
    if args.jd:
        with open(args.jd) as f:
            jd_text = f.read()
    else:
        jd_text = sys.stdin.read()

    log("⟳ Extracting required experience...")
    jd_required = extract_required_years(jd_text)

    log("⟳ Scoring resume against JD...")
    result = score_resume(resume_data, jd_text, skills_map)

    experience_info = {
        "your_experience": (years, months),
        "jd_required": jd_required,
    }

    ignore_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ignore")
    os.makedirs(ignore_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(ignore_dir, f"report_{timestamp}.txt")

    log("⟳ Generating report...")
    report = format_report(result, experience_info, skills_map, verbose=args.verbose, report_path=report_path)
    print(report)

    with open(report_path, "w") as f:
        f.write(report)


if __name__ == "__main__":
    main()
