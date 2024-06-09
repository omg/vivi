import glob
  
# in a simple proposal command, we're just automatically correcting their diff file
# there should not be warnings or errors from process_diff, in fact it is unnecessary to run it just when they upload their diff file
# we only need to run it when we're checking the branch's proposals directory for incorrect files and etc.

# now on each update, we check the branch's proposals directory and process_diff.
# if there are warnings, they largely don't matter, but if there are errors, leave a bot comment in the PR,
# we can automatically correct the diff file's warnings via a !fix command in that same PR but it really doesn't matter
# bot comment "This proposal's branch has errors in X file(s), please fix them before continuing."
# only leave this comment once
# also add "This proposal's branch has warnings in X file(s), they can be automatically fixed by running !fix." if there are warnings

def get_proposal_conflicts(directory: str = "proposals"):
  """
  Retrieves conflicting diff lines from proposal files in the specified directory.
  This assumes that all files in the directory are diff files, and that the diff files are valid.
  
  Returns:
  - A list of strings, each representing a conflicting line found in the diff files.
  """
  
  additions = set()
  removals = set()
  
  proposals = glob.glob(f"{directory}/*")
  for file_path in proposals:
    with open(file_path, "r") as file:
      diff_text = file.read()
      lines = diff_text.split('\n')
      
      # Add all additions and removals to the respective lists
      for line in lines:
        if line.startswith("+"):
          additions.add(line[1:])
        elif line.startswith("-"):
          removals.add(line[1:])
  
  # Find the conflicts, which are lines that are both added and removed
  conflicts = additions.intersection(removals)
  return list(conflicts)



# Combines all the properly formatted diff files into a single diff file.