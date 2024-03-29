PiCaS snakemake profile
-----------------------

The Pitch-Catch System, or PiCaS, work management tool that can work large amounts of jobs on a heterogeneous compute infrastructure. It  is developed by [SURF](http://www.surf.nl) and relies on a CouchDB server to keep track of the work itself. The user documentation can be found [here](https://doc.grid.surfsara.nl/en/latest/Pages/Practices/picas/picas_overview.html), and the client source code with examples [here](https://github.com/sara-nl/picasclient/).

Integrating PiCaS (or picas) with snakemake allows you to send the work that snakemake creates from a Snakefile to any heterogeneous compute infrastructure that is connected to your picas database containing the work.

Setup
=====

This profile will allow snakemake to send its work to the CouchDB server, while the picas client (running on a worker node) will contact the server and perform the work stored in the DB.

To use the picas profile, in general you need three machines:

1. A machine running snakemake
2. A machine running the CouchDB server
3. A machine running the picas client

You can set up this screnario any way you want, you can even run the DB in a container, while running the client and snakemake on the same machine. In this case 1., 2. and 3. are the same machine. Usually, however, the DB is on a seperate machine and the client runs on a worker machine (slurm, grid, etc.).

## Prerequisites

To run snakemake with picas you need to setup the 3 components mentioned above.

### Install snakemake
Install snakemake following their documentation as described [here](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html).

### Set up CouchDB
Set up a CouchDB in your compute infrastructure as described in the [PiCaS documentation](https://doc.grid.surfsara.nl/en/latest/Pages/Practices/picas/picas_overview.html#picas-server-1).

### Install picasclient
Install the PiCaS client on the machine that will be performing the work, like the filesystem of a cluster, such that a worker node in the cluster can run the picas client. For the Grid, you have to use the sandbox or CVMFS to distribute the code. The installation instructions for the client can be found [here](https://github.com/sara-nl/picasclient/).

As the code generated by snakemake contains calls to snakemake, picas will need to be installed into the (virtual, conda, mamba) environment that runs snakemake. For the standard mamba installation, activate it with:

```
mamba activate snakemake
```

To ensure you are installing it with the proper pip into the mamba environment, check:

```
which pip
>>> ~/mambaforge/envs/snakemake/bin/pip
```

And see that you will install picasclient into the mamba environment. Now follow the picasclient installation instructions given above to install the client in the relevant environment.


## Deploy profile

To deploy this snakemake profile, on the machine that you run Snakemake, first ensure cookiecutter is available:

```
pip install cookiecutter

```

Then install the profile with:

```
mkdir -p ~/.config/snakemake
cd ~/.config/snakemake
cookiecutter https://github.com/sara-nl/picas-profile.git
```

When asked for the PiCaS information, insert the information needed to connect to your PiCaS instance. NB: The `no_shared_fs` is used for Grid storage. If you have no shared file-system, like on a laptop or mounted storage on a compute cluster, set this to true and input the necessary information to approach your storage cluster. The default protocol is set to gfal2, but this can be overriden if needed.

Running
=======

## Run snakemake

The snakemake example is used to showcase the picas workflow.

First make sure you can run the Basic Workflow as given in the [snakemake documentation](https://snakemake.readthedocs.io/en/stable/tutorial/basics.html).
Once you have the basic snakemake example running and the whole stack given in de [Setup](#Setup) is installed, you can now run the example with:

```
snakemake --profile picas -j N ...
```

where N is the number of jobs you want to run in parallel, for the Basic example, you only have to use up to 3 as there are 3 parallel steps in the snakemake graph (A, B and C in the samples).

## Run picasclient

You will notice the snakemake steps stall. This is because there is no client running to execute the code that is sent to the DB. 
In parallel to snakemake communicating with the DB, you have to run a job that performs the work that is stored in the DB. 
You can start a job by running the `local-example.py` from the `picasclient` examples folder. The picasclient documentation describes how to do this. 
Ensure that the environment that the picasclient is run in also contains snakemake and all dependencies needed for the code, to ensure the code from snakemake can actually be executed.

The picasclient will run for a short time by default before stopping if there is no work to be done. To run the whole snakemake example, set the time the ExampleActor runs to 600 seconds (10 minutes) or similar by changing the `time_elapsed` argument value. 

Before running, the client needs to know about your picas credentials, so link them with:

```
ln -s ~/.config/snakemake/picas/picasconfig.py ~/picasclient/examples/picasclient.py
```

If the file already exists, replace it with the link to avoid duplicate information. Now run the example with:

```
python local-example.py
``` 

The example will start a processing script that fetches the tokens one by one from the DB and evaluates the code that snakemake has written in the token. By doing so the snakemake steps are performed, and the profile communicates state of the tokens in the DB back to snakemake. On subsequent steps, snakemake will send the next tokens to the DB and so the processing continues.

Having such a DB with tokens allows you to run the picasclient on any compute infrastructure, while having control over the tokens in the DB before they are fetched by the client. You can scale up, run in parallel or move your execution to any combination of systems you prefer.

## Running on the Grid

To run the Snakemake turorial example on the grid using PiCaS, there are some prerequisites. It helps to be up to speed with the full snakemake tutorial, ensure you understand the example given [here](https://snakemake.readthedocs.io/en/stable/tutorial/tutorial.html).

First, setup the snakemake stack and profile as described above on a Grid UI machine. Snakemake will be run from this machine, which then pushes the work to the CouchDB back-end. You can use the usual Snakefile from the snakemake tutorial for steering snakemake.
This work is subsequently pulled by a pilot job on the Grid, performed, and stored on Grid Storage. Beware that your picasconfig needs to have set the `no-shared-fs` settings in the profile, otherwise your grid job can not approach the Grid Storage Element.

Second, a CVMFS instance needs to be available for providing the software like the snakemake calls that are done on the Grid Compute Element. To distribute the snakemake code, connect to a CVMFS distribution machine and create a new conda/mamba environment in `/cvmfs/path/to/your/space`. For brevity, here are example steps for a simple snakemake environment that should have all the components needed to run on the Grid:

```
conda create -c conda-forge -c bioconda -n snakemake-picas snakemake
conda install -c bioconda samtools
conda install -c bioconda bcftools
conda install python-gfal2
```

Gfal2 is used for interacting with Grid Storage. Now publish the conda environment with `publish-my-software` or equivalent and wait until its available on CVMFS.

If you are having trouble installing your environment on CVMFS, we suggest reading the README for the [grid profile](https://github.com/Snakemake-Profiles/surfsara-grid). (NB: this execution of this profile is currently broken, but the Setup is fine.)

Third, set up the data needed for the snakemake example on your grid storage, see the tutorial linked at the top of this subsection.

NB: Unfortunately, in the first step of the snakemake example, the `genome.fa.*` files need to be available to the `bwa mem` and/or `samtools` commands, so this step has to be done locally and the output has to be uploaded to your storage too. As these files are not explicitly called in the snakemake example, the job will not explicitly fetch them from storage, and thus the files are not available and `bwa mem` and/or `samtools` fail.

The data will look something like this on your storage cluster:

```
rclone ls token:/path/to/snakemake/files/

   234112 data/genome.fa
     2598 data/genome.fa.amb
       83 data/genome.fa.ann
   230320 data/genome.fa.bwt
       18 data/genome.fa.fai
    57556 data/genome.fa.pac
   115160 data/genome.fa.sa
  5752788 data/samples/A.fastq
  5775000 data/samples/B.fastq
  5775000 data/samples/C.fastq
  2200439 mapped_reads/A.bam
  2203496 mapped_reads/B.bam
```

We will distribute the `plot-quals.py` through the sandbox to shortly show how the sandbox works. Also the Snakefile is needed in the sandbox, so create two links, one to each of the files:

```
cd /path/to/picasclient/
cd examples/grid-sandbox
ln -s  /path/to/snakemake/scripts/plot-quals.py plot-quals.py
ln -s  /path/to/snakemake/Snakefile Snakefile
```

Now the `jdl` file will send these files (and everything else mentioned in the sandbox) to the machine executing the commands.

To properly call `plot-quals.py` on the Grid, the Snakefile as given in the snakemake example has to be updated. On the grid the `scripts` folder will not exist in the sandbox, as the files are placed in the root of the Grid machine. So remove the `scripts` from the Snakefile: `"scripts/plot-quals.py"` becomes `"plot-quals.py"`

Now you need to do two things after one another to get Snakemake to run on the Grid:

1. Start a job on the grid running the picas client
2. Start snakemake using the picas profile installed before

```
cd /path/to/picasclient/examples
dirac-wms-job-submit snakemake.jdl
```

Now wait until this job is running. The picas client will wait for a time for jobs in the DB before exiting. If the exit happens too quickly, change the `time_elapsed` in `example/local-example.py` to something more managable than the default 30 seconds (for example, 10 minutes).

Once the Grid job is running, start snakemake:

```
snakemake --profile picas -j 1
```

If all is set well, you will see the regular snakemake logging output in green. After the processing is finished, you will find the output files in your Grid storage:

```
rclone ls token:/path/to/snakemake/files/
  2183986 sorted_reads/A.bam
      344 sorted_reads/A.bam.bai
  2188317 sorted_reads/B.bam
      344 sorted_reads/B.bam.bai
  2200439 mapped_reads/A.bam
  2203496 mapped_reads/B.bam
    13008 plots/quals.svg
    69995 calls/all.vcf
   234112 data/genome.fa
     2598 data/genome.fa.amb
       83 data/genome.fa.ann
   230320 data/genome.fa.bwt
       18 data/genome.fa.fai
    57556 data/genome.fa.pac
   115160 data/genome.fa.sa
  5752788 data/samples/A.fastq
  5775000 data/samples/B.fastq
  5775000 data/samples/C.fastq
```

And you have succesfully ran snakemake through picas, where the jobs are fetched and executed on a Grid Compute Element.
