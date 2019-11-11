# PAPPLY
Python wrapper to execute command line programs in parallel using multiprocessing.Pool

# Description
A very simple wrapper around python's multiprocessing to be able to
easily execute command line programs in parallel.
It's implementation is inspired by [GNU
Parallel](https://www.gnu.org/software/parallel/) and
[Apply](http://maverick.inria.fr/~Gilles.Debunne/Code/Apply).

The basic idea is that one does not have to change much to the original
command line to run tasks in parallel.

The first argument is interpreted as the command to execute multiple
times, all other arguments are used as the inputs to the command.

# Example usage
hello world: **papply echo \"Hello World" "Hello Papply\"**

compressing files with [GNU gzip](https://www.gnu.org/software/gzip/):

**gzip \*.txt**

becomes:

**papply gzip \*.txt**

converting images to jpg using [ImageMagick's](https://imagemagick.org/index.php) convert:

**convert 1.png 1.jpg**, **convert 2.png 2.jpg**, **convert 2.png 2.jpg**, ...

becomes:

**papply \"convert %F %n.jpg\" \*.png**

# Features
## Template replacements
The following strings can appear in the command string (the first
argument to *papply*). They will be replaced by:

* %F: Full original input
* %d: directory name (no trailing slash)
* %f: file name with extension
* %n: file name without extension
* %e: extension (with leading .)
* %z: empty string

## Configuration
The basic configuration should work for most use-cases. I have not
implemented command line options to *papply* itself on purpose. This is
a choice to keep the interface as simple as possible.

If you want to override the default values you can create a
*papply.ini* file. This file will be looked for first in the directory
where you execute the command and second in your home directory. The
following parameters can be changed:

* **num_cores**: number of cores to use, default all available cores
* **overcommit_factor**: how many threads per core to request, default 1
* **show_progress**: print progress of the running jobs (yes, no, IfLong), default show progress if running a long time
* **long_duration**: time in seconds to be considered long after which progress is shown, default 60

Any values that are not set explicitly will default to the standard
value. There is an example ini file included in the distribution
(*papply.ini.example*).
