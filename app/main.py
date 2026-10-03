import argparse
import analyze_executer

# 引数受け取り
parser = argparse.ArgumentParser()
parser.add_argument("--mode", choices=["desc", "rename"], required=True)
args = parser.parse_args()

if args.mode == "desc":
    analyze_executer.execute()
elif args.mode == "rename":
    analyze_executer.rename_file()
else:
    raise ValueError(f"Invalid mode: {args.mode}")