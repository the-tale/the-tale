#! /bin/sh

LOGS_DIR="${HOME}/logs"

case "$1" in
start)
echo "Starting game workers..."
. ${HOME}/env/bin/activate && nohup python -u ./manage.py game_highlevel 2>&1 1>>${LOGS_DIR}/game_highlevel.log &
. ${HOME}/env/bin/activate && nohup python -u ./manage.py game_logic 2>&1 1>>${LOGS_DIR}/game_logic.log &
. ${HOME}/env/bin/activate && nohup python -u ./manage.py game_supervisor 2>>&1 1>${LOGS_DIR}/game_supervisor.log &
. ${HOME}/env/bin/activate && nohup python -u ./manage.py game_turns_loop 2>&1 1>>${LOGS_DIR}/game_turns_loop.log &
;;

stop)
echo "Stop game workers..."
pkill -f game_turns_loop
pkill -f game_supervisor
pkill -f game_logic
pkill -f game_highlevel
;;

status)
echo "Not implemented yet"
;;
*)

echo "Usage: ./scripts/workers {start|stop|status}"
exit 1

esac

exit 0
