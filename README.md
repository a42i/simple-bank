# Overview

This repository uses the [Nix](https://nixos.org) package manager for dependency management. Install
it by following the instructions [here](https://nixos.org/download/#download-nix), and remember to
enable flakes ([instructions](https://nixos.wiki/wiki/Flakes)). Alternately, use [Determinate
Nix](https://docs.determinate.systems/determinate-nix/#getting-started) for an easier experience.

Once you've got Nix setup, `cd` into the root directory of the project and type `nix develop`. Once
you're in the `nix shell`, use `just -l` to see the available targets. Use `just test` to run all the
tests and `just run` to execute the simple bank CLI.

# Notes

* I did not have enough time to implement a harness that tested out the CLI directly. In a real
  project, some simple canary tests to exercise the command line arguments etc. would be useful.
* I've taken a very simplistic approach to error handling within the [cli](src/simple_bank/cli.py)
  module; this was done to save time. An approach where all errors are collected before exiting the
  program would be quite simple to implement.
* The tests don't check for the contents of any error messages; this is deliberate. Ideally, there
  would be distinct types for each possible error condition and the tests would check for that. But,
  to keep things more manageable, I am using a single `InvalidInput` tuple for this exercise.
