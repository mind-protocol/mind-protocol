"""
Remove deprecated node types that have been replaced by universal types.
This script modifies complete_schema_data.py in-place.
"""

TYPES_TO_REMOVE = [
    'Memory', 'Person', 'Relationship', 'Personal_Goal', 'Personal_Pattern',  # N1
    'Human', 'AI_Agent', 'Decision', 'Task', 'Milestone', 'Risk', 'Metric', 'Best_Practice', 'Anti_Pattern',  # N2
    'Event', 'External_Person', 'Behavioral_Pattern', 'Reputation_Assessment', 'Psychological_Trait',  # N3
]

def remove_types_from_file(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    skip_until_next_type = False
    current_type = None
    brace_depth = 0

    for i, line in enumerate(lines):
        # Check if this line starts a new type definition
        if '"' in line and '": {' in line:
            # Extract type name
            type_name = line.split('"')[1]

            if type_name in TYPES_TO_REMOVE:
                print(f"Removing type: {type_name}")
                skip_until_next_type = True
                current_type = type_name
                brace_depth = 1  # We just saw the opening {
                continue

        if skip_until_next_type:
            # Count braces to know when type definition ends
            brace_depth += line.count('{') - line.count('}')

            # When we get back to 0, the type definition is complete
            if brace_depth == 0:
                skip_until_next_type = False
                current_type = None
                # Also skip the next line if it's just a comma and newline
                if i + 1 < len(lines) and lines[i+1].strip() == '':
                    continue
            continue

        new_lines.append(line)

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"\n✅ Removed {len(TYPES_TO_REMOVE)} deprecated types from {file_path}")

if __name__ == '__main__':
    remove_types_from_file('tools/complete_schema_data.py')
