Running Lens on Condor
======================

There is a compiled copy of lens at: `/squid/crcox/Lens/LensCRC.tgz`.

In your wrapper script you will need to retrieve this file (e.g., with `wget`)
and extract it (with `tar xzf`).

Jobs on condor will typically be evicted every three days. It is possible that
a model will need longer than that to finish training. The solution is to set
up the jobs so that they will be able to pick up where they left off. The
easiest way to manage this is to not use folders when running the job on an
execute machine, and keep your weight files organized using pre- and
post-scripts that are run on the submit node.

The reason for this is condor will only transfer files, not directories, when a
job is evicted. Directories can be used on remote jobs, but they need to be
tar-ed (so that condor sees it as a file). In the case of eviction, you will
not be given a "last chance" to tar things up before you are booted from the
execute machine. The job is just terminated, and everything in the directory
will be left behind.

The solution is to write all files into the working directory. This way,
everything will be transfered, no matter what. The problem, of course,
organization. Directories are important. So, on the submit node job directories
could be set up with a `wt` directory for logging of model weights. But a
prescript will actually pull the specfic weights that need to go to the job,
and a post script will take all of the weight files that are returned and put
them back into the `wt` folder. In the end, organization is balanced with
condor functionality, and jobs will complete even if evicted.

The prescript
-------------
This is very simple.

```bash
	if [ -d wt ]; then
		# Copy the most current weight file into the current directory as init_0.wt
		cp -v $( ls -t wt/*.wt | head -1 ) "init_0.wt"
	fi
```

The postscript
--------------
Also very simple.

```bash
	# Make the weight directory if it does not exist
	if [ ! -d wt]; then
		mkdir wt
	fi
	# Move the weight files into it.
	mv -v *.wt wt/
```

The DAG
-------
This is where all the pieces get put together, and things actually get a little complicated. We need to ensure that the pre- and post-scripts are executed in the appropriate job directories.
