#! /bin/sh

PID_FILE="/var/run/the-tale-workers.pid"
LOGS_DIR="${HOME}/logs"

# test -f /lib/lsb/init-functions || exit 1
# . /lib/lsb/init-functions

case "$1" in
start)
echo "Starting game workers..."
nohup python -u ./manage.py game_supervisor 2>&1 1>${LOGS_DIR}/game_supervisor.log &
;;

stop)
echo "Stop game workers..."
pkill -f game_supervisor
;;

status)
echo "Not implemented yet"
;;
*)

echo "Usage: /etc/init.d/boinc {start|stop|status}"
exit 1

esac

exit 0