
import re

file_path = r"c:\Users\3dmax\Libriscribe\manuscript_original.md"

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

print(f"Total lines: {len(text.splitlines())}")

# Find all lines with "Chapter"
print("\n--- Lines containing 'Chapter' ---")
lines = text.splitlines()
for i, line in enumerate(lines):
    if "Chapter" in line:
        print(f"{i+1}: {line}")

# Test DocumentParser logic
print("\n--- DocumentParser Logic ---")
chapter_pattern = r'(?i)(chapter\s+\d+|#\s+chapter\s+\d+)'
matches = re.findall(chapter_pattern, text)
print(f"Matches found: {len(matches)}")
for m in matches:
    print(f"Match: '{m}'")
