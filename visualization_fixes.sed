# Fix 1: Make node labels larger and brighter
s/\.attr("font-size", 10)/\.attr("font-size", 14)/g
s/\.attr("fill", "#aaa")/\.attr("fill", "#e0e0e0")/g

# Fix 2: Remove connect button from HTML
s/<button id="connectBtn">Connect<\/button>//g

# Fix 3: Change status div positioning (button removed)
s/<div class="status disconnected" id="status">Disconnected<\/div>/<div class="status disconnected" id="status">Select a graph<\/div>/g
