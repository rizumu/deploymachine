#!/bin/bash
# http://gist.github.com/537145

gunicorn path.to.app &

MASTER_PID=$!
trap "kill $MASTER_PID; exit" INT TERM EXIT

while true
do
    sleep 1
    inotifywait -r -q -e modify -e create -e delete -e close_write \
        --exclude=".*\.(swp|swx)" ..
    kill -HUP $MASTER_PID
done
