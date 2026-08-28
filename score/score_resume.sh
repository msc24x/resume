#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Colors
R='\033[0;31m'  # Red
G='\033[0;32m'  # Green
Y='\033[0;33m'  # Yellow
B='\033[0;34m'  # Blue
C='\033[0;36m'  # Cyan
M='\033[0;35m'  # Magenta
W='\033[1;37m'  # White Bold
D='\033[0m'     # Reset

VERBOSE=""
JD_FILE=""

for arg in "$@"; do
    case "$arg" in
        -v|--verbose) VERBOSE="-v" ;;
        *) JD_FILE="$arg" ;;
    esac
done

echo -e "${M}╔══════════════════════════════════════════════════╗${D}"
echo -e "${M}║${W}            RESUME SCORE REPORT TOOL             ${M}║${D}"
echo -e "${M}╚══════════════════════════════════════════════════╝${D}"
echo ""

if [ -n "$JD_FILE" ]; then
    if [ ! -f "$JD_FILE" ]; then
        echo -e "${R}✘ File not found: $JD_FILE${D}"
        exit 1
    fi
    JD_TEXT=$(cat "$JD_FILE")
    echo -e "${G}✔ Reading JD from file: ${W}$JD_FILE${D}"
else
    echo -e "${C}Paste your job description below.${D}"
    echo -e "${Y}Press ${W}Ctrl+D${Y} when done (or Ctrl+Z on Windows).${D}"
    echo ""
    echo -e "${B}────────────────────────────────────────────────────${D}"
    echo ""
    JD_TEXT=$(cat)
fi

if [ -z "$JD_TEXT" ]; then
    echo -e "${R}✘ No job description provided. Exiting.${D}"
    exit 1
fi

JD_LINES=$(echo "$JD_TEXT" | wc -l)
JD_WORDS=$(echo "$JD_TEXT" | wc -w)

echo ""
echo -e "${B}────────────────────────────────────────────────────${D}"
echo -e "${G}✔ Received: ${W}${JD_WORDS} words${G} across ${W}${JD_LINES} lines${D}"
echo -e "${B}────────────────────────────────────────────────────${D}"
echo ""

if [ -z "$VERBOSE" ]; then
    echo ""
fi

if [ -n "$JD_FILE" ]; then
    python3 "$SCRIPT_DIR/score_resume.py" $VERBOSE "$SCRIPT_DIR/../resume_data.json" "$JD_FILE"
else
    echo "$JD_TEXT" | python3 "$SCRIPT_DIR/score_resume.py" $VERBOSE "$SCRIPT_DIR/../resume_data.json"
fi
