dactyls.far: dactyls.grm byte.far arpabet.far ../symbol_tables/arpabet.sym ../data/cmumini.txt ../data/cmumini.txt
	thraxcompiler --save_symbols --input_grammar=$< --output_far=$@

byte.far: byte.grm 
	thraxcompiler --save_symbols --input_grammar=$< --output_far=$@

arpabet.far: arpabet.grm ../symbol_tables/arpabet.sym
	thraxcompiler --save_symbols --input_grammar=$< --output_far=$@

clean:
	rm -f byte.far arpabet.far
