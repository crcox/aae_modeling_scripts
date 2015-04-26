#!/usr/bin/env perl

use YAML::XS ;
use String::Scanf ;
use Text::Template ;
use Cwd 'abs_path' ;

my $template = @ARGV[0] ;
my $config   = @ARGV[1] ;

my $template = Text::Template->new(SOURCE => $template)
  or die "Could not construct template: $Text::Template::ERROR" ;

open my $fh, '<', $config
  or die "Could not open config file: $!" ;

# Convert YAML file to perl hash ref (and cast to a hash)
my %vars = %{ YAML::XS::LoadFile($fh) } ;

# Create extra/derivative variables
$vars{ "ReportInterval" } = $vars{ "UpdatesPerCall" } / 10 ;

# Fill in the template
my $result = $template->fill_in(HASH => \%vars, DELIMITERS=>['<<<','>>>']) ;

# If all went well, print the template to stdout
if (defined $result) { print $result }
else { die "Could not fill in template: $Text::Template::ERROR" } ;
