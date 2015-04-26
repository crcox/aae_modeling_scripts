#!/usr/bin/env perl
use YAML::XS;
use String::Scanf;
use Text::Template;
use Cwd 'abs_path';

my $template = @ARGV[0];
my $jobdir   = @ARGV[1];
my $config   = @ARGV[2];

%unitsize = ();
$unitsize{"KB"}=10e3;
$unitsize{"MB"}=10e6;
$unitsize{"GB"}=10e9;

my $template = Text::Template->new(SOURCE => $template)
  or die "Couldn't construct template: $Text::Template::ERROR";

open my $fh, '<', $config
  or die "can't open config file: $!";

# convert YAML file to perl hash ref (and cast to a hash)
my %vars = %{YAML::XS::LoadFile($fh)};

# Convert memory request to MB
($val,$unit) = sscanf("%d%s",$vars{ "request_memory" });
my $bytes = $val*$unitsize{ $unit } . "\n";
$vars{ "MEM_MB" } = $bytes / $unitsize{ "MB" };

# Convert disk request to KB
($val,$unit) = sscanf("%d%s",$vars{ "request_disk" });
my $bytes = $val*$unitsize{ $unit } . "\n";
$vars{ "DISK_KB" } = $bytes / $unitsize{ "KB" };

# Turn shared dir into an absolute path
$vars{ "SHAREDIR" } = abs_path($vars{ "SHAREDIR" });
$vars{ "WRAPPER" } = abs_path($vars{ "WRAPPER" });

# Create extra vars:
$vars{ "JOB" } = $jobdir;
$vars{ "JOBDIR" } = abs_path($jobdir);

# Fill in the template
my $result = $template->fill_in(HASH => \%vars);

# If all went well, print the template to stdout
if (defined $result) { print $result }
else { die "Couldn't fill in template: $Text::Template::ERROR" }
