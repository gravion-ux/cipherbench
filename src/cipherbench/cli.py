import argparse
import json
from pathlib import Path

from .benchmark import summarize


def main():
    p=argparse.ArgumentParser();p.add_argument("records",type=Path);a=p.parse_args()
    data=json.loads(a.records.read_text(encoding="utf-8"))
    print(json.dumps({"summary":summarize(data),"notice":"Results depend on hardware, provider, configuration and workload."},indent=2))
if __name__=="__main__":main()
