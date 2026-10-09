# Building the symbol server

# Fork symbol packaging

This upstream tooling is available to the experimental open source
[Proton Vanguard compatibility effort](../README.md), which aims to bring League
of Legends back to Linux. Package symbols from the same local build as the
binaries being investigated and record their hashes in
[test evidence](../docs/TESTING.md). This recipe does not establish a hosted
symbol service or a release publishing process for this fork. See
[CONTRIBUTING.md](../CONTRIBUTING.md) for review and publication conventions.

From a Proton build environment, after building Proton, run
```
make symstore-tarball
```
This will create in <BUILD>/symstore a .zip file, named after the
release being built (<BUILD_NAME>-symstore.zip).

# Requirements for symbol server

This requires mapping a directory <TOP> (and all its sub-hierarchy) at
a given URI.

There are two strong requirements:
- all files in <TOP> must be served as binary,
- the mapping of <TOP> must be case insensitive.
