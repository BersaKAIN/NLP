chunker.far: chunker.grm byte.far tags.far
	thraxcompiler --save_symbols --input_grammar=$< --output_far=$@

byte.far: byte.grm 
	thraxcompiler --save_symbols --input_grammar=$< --output_far=$@

tags.far: tags.grm 
	thraxcompiler --save_symbols --input_grammar=$< --output_far=$@

clean:
	rm -f byte.far tags.far
