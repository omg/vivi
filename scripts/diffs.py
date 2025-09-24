from scripts.colors import Colors

def get_line_name(line_number, uppercase=False):
    """
    Retrieves the name of a line number for display in the console.
    A number will be displayed such as "line 1", while None will be displayed as "the end of the file".
    
    Parameters:
    - line_number: The line number.
    
    Returns:
    - The name of the line number.
    """
    
    if line_number is None:
        return "The end of the file" if uppercase else "the end of the file"
    else:
        return f"Line {line_number}" if uppercase else f"line {line_number}"

# Issue classes

class Issue:
    """
    Represents an issue with a file.
    
    Attributes:
    - issue_type: The type of issue (error or warning).
    - message: The message describing the issue.
    - correctable: A boolean indicating whether the issue is automatically correctable.
    """
    
    def __init__(self, issue_type, message, correctable):
        self.issue_type = issue_type
        self.message = message
        self.correctable = correctable
    
    def get_color(self):
        """
        Returns the color associated with the issue type for display in the console.
        
        Returns:
        - The color code for the issue type.
        """
        if self.issue_type == "error":
            return Colors.FAIL
        else:
            return Colors.WARNING
    
    def get_prefix(self):
        """
        Returns the prefix for the issue for display in the console.
        This will display such as "[error]" or "[warning]".
        
        Returns:
        - The prefix for the issue.
        """
        return f"{self.get_color()}[{self.issue_type}] "
    
    def get_display_message(self):
        """
        Returns the message of the issue for display in the console.
        Issue classes which inherit from this class should override this method if they want to customize the message display.
        
        Returns:
        - The display message of the issue.
        """
        return f"{self.message}"

    def __str__(self):
        return f"{self.get_prefix()}{self.get_display_message()}{Colors.ENDC}"

    def __repr__(self):
        return self.__str__()

class LineIssue(Issue):
    """
    Represents an issue with specific lines in a file.
    
    Attributes:
    - issue_type: The type of issue (error or warning).
    - message: The message describing the issue.
    - line_start: The starting line number of the issue.
    - line_end: The ending line number of the issue.
    - correctable: A boolean indicating whether the issue is automatically correctable.
    """
    
    def __init__(self, issue_type, message, line_start, line_end, correctable):
        super().__init__(issue_type, message, correctable)
        self.line_start = line_start
        self.line_end = line_end
  
    def get_display_message(self):
        single_line = self.line_start == self.line_end
        
        if single_line:
            invalid_lines_message = f"Invalid line at {get_line_name(self.line_start)}."
        else:
            line_range_str = f"{get_line_name(self.line_start)} to {get_line_name(self.line_end)}"
            invalid_lines_message = f"Invalid lines from {line_range_str}."
        
        return f"{invalid_lines_message} {self.message}"

class ConflictIssue(Issue):
    """
    Represents an issue with conflicting content between multiple files.
    
    Attributes:
    - issue_type: The type of issue (error or warning).
    - conflicting_content: The content that is conflicting between the files.
    - addition_files: A list of files where the content was added.
    - removal_files: A list of files where the content was removed.
    """
    
    def __init__(self, issue_type, conflicting_content, addition_files, removal_files):
        super().__init__(issue_type, "Conflict detected.", False)
        self.conflicting_content = conflicting_content
        self.addition_files = addition_files
        self.removal_files = removal_files
    
    def join_words(self, words):
        if len(words) == 1:
            return words[0]
        elif len(words) == 2:
            return f"{words[0]} and {words[1]}"
        else:
            return ', '.join(words[:-1]) + f", and {words[-1]}"
    
    def get_display_message(self):
        added_files_str = self.join_words(self.addition_files)
        removed_files_str = self.join_words(self.removal_files)
        return f"Conflict detected, added in {added_files_str}, but removed in {removed_files_str}: {self.conflicting_content}."

# Collections

class IssueCollection:
    """
    Represents a collection of issues.
    
    Attributes:
    - issues: A list of issues.
    """
    
    def __init__(self):
        self.issues = []
    
    def add_issue(self, issue: Issue):
        """
        Adds an issue to the collection.
        
        Parameters:
        - issue: The issue to add.
        """
        self.issues.append(issue)
    
    def extend(self, issues: list[Issue]):
        """
        Extends the collection with a list of issues.
        
        Parameters:
        - issues: A list of issues to add.
        """
        self.issues.extend(issues)
    
    def has_issue_type(self, issue_type):
        """
        Determines if the collection contains any issues of a specific type.
        
        Parameters:
        - issue_type: The type of issue to check for.
        
        Returns:
        - A boolean indicating if the collection contains any issues of the specified type.
        """
        return any(issue.issue_type == issue_type for issue in self.issues)
    
    def has_issues(self):
        """
        Determines if the collection contains any issues.
        
        Returns:
        - A boolean indicating if the collection contains any issues.
        """
        return len(self.issues) > 0
    
    def has_errors(self):
        """
        Determines if the collection contains any errors.
        
        Returns:
        - A boolean indicating if the collection contains any errors.
        """
        return self.has_issue_type("error")
    
    def has_warnings(self):
        """
        Determines if the collection contains any warnings.
        
        Returns:
        - A boolean indicating if the collection contains any warnings.
        """
        return self.has_issue_type("warning")
    
    def __str__(self):
        return '\n'.join(str(issue) for issue in self.issues)
    
    def __repr__(self):
        return self.__str__()

# Processing

class ProcessedDiff:
    def __init__(self, issues: IssueCollection, corrected_diff: str, additions: set, removals: set):
        self.issues = issues
        self.corrected_diff = corrected_diff
        self.additions = additions
        self.removals = removals

# Process functionality

MAXIMUM_LINES = 3

def process_diff(diff_content: str) -> ProcessedDiff:
    """
    Processes a diff by validating and automatically correcting its content.
    
    Ensures lines start with #, +, or -, and corrects formatting and whitespace issues.
    
    Parameters:
    - diff_content: The content of the diff.
    
    Returns:
    - A ProcessedDiff object containing the corrected diff content, issues, and sets of additions and removals.
    """
    
    lines = diff_content.split('\n')
    
    corrected_lines = []
    unique_content_lines = []
    
    issues = IssueCollection()
    additions = set()
    removals = set()
    
    has_content = False
    current_empty_lines = 0
    too_many_lines_start = 0
    
    def check_too_many_lines(line_number=None):
        if current_empty_lines >= MAXIMUM_LINES:
            issues.add_issue(
                LineIssue(
                    issue_type="warning",
                    message=f"Too many empty lines.",
                    line_start=too_many_lines_start,
                    line_end=line_number,
                    correctable=True
                )
            )
    
    for line_number, line in enumerate(lines, start=1):
        is_empty = line.strip() == ""
        
        if is_empty:
            current_empty_lines += 1
            if current_empty_lines == MAXIMUM_LINES:
                too_many_lines_start = line_number
            else:
                corrected_lines.append("")
            continue
        else:
            if current_empty_lines > 0:
                check_too_many_lines()
            current_empty_lines = 0
        
        if line.startswith("#"):
            # Comments
            comment_text = line[1:].strip()  # Retrieve the comment text, stripping leading and trailing spaces
            corrected_line = "#" + " " + comment_text  # Create a properly formatted comment line
            corrected_lines.append(corrected_line)
            if corrected_line != line:
                issues.add_issue(
                    LineIssue(
                        issue_type="warning",
                        message="Invalid formatting.",
                        line_start=line_number,
                        line_end=line_number,
                        correctable=True
                    )
                )
        elif line.startswith(("+", "-")):
            # Added/removed lines
            is_addition = line[0] == "+"
            content = line[1:].strip().upper()  # Retrieve the content, stripping leading and trailing spaces and converting to uppercase
            if content:
                has_content = True
                corrected_line = line[0] + " " + content  # Create a properly formatted added/removed line
                if content in unique_content_lines:
                    # This is decided to be an error REGARDLESS of if both lines are additions, or both lines are removals.
                    # You could technically automatically remove the duplicate line, but that could lead to unintended readability changes.
                    # Maybe there was an important comment above the duplicate line that could provide context to the change.
                    # It could also have been grouped with other similar changes, etc.
                    # It's better to let the user decide how to handle the duplicate line.
                    issues.add_issue(
                        LineIssue(
                            issue_type="error",
                            message=f"Duplicate content detected: {content}.",
                            line_start=line_number,
                            line_end=line_number,
                            correctable=False
                        )
                    )
                else:
                    corrected_lines.append(corrected_line)
                    unique_content_lines.append(content)
                    
                    content_set = additions if is_addition else removals
                    content_set.add(content)
            else:
                issues.add_issue(
                    LineIssue(
                        issue_type="error",
                        message=f"No content after {line[0]}.",
                        line_start=line_number,
                        line_end=line_number,
                        correctable=False
                    )
                )
        else:
            # Invalid character
            issues.add_issue(
                LineIssue(
                    issue_type="error",
                    message="Invalid line start character.",
                    line_start=line_number,
                    line_end=line_number,
                    correctable=False
                )
            )
    
    check_too_many_lines()
    
    if not has_content:
        # No content found in diff
        issues.add_issue(
            Issue(
                issue_type="error",
                message="No content found in diff.",
                correctable=False
            )
        )

    # Join the corrected lines back into a single string
    corrected_text = '\n'.join(corrected_lines)
    
    return ProcessedDiff(issues, corrected_text, additions, removals)

# Diff mapping

class ProcessedDiffMapping:
    """
    Represents a mapping of processed diffs by file.
    
    Attributes:
    - general_issues: An IssueCollection object containing issues general to all files.
    - conflicts: An IssueCollection object containing conflicts between the additions and removals of the diffs.
    - processed_diffs: A dictionary mapping file names to ProcessedDiff objects.
    """
    
    def __init__(self):
        self.general_issues = IssueCollection()
        self.conflicts = IssueCollection()
        self.processed_diffs: dict[str, ProcessedDiff] = {}
    
    def add_processed_diff(self, file_name: str, processed_diff: ProcessedDiff):
        """
        Adds an issue collection to the mapping for a specific file.
        This will overwrite any existing issue collection for the file.
        
        Parameters:
        - file_name: The name of the file.
        - issue_collection: The issue collection to add.
        """
        self.processed_diffs[file_name] = processed_diff
        
    def add_unprocessed_diff(self, file_name: str, diff_content: str):
        """
        Adds a diff to the mapping for a specific file.
        
        Parameters:
        - file_name: The name of the file.
        - diff_content: The content of the diff.
        """
        self.add_processed_diff(file_name, process_diff(diff_content))
    
    def add_general_issue(self, issue: Issue):
        """
        Adds an issue to the general issue collection for a specific type.
        
        Parameters:
        - file_name: The name of the file.
        - issue: The issue to add.
        """
        self.general_issues.add_issue(issue)
    
    def check_for_conflicts(self):
        """
        Checks for conflicts between the additions and removals of all processed diffs.
        
        Displays as:
        Conflict detected, added in file1, added in file2, but removed in file3, removed in file4: conflicting content.
        """
        conflicts = IssueCollection()
        
        additions: dict[str, list[str]] = {}
        removals: dict[str, list[str]] = {}
        
        for file_name, processed_diff in self.processed_diffs.items():
            for addition in processed_diff.additions:
                additions.setdefault(addition, []).append(file_name)
            for removal in processed_diff.removals:
                removals.setdefault(removal, []).append(file_name)
        
        for content, addition_files in additions.items():
            if content in removals:
                removal_files = removals[content]
                conflicts.add_issue(
                    ConflictIssue(
                        issue_type="error",
                        conflicting_content=content,
                        addition_files=addition_files,
                        removal_files=removal_files
                    )
                )
        
        self.conflicts = conflicts
        return conflicts
    
    def get_all_issues(self):
        issues = IssueCollection()
        issues.extend(self.get_top_level_issues())
        issues.extend(self.get_diff_issues())
        return issues
    
    def get_top_level_issues(self):
        issues = IssueCollection()
        issues.extend(self.general_issues.issues)
        issues.extend(self.conflicts.issues)
        return issues
    
    def get_diff_issues(self):
        issues = IssueCollection()
        for processed_diff in self.processed_diffs.values():
            issues.extend(processed_diff.issues.issues)
        return issues
    
    def get_collection_display(self, name: str, issue_collection: IssueCollection):
        return f"[{name}]\n{issue_collection}"
    
    def __str__(self):
        display_messages = []
        
        if self.get_top_level_issues().has_issues():
            display_messages.append(self.get_collection_display("General", self.general_issues))
        
        for file_name, issue_collection in self.issues.items():
            if issue_collection.has_issues():
                display_messages.append(self.get_collection_display(file_name, issue_collection))
        
        return '\n\n'.join(display_messages)
    
    def __repr__(self):
        return self.__str__()
