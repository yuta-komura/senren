#!/bin/sh

SCRIPT_DIR=$(
    cd $(dirname $0)
    cd ../
    pwd
)

. ${SCRIPT_DIR}/venv/bin/activate

python ${SCRIPT_DIR}/initialize.py

python ${SCRIPT_DIR}/backtest_entry.py &

python ${SCRIPT_DIR}/backtest_entry_normalize.py &

python ${SCRIPT_DIR}/backtest_entry_analysis_tuning.py &
python ${SCRIPT_DIR}/entry.py &

python ${SCRIPT_DIR}/entry_to_position.py &

wait
