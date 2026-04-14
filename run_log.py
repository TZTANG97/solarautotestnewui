import subprocess

log_file = "log.txt"

cmd = [
    "powershell",
    "-NoExit",
    "-Command",
    f"Get-Content {log_file} -Wait -Tail 50"
]

subprocess.run(cmd)