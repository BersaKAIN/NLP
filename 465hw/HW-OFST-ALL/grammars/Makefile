noisy.far: noisy.grm byte.far entrain.fst entrain.sym entrain.alpha entrain.alpha entrain.alpha
	thraxcompiler --save_symbols --input_grammar=$< --output_far=$@

byte.far: byte.grm 
	thraxcompiler --save_symbols --input_grammar=$< --output_far=$@

clean:
	rm -f byte.far
