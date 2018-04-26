#!/usr/bin/env bash

run_worker() {
    local queue=$1

    TERM_CHILD=1 BACKGROUND=yes QUEUES=${queue} bundle exec rake resque:work &&
        echo "[RESQUE] Resque worker listening on queue '${queue}'"
}

run_workers() {
    echo "[RESQUE] Starting new Resque workers"
    pushd ${THISSCRIPTDIR} > /dev/null
    if [[ -z ${NUMWORKERS} ]]; then
        run_worker ${QUEUE}
    else
        for i in $(seq 0 $((NUMWORKERS - 1))); do
            run_worker ${QUEUE}${i}
        done
    fi
    popd > /dev/null
}

# script starts here
if [[ $# -lt 1 || $# -gt 2 ]]; then
    echo "Usage: $0 queue_name [num_workers]"
    exit 1
fi

# vars
THISSCRIPT=$(readlink -f ${BASH_SOURCE})
THISSCRIPTDIR=$(dirname ${THISSCRIPT})
QUEUE=$1
if [[ $# -eq 2 ]]; then
    NUMWORKERS=$2
else
    NUMWORKERS=""
fi

# main
${THISSCRIPTDIR}/stop_resque.sh ${QUEUE}
run_workers