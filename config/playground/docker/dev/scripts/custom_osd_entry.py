#!/usr/bin/python

import os
import sys

SOURCE_FILE = "/opt/opensearch-dashboards/extra_config/osd.yml"
TARGET_FILE = "/usr/share/opensearch-dashboards/config/opensearch_dashboards.yml"

def update_config():
    s_keys = set()
    nc = []
    with open(SOURCE_FILE, "r") as s:
        for r in s:
            if not r.strip():
                continue
            nc += [r]
            kv = r.split(":")
            if len(kv) < 2 or r.strip().startswith("#"):
                continue
            s_keys.add(kv[0])

    if not nc:
        return

    nt = []
    with open(TARGET_FILE, "r") as t:
        for r in t:
            kv = r.split(":")
            if len(kv) < 2 or r.strip().startswith("#"):
                nt += [r]
            elif kv[0] in s_keys:
                # skip to use src value
                continue
            else:
                nt += [r]

    with open(TARGET_FILE, "w") as f:
        f.write("\n".join(nt + nc))

def run():
    if os.path.exists(SOURCE_FILE):
        update_config()

    for i in range(1, len(sys.argv)):
        os.system("/opt/opensearch-dashboards/scripts/install-plugins.sh " + sys.argv[i])

    os.system("./opensearch-dashboards-docker-entrypoint.sh opensearch-dashboards")

if __name__ == "__main__":
    run()