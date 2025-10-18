import sys

# Read the file
with open('visualization_server.py', 'r') as f:
    content = f.read()

# Fix the header parsing - FalkorDB header is list of [type, name], not objects
# Change: [col.name for col in X.header]
# To: [col[1] for col in X.header]

content = content.replace(
    '[col.name for col in nodes_result.header]',
    '[col[1] for col in nodes_result.header]'
)

content = content.replace(
    '[col.name for col in links_result.header]',
    '[col[1] for col in links_result.header]'
)

content = content.replace(
    '[col.name for col in entities_result.header]',
    '[col[1] for col in entities_result.header]'
)

# Write back
with open('visualization_server.py', 'w') as f:
    f.write(content)

print("Fixed query result parsing")
