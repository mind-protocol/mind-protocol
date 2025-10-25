# This script launches 6 PowerShell tabs, arranged in 3 vertical panes,
# using the Windows Terminal (wt.exe) command-line interface.

# --- Pane 1 (Left Column) ---
# 1. Start Pane 1, Tab 1 (Ada)
$command = "wt.exe -d 'C:\Users\reyno\mind-protocol\consciousness\citizens\ada' powershell.exe -NoExit -Command 'claude --dangerously-skip-permissions --debug --add-dir ../../../ --continue'"

# --- Pane 2 (Middle Column) ---
# 2. Split the first pane vertically to create Pane 2, Tab 1 (Luca)
$command += " ; split-pane -V -d 'C:\Users\reyno\mind-protocol\consciousness\citizens\luca' powershell.exe -NoExit -Command 'claude --dangerously-skip-permissions --debug --add-dir ../../../ --continue'"

# --- Pane 3 (Right Column) ---
# 3. Split the second pane vertically to create Pane 3, Tab 1 (Marco)
$command += " ; split-pane -V -d 'C:\Users\reyno\mind-protocol\consciousness\citizens\marco' powershell.exe -NoExit -Command 'claude --dangerously-skip-permissions --debug --add-dir ../../../ --continue'"

# --- Add the 2nd Tabs to Each Pane ---
# 4. Go back to Pane 1 (index 0) and add Tab 2 (Felix)
$command += " ; focus-pane -t 0 ; new-tab -d 'C:\Users\reyno\mind-protocol\consciousness\citizens\felix' powershell.exe -NoExit -Command 'claude --dangerously-skip-permissions --debug --add-dir ../../../ --continue'"

# 5. Go to Pane 2 (index 1) and add Tab 2 (Piero)
$command += " ; focus-pane -t 1 ; new-tab -d 'C:\Users\reyno\mind-protocol\consciousness\citizens\piero' powershell.exe -NoExit -Command 'claude --dangerously-skip-permissions --debug --add-dir ../../../ --continue'"

# 6. Go to Pane 3 (index 2) and add Tab 2 (Victor)
$command += " ; focus-pane -t 2 ; new-tab -d 'C:\Users\reyno\mind-protocol\consciousness\citizens\victor' powershell.exe -NoExit -Command 'claude --dangerously-skip-permissions --debug --add-dir ../../../ --continue'"

# Execute the entire command chain
Invoke-Expression $command