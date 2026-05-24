import os, json

ws = r"C:\Users\Administrator\.openclaw\workspace"
files = ["AGENTS.md","SOUL.md","TOOLS.md","USER.md","IDENTITY.md","BOOTSTRAP.md","HEARTBEAT.md","MEMORY.md"]
total = 0
for f in files:
    p = os.path.join(ws, f)
    if os.path.exists(p):
        sz = os.path.getsize(p)
        total += sz
        est = sz // 3
        print(f"{f:20s} {sz:6d} bytes  ~{est} tokens")
print(f"{'TOTAL':20s} {total:6d} bytes  ~{total//3} tokens")
