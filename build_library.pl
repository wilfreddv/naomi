#!/usr/bin/perl -w

use strict;

my( $SOURCELIST, $did_assemble, $srcpath, $srcfile, $srcmod,
    $targetfile, $targetmod, @TARGETLIST, $command );

$SOURCELIST = "sources.txt";
-f $SOURCELIST ? open SOURCES, $SOURCELIST : die "No $SOURCELIST";

`mkdir -p build`;

$did_assemble = 0;
while( $srcpath = <SOURCES> ) {
    foreach $srcfile ( glob($srcpath) ) {
        chomp($srcfile);
        $targetfile = $srcfile =~ s/s$/o/r;
        $targetfile =~ s/.*\///;
        $targetfile = "build/$targetfile";
        $srcmod = -M $srcfile;
        $targetmod = -M $targetfile;

        if( !defined $srcmod ) {
            print "Skipping file: $srcfile\n";
            next;
        }

        if( !defined $targetmod || $targetmod > $srcmod ) {
            $command = "nasm -Ilibnaomi -gdwarf -felf64 -o $targetfile $srcfile";

            print "$command\n";
            `$command`;
            $did_assemble = 1;
            push(@TARGETLIST, $targetfile);
        }
    }
}

close SOURCES;

my( $lib, $libts, $objs );
$libts = -M "libnaomi.a";

if( $did_assemble || !defined $libts ) {
    $objs = join(" ", @TARGETLIST);
    $command = "ar rU libnaomi.a $objs";
    print "$command\n";
    `$command`;
}
