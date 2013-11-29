#!/usr/bin/perl

# Usage: perl makeSymbolLibrary.pl <symbol table name>
# Prints to STDOUT Thrax code to create a symbol table.

# Each two-column line read from STDIN must contain the
# multicharacter (ASCII) symbol to be encoded. Spaces cannot be
# included. The second column can be anything.

$sym = $ARGV[0];
print "syms = SymbolTable['$sym'];\n";


$s=''; $c=0; $e=0;
while(<STDIN>){
    chomp;
    if(/^(\S+)\s*(\S+)$/){
	$w=$1;
	# create various escapes
	$w =~ s/\\/\\\\/g;
	$w =~ s/\[/\\\[/g;
	$w =~ s/\]/\\\]/g;
	$w =~ s/"/\\"/g;
	$s .= "\"$w\".syms | ";
	$c++;
	if($c % 1000 == 0){
	    $s =~ s/\|\s*$//;
	    chomp($s);
	    print "e${e} = Optimize[ $s ];\n";
	    $e++;
	    $s='';
	}
    }
    
}
$s =~ s/\|\s*$//;
chomp($s);
print "e${e} = Optimize[ $s ];\n";
$e++;
$s='';
print "export Alphabet = Optimize[\n";
for($i=0;$i<$e;$i++){
    $s .= "e${i} | ";
}
$s =~ s/\| $//;
chomp($s);
print "$s];\n";
