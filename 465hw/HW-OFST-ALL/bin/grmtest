#!/bin/bash

# Usage: grmtest <grm_file> <transducer_name> [max_number_output_lines] [symbol_table]
# Test FST <transducer_name> from <grm_file>. Generate 
# [max_number_output_lines] (default: 1), using [symbol_table] (default: byte)
# as necessary to properly encode/decode from FST.

name=$1
if [[ -z $name ]]; then
    echo Usage: grmtest grm_file transducer_name [ max_number_output_lines ] [ symbol_table ]
    exit
fi
rule=$2
if [[ -z $rule ]]; then
    echo Error: Please specify the name of an FSM to test from $name.
    exit
fi
numout="$3"
if [[ -z $numout ]]; then
    numout=100;
fi
symtab="$4"
if [[ -n $symtab ]]; then
    symtab="--input_mode=$symtab --output_mode=$symtab"
fi

if [[ $name =~ ^(.+)[\.]([^\.]*)$ ]]; then
    name=${BASH_REMATCH[1]};
fi

thraxmakedep --save_symbols $name.grm && make && thraxrewrite-tester --print_rules=false --far=$name.far $symtab --noutput=$numout --rules=$rule
