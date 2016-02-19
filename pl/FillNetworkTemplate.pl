#!/usr/bin/env perl
use strict;
use warnings;
use FindBin::libs;
use WriteFile::Unique;
use YAML::XS;
use String::Scanf;
use Text::Template;

my $templatefile = $ARGV[0];
my $config   = $ARGV[1];

my $template = Text::Template->new(SOURCE => $templatefile, DELIMITERS => [qw(<% %>)])
  or die "Couldn't construct template: $Text::Template::ERROR";

open my $fh, '<', $config
  or die "can't open config file: $!";

# convert YAML file to perl hash ref (and cast to a hash)
my %vars = %{YAML::XS::LoadFile($fh)};
close $fh;

# Fill in the template
my $result = $template->fill_in(HASH => \%vars);

my $filename = "network.in";
open(my $fh, '>', $filename) or die "Could not open file '$filename' $!";
if (not defined $result) { die "Couldn't fill in template: $Text::Template::ERROR" };
print $fh $result;
close $fh;
