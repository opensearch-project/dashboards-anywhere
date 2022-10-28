#!/bin/bash
set -e

echo "Start plugin installation"
cnt=0

for var in "$@"
do
  /usr/share/opensearch-dashboards/bin/opensearch-dashboards-plugin install $var
  cnt=$((cnt+1))
done
echo "Finished installing $cnt plugins"