#!/usr/bin/python

import os
import sys

def run():
    SOURCE_FILE = "/opt/opensearch-dashboards/extra_config/osd.yml"
    TARGET_FILE = "/usr/share/opensearch-dashboards/config/opensearch_dashboards.yml"

    s_keys = set()
    nc = []
    with open(SOURCE_FILE, "r") as s:
        for r in s:
            nc += [r]
            kv = r.split(":")
            if len(kv) < 2 or r.strip().startswith("#"):
                continue
            s_keys.add(kv[0])

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

    for i in range(1, len(sys.argv)):
        os.system("/opt/opensearch-dashboards/scripts/install-plugins.sh " + sys.argv[i])

    os.system("./opensearch-dashboards-docker-entrypoint.sh opensearch-dashboards")

if __name__ == "__main__":
    run()