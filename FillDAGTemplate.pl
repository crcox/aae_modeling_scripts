#!/usr/bin/env perl
use YAML::XS;
use String::Scanf;
use Text::Template;
use Cwd 'abs_path';

my $template = @ARGV[0];
my $jobdir   = @ARGV[1];

my $template = Text::Template->new(SOURCE => $template)
  or die "Couldn't construct template: $Text::Template::ERROR";

if ( @ARGV > 2 ) {
  my $config   = @ARGV[2];
  open my $fh, '<', $config
    or die "can't open config file: $!";

  # convert YAML file to perl hash ref (and cast to a hash)
  %vars = %{YAML::XS::LoadFile($fh)};
  $vars{ "UNIQUE" } = $jobdir;
  $vars{ "JOBDIR" } = abs_path($jobdir);
  $vars{ "SUBMITFILE" } = abs_path("$jobdir/process.sub");
} else {
  %vars = (
    UNIQUE => $jobdir,
    JOBDIR => abs_path($jobdir),
    SUBMITFILE => abs_path("$jobdir/process.sub")
  );
}

# Fill in the template
my $result = $template->fill_in(HASH => \%vars);

# If all went well, print the template to stdout
if (defined $result) { print $result }
else { die "Couldn't fill in template: $Text::Template::ERROR" }
