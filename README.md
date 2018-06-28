# biogl
A collection of (semi) useful small bioinformatics modules

There are a variety of ways to use this module within other Python code, some of which are platform-dependent.

On Linux, my preferred method is to simply add the location of the `biogl` directory to the `PYTHONPATH` environmental variable in your preferred shell. For example, if you are using Bash, simply add the following to your `~/.bashrc` file:

```
export PYTHONPATH=$PYTHONPATH:{biogl_directory_path}
```
