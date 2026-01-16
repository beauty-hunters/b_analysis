NJOBS=1000
NCORES=40
NEVENTSPERJOB=100000
MODE=mode2
SEEDSTART=10100
SEEDEND=$(($SEEDSTART + $NJOBS - 1))

# Create output and log directories if they do not exist
if [ ! -d b0_production/${MODE}/logs ]; then
    mkdir -p b0_production/${MODE}/logs
fi

nice -n 15 parallel -j $NCORES "root -l -q -b 'simulateB0production.cc($NEVENTSPERJOB, {}, \"$MODE\", \"b0_production/${MODE}/b0_pythia8_${MODE}_seed{}.root\")' > "b0_production/${MODE}/logs/log_b0_${MODE}_seed{}.txt" ::: $(seq $SEEDSTART $SEEDEND)
