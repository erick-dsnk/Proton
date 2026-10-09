# Symbol debugging in this fork

This upstream Proton guide is retained for the experimental open source
[Proton Vanguard compatibility effort](../README.md), which aims to bring League
of Legends back to Linux. Use binaries and symbols from the exact fork build
that produced the dump, and record revisions and hashes following
[TESTING.md](../docs/TESTING.md). Valve's symbol archive serves upstream builds;
this fork does not promise matching symbols there or published symbol packages.
Debugging evidence alone does not establish Vanguard acceptance or playable
League.

This small note to describe how a windows developer can inject
minidump files generated from a crash of a game running under Proton
Steam (desktop or Deck).

Note: this doesn't apply if the application is running managed code as
it's required more compabilities between .NET and Mono. So, from now
on, we only consider native (non managed) code.

These minidumps are fully reloadable under Microsoft tools (WinDbg or
Visual Studio) when the binaries of the Proton system files are made
available to the debugging tool.
It's mandatory for reloading a minidump created with a given Proton
version that the very same Proton system files are made avaiable to
the machine running the debugging tool.

If the right version is not installed, the debugging tool will likely
emit warnings (like "couldn't match module", or "invalid time
stamp"). This means the debugging tool will report likely bogus
information, and your setup must be fixed before going any further.

# Installing on dev machine

The retained upstream procedure describes symbol-store zip packages for Valve
Proton releases starting at Proton 8.0-4. For a local fork build, generate the
matching package using [guidelines-deploy.md](guidelines-deploy.md).

Where published by upstream, the .zip file is part of its GitHub release and is
named
<BUILD_NAME>-symstore.zip.

You must create a top directory (referred as <SYMSTORE> below) and
extract the zip file with <SYMSTORE> as the parent directory.

Each time a new Proton's version is released, this extraction scheme
has to be done in order to have proper access to minidumps generated
from this Proton version.

# Setting up the debugging tools

## WinDbg

In the WinDbg "File > Settings" menu, in the "Symbols path" pane, add
```
srv*<SYMSTORE>
```
Of course, one can add also the paths to the application being
debugged.

## Visual Studio

In Visual Studio:
- Open the minidump from the "File > Open > File" menu
- Open the "Set Symbol paths" item, and add a (.pdb) store pointing to
  <SYMSTORE>
- Depending on your project settings, you could also have another
  store pointing to your own application
- Then start debugging by using the "Debug with..." appropriate to
  your project.

## Other debugging tool

If the tool supports symbol stores, then there's should be a similar
configuration as described above for MS tools.

[[ Note: the settings above should work also if we're able to generate
.pdb files along side the images ]]

# Public store

Valve's upstream Proton symbol store is described at <https://proton-archive.steamos.cloud/>.

Then no local installation is required, only setting the
```
srv*<SYMSTORE_URI>
```
in the debugging tools would be required.
