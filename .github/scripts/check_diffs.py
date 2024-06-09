import sys
import glob

from utils.colors import Colors

def get_diff_issues(diff_content):
  """
  Retrieves issues in a diff, formatted for printing to the console.
  
  Parameters:
  - diff_content: The content of the diff.
  
  Returns:
  - A list of strings, each representing a printable issue found in the diff file.
  """

  lines = diff_content.split('\n')
  previous_line_empty = False
  has_content = False
  content_lines = []
  issues = []

  for line_number, line in enumerate(lines, start=1):
    if line.startswith("#"):
      # Comments
      comment_text = line[1:].strip()  # Retrieve the comment text, stripping leading and trailing spaces
      expected_line = "#" + " " + comment_text  # Create a properly formatted comment line
      previous_line_empty = False
      if expected_line != line:
        issues.append(f"{Colors.WARNING}[warning] Invalid line on line {line_number}. Invalid formatting.\nActual:\t[{line}]\nExpected:\t[{expected_line}]{Colors.ENDC}")
    elif line.startswith(("+", "-")):
      # Added/removed lines
      content = line[1:].strip().upper()  # Retrieve the content, stripping leading and trailing spaces and converting to uppercase
      if content:
        expected_line = line[0] + " " + content  # Create a properly formatted added/removed line
        if not content in content_lines:
          content_lines.append(content)
        else:
          issues.append(f"{Colors.FAIL}[error] Invalid line on line {line_number}. Duplicate content detected: {content}.{Colors.ENDC}")
        previous_line_empty = False
        has_content = True
        if expected_line != line:
          issues.append(f"{Colors.FAIL}[error] Invalid line on line {line_number}. Invalid formatting.\nActual:\t[{line}]\nExpected:\t[{expected_line}]{Colors.ENDC}")
      else:
        issues.append(f"{Colors.FAIL}[error] Invalid line on line {line_number}. No content after {line[0]}.{Colors.ENDC}")
    elif line.strip() == "":
      # Empty lines
      if not previous_line_empty:
        # First detected empty line
        previous_line_empty = True
      else:
        # Consecutive empty lines
        issues.append(f"{Colors.WARNING}[warning] Invalid line on line {line_number}. Consecutive empty lines.{Colors.ENDC}")
    else:
      # Invalid character
      issues.append(f"{Colors.FAIL}[error] Invalid line on line {line_number}. Must start with +, -, or #.{Colors.ENDC}")

  if not has_content:
    # No content found in diff
    issues.append(f"{Colors.FAIL}[error] No content found in diff.{Colors.ENDC}")
  else:
    # Check for leading and trailing empty lines
    if lines[0] == "":
      issues.append(f"{Colors.WARNING}[warning] Leading empty lines detected.{Colors.ENDC}")
    
  return issues

# Find all files in the proposals directory, don't check the extension.
diff_files = glob.glob("proposals/*")

# Check each file
has_issues = False
for file_path in diff_files:
  # Check if this is a diff file
  if not file_path.endswith(".diff"):
    has_issues = True
    print(f"{Colors.BOLD}{Colors.FAIL}[failure]{Colors.ENDC}{Colors.FAIL} Non-diff file found in the proposals directory: {file_path}{Colors.ENDC}")
    continue
  # Get issues in the diff file
  issues = get_diff_issues(open(file_path, 'r').read())
  if issues:
    has_issues = True
    print(f"{Colors.BOLD}{Colors.FAIL}[failure]{Colors.ENDC}{Colors.FAIL} Issues found in {file_path}:{Colors.ENDC}")
    for issue in issues:
      print(issue)

if has_issues:
  sys.exit(1)
