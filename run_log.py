import subprocess

log_file = "log.txt"
ps_cmd = (
    "chcp 65001 > $null; "
    "[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false); "
    "[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false); "
    "$OutputEncoding = [System.Text.UTF8Encoding]::new($false); "
    f"Get-Content -Encoding utf8 '{log_file}' -Wait -Tail 50"
)

cmd = [
    "powershell",
    "-NoExit",
    "-Command",
    ps_cmd
]

subprocess.run(cmd)