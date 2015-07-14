#!/usr/bin/env perl
use strict;
use warnings;
use FindBin::libs;
use WriteFile::Unique;
use YAML::XS ;
use String::Scanf ;
use Text::Template ;

my $templatefile = $ARGV[0] ;
my $config   = $ARGV[1] ;

my $template = Text::Template->new(SOURCE => $templatefile, DELIMITERS=>['<%','%>'])
  or die "Could not construct template: $Text::Template::ERROR" ;

open my $fh, '<', $config
  or die "Could not open config file: $!" ;

# Convert YAML file to perl hash ref (and cast to a hash)
my @arr = YAML::XS::LoadFile($fh) ;
#for my $record (@arr) {
#  print "$record->{NetworkFile}:\n";
#  for my $subrecord (@{$record->{ProcFiles}}) {
#    print "\t$subrecord\n";
#  }
#}

my $i = 0;
for my $phase (@arr) {
  $i++;
  # Create extra/derivative variables
#  $phase->{ReportInterval} = $phase->{UpdatesPerCall} / 10 ;

  # Fill in the template
  my $result = $template->fill_in(HASH => $phase) ;

  my $filename = sprintf("trainscript_phase%02d.tcl", $i);
  open $fh, '>', $filename
    or die "Could not open file for writing: $!";

  print $fh $result;
};
# If all went well, print the template to stdout
#if (defined $result) { print $result }
#else { die "Could not fill in template: $Text::Template::ERROR" } ;
