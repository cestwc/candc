#!/bin/sh

PROGRAM=`basename $0`

if [ ! $# == 1 ]; then
  (
    echo "$PROGRAM: incorrect number of command line arguments"
    echo "usage: $PROGRAM <work>"
    echo "work:  <work> is where the data should be stored"
  ) > /dev/stderr;
    exit 1;
fi

WORK=$1

BIN=bin
SCRIPTS=src/scripts/ccg
DATA=src/data/ccg
CCGBANK=gold/CCGbank

SUPER=$WORK/super
GOLD=$WORK/gold
GEN=$WORK/generated
POS=$WORK/pos
SUPER=$WORK/super
OUT=$WORK/cl07

BETA="0.075,0.03,0.01,0.005,0.001"
CUTOFF="20,20,20,20,150"
MAXCATS="1000000"
FWDBEAM="0.1"

DEPS=model_deps
DERIVS=model_derivs
DERIVS_REV=model_derivs_rev
HYBRID=model_hybrid
