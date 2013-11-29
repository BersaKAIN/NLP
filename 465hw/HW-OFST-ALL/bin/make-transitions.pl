#!/usr/bin/perl

# Usage: perl make-transitions.pl 
# Read space-separated tricolumn text from STDIN, where each column is
# <count> <tag/label/hidden state> <word/emission>
# indicating how many times <word> was generated from <state>.
# Output: Thrax code that encodes transitions as WFST (to be used in HMMs).
# Final WFST is called EMISSIONS.

# Assumes the symbol tables words.sym and tags.sym can be found.
# Note that, as of 15 August 2013, this was not fully tested/integrated, 
# since the HMM question was scrapped for the Fall 2012 assignment.
# Things may have changed that break this! 

%h=();
$ts='tagSym';
$ws='wordSym';
while(<STDIN>){
    chomp;
    /^\s*(\S+)\s*(\S+)\s*(\S+)\s*$/;
    $tran = "\"$2\".$ts\t\"$3\".$ws";
    $h{$tran} = defined($h{$tran})?($h{$tran} + 1):1;
    $tag = "\"$2\".$ts";
    $c{$tag} = defined($c{$tag})?($c{$tag} + $1):($1);    
    
}

print "$ts = SymbolTable['tags.sym'];\n";
print "$ws = SymbolTable['words.sym'];\n";

$s='';
$count=0; $enum=0; $hit=0;
foreach $k (keys %h){
    @a=split(/\t/,$k);
    # make weights negative log-probabilities
    $weight = -log($h{$k}/$c{$a[0]});
    $s .= "($a[0] : $a[1] <$weight>) | ";

    $count+=1;
    if($count % 1000 == 0){
	$s =~ s/\|\s*$//;
	print "e${enum} = Optimize[$s];\n";
	$s='';
	$enum++;
	$hit=1;
    } else{ $hit=0;}
}
$s =~ s/\|\s*$//;
print "e${enum} = Optimize[$s];\n";
$enum++;

$s='';
for($i=0;$i<$enum; $i++){
    $s .= "e${i} | ";
}
$s =~ s/\|\s*$//;
print "export EMISSIONS = Optimize[$s];\n";
