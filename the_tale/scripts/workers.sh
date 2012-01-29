#! /bin/sh

PID_FILE="/var/run/the-tale-workers.pid"
LOGS_DIR="${HOME}/logs"

# test -f /lib/lsb/init-functions || exit 1
# . /lib/lsb/init-functions

case "$1" in
start)
echo "Starting game workers..."
. ../../env/bin/activate && nohup python -u ./manage.py game_supervisor 2>&1 1>${LOGS_DIR}/game_supervisor.log &
. ../../env/bin/activate && nohup python -u ./manage.py game_logic 2>&1 1>${LOGS_DIR}/game_logic.log &
. ../../env/bin/activate && nohup python -u ./manage.py game_highlevel 2>&1 1>${LOGS_DIR}/game_highlevel.log &
;;

stop)
echo "Stop game workers..."
pkill -f game_supervisor
pkill -f game_logic
pkill -f game_highlevel
;;

status)
echo "Not implemented yet"
;;
*)

echo "Usage: /etc/init.d/boinc {start|stop|status}"
exit 1

esac

exit 0