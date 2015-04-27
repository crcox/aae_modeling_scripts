package WriteFile::Unique;

use Fcntl;
use Errno;
use IO::File;

sub open {

    my $file = shift || '';
    unless ($file =~ /^(.*?)(\.[^\.]+)$/) {
        print "Bad file name: '$file'\n";
        return;
    }
    my $io;
    my $seq  = '';
    my $base = $1;
    my $ext  = $2;
    until (defined ($io = IO::File->new($base.$seq.$ext
                                   ,O_WRONLY|O_CREAT|O_EXCL))) {

        last unless $!{EEXIST};
        $seq = '_0' if $seq eq '';
        $seq =~ s/(\d+)/$1 + 1/e;
    }

    return $io if defined $io;

}

1;
