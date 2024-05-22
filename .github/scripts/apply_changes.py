import os

def apply_diff(word_list_path, diff_path):
  # Read the current word list
  with open(word_list_path, 'r') as file:
    word_list = set(file.read().splitlines())

  # Apply the changes from the diff file
  with open(diff_path, 'r') as file:
    for line in file:
      line = line.strip()
      if line.startswith('+'):
        word_list.add(line[1:])
      elif line.startswith('-'):
        word_list.discard(line[1:])

  # Write the updated word list back to the file
  with open(word_list_path, 'w') as file:
    file.write('\n'.join(sorted(word_list)))

if __name__ == "__main__":
  word_list_file = 'dictionaries/word-lists/vivi/english.txt'
  changes_dir = 'changes'

  for diff_file in os.listdir(changes_dir):
    if diff_file.endswith('.diff'):
      apply_diff(word_list_file, os.path.join(changes_dir, diff_file))
      os.remove(os.path.join(changes_dir, diff_file))
