#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Usage: $0 blue|green"
    echo "Current backend:"
    grep -E "server 127.0.0.1" /etc/nginx/conf.d/lacrei-saude.conf
    exit 1
fi

TARGET="$1"
CONF="/etc/nginx/conf.d/lacrei-saude.conf"

if [ "$TARGET" = "blue" ]; then
    NEW_SERVER="server 127.0.0.1:8001;"
elif [ "$TARGET" = "green" ]; then
    NEW_SERVER="server 127.0.0.1:8002;"
else
    echo "Unknown target: $TARGET. Use 'blue' or 'green'"
    exit 1
fi

# Backup current config
cp "$CONF" "$CONF.bak.$(date +%s)"

# Update upstream server
sed -i "s/server 127.0.0.1:[0-9]*;/$NEW_SERVER/" "$CONF"

# Test nginx config
nginx -t

# Reload nginx
systemctl reload nginx

echo "Switched backend to $TARGET"
echo "Current config:"
grep -E "server 127.0.0.1" "$CONF"
