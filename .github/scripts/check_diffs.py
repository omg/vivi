import sys
import glob

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_diff_issues(diff_text):
    """
    Retrieves issues in a diff file.
    
    Parameters:
    - diff_text: A string representing the contents of a diff file.
    
    Returns:
    - A list of strings, each representing an issue found in the diff file.
    """

    lines = diff_text.split('\n')
    previous_line_empty = False
    has_content = False
    issues = []

    for line_number, line in enumerate(lines, start=1):
        if line.startswith("#"):
            # Comments
            comment_text = line[1:].strip()  # Retrieve the comment text, stripping leading and trailing spaces
            expected_line = "#" + " " + comment_text  # Create a properly formatted comment line
            previous_line_empty = False
            if expected_line != line:
                issues.append(f"{bcolors.WARNING}[warning] Invalid line on line {line_number}. Leading or trailing whitespace.\nActual: [{line}]\nExpected: [{expected_line}]{bcolors.ENDC}")
        elif line.startswith(("+", "-")):
            # Added/removed lines
            content = line[1:].strip().upper()  # Retrieve the content, stripping leading and trailing spaces and converting to uppercase
            if content:
                expected_line = line[0] + " " + content  # Create a properly formatted added/removed line
                previous_line_empty = False
                has_content = True
                if expected_line != line:
                    issues.append(f"{bcolors.WARNING}[warning] Invalid line on line {line_number}. Invalid formatting.\nActual: [{line}]\nExpected: [{expected_line}]{bcolors.ENDC}")
            else:
                issues.append(f"{bcolors.FAIL}[error] Invalid line on line {line_number}. No content after {line[0]}.{bcolors.ENDC}")
        elif line.strip() == "":
            # Empty lines
            if not previous_line_empty:
                # First detected empty line
                previous_line_empty = True
            else:
                # Consecutive empty lines
                issues.append(f"{bcolors.WARNING}[warning] Invalid line on line {line_number}. Consecutive empty lines.{bcolors.ENDC}")
        else:
            # Invalid character
            issues.append(f"{bcolors.FAIL}[error] Invalid line on line {line_number}. Must start with +, -, or #.{bcolors.ENDC}")

    if not has_content:
        # No content found in diff
        issues.append(f"{bcolors.FAIL}[error] No content found in diff.{bcolors.ENDC}")
    else:
        # Check for leading and trailing empty lines
        if lines[0] == "":
            issues.append(f"{bcolors.WARNING}[warning] Leading empty lines detected.{bcolors.ENDC}")
        if lines[-1] == "":
            issues.append(f"{bcolors.WARNING}[warning] Trailing empty lines detected.{bcolors.ENDC}")
    
    return issues

# Find all .diff files in the repository
diff_files = glob.glob('changes/*.diff', recursive=True)

# Check each file
has_issues = False
for file_path in diff_files:
    issues = get_diff_issues(open(file_path, 'r').read())
    if issues:
        has_issues = True
        print(f"{bcolors.BOLD}{bcolors.FAIL}[failure]{bcolors.ENDC}{bcolors.FAIL} Issues found in {file_path}:{bcolors.ENDC}")
        for issue in issues:
            print(issue)

if has_issues:
    sys.exit(1)