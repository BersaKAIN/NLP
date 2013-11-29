#!/bin/env perl

@a = qw(0 1 2 3 4 5 6 7 8 9 a b c d e f g h i j k l m n o p q r s t u v w x y z A B C D E F G H I J K L M N O P Q R S T U V W X Y Z ! \" # $ % & ' ( ) * + , - . / : ; < = > ? @ \[ \\\\ \] ^ _ ` { | } ~);
push(@a, " ");
push(@a, "\\n");
push(@a, "\\t");
push(@a, "\\r");

# foreach $key (@a){
#     push(@sr,"(\"$key\" : \"$key\")");
# }
# print join(' | ', @sr);

@rw=(); $srw=''; @su=(); @rewrites=();
foreach $key (@a){
    # foreach $key2 (@a){
    # 	if($key eq $key2){ 
    # 	    next;
    # 	} else{
    # 	    push(@rw, "\"$key2\"");
    # 	}
    # }
    push(@rewrites,"(\"[sub]\" : (" . join(' | ', @rw) . ")) <0.5>");
}
print join(' | ', @rewrites);
