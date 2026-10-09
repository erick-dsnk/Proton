# Building this fork

This guide covers two different artifacts: an isolated x64 Wine runtime for
benign driver conformance work, and a complete Proton integration build. The
first rundown increment has evidence for the Wine path only. Neither build
establishes Vanguard acceptance or League gameplay. Record actual results using
[TESTING](TESTING.md) and the [evidence convention](evidence/README.md).

The full Proton guidance below preserves the useful build, installation,
debugging and editor instructions inherited from Valve's README, adjusted for
this independent experimental fork.

## Obtain the source

For the current Wine-only research path:

```bash
git clone --branch main https://github.com/erick-dsnk/Proton.git proton
cd proton
git submodule update --init wine
git rev-parse HEAD
git -C wine rev-parse HEAD
git submodule status
```

Always use the Wine revision pinned by Proton's gitlink. Do not substitute a
system Wine installation or the latest upstream Wine branch for this checkout.
For a full Proton build, initialize all required components:

```bash
git submodule update --init --recursive
```

After changing branches, synchronize submodule URLs and restore the branch's
gitlinks, after preserving any local submodule work:

```bash
git submodule sync --recursive
git submodule update --init --recursive
```

Wine implementation lives in `wine/`; its code commits and the parent Proton
gitlink update are separate commits. Read [CONTRIBUTING](../CONTRIBUTING.md) for
the publication/review convention. Other components retain their upstream
licenses and purpose.

## Container and SDK

Most full Proton builds run inside its SDK container. A functioning Docker or
Podman setup and the host dependencies checked by `configure.sh` are required.
The upstream build guide recommends [rootless Podman](https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md);
distribution instructions include Arch [Podman](https://wiki.archlinux.org/title/Podman)
and [Docker](https://wiki.archlinux.org/title/Docker), and Debian
[Podman](https://wiki.debian.org/Podman) and [Docker](https://wiki.debian.org/Docker).
The full Proton build invokes the container itself. The Wine-only research
recipe below uses explicit Docker mounts to avoid fetching/building unrelated
components.

`Makefile.in` pins the default SDK tag. The first x64 experiment used:

```text
registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64:4.0.20260331.220802-0
sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9
```

Use the digest for that comparison. A different SDK or architecture creates a
new experiment baseline. Bound concurrency to available memory; `-j8` below
matches the recorded full-Wine build, not a host requirement.

## Isolated x64 Wine conformance build

Run these blocks in the same Bash session from the cloned Proton directory.
They create a source copy and object directory outside the repository. Host
`rsync` is needed for the source copy. Use a new directory for each experiment;
the initial checkpoint's local artifacts are described in the
[implementation register](vanguard-implementation-progress.md).

```bash
PROTON_SOURCE="$(pwd -P)"
VANGUARD_BUILD="$(dirname "$PROTON_SOURCE")/proton-vanguard-wine-build"
VANGUARD_SDK='registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64@sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9'
VANGUARD_BUILD_USER="$(id -u):$(id -g)"
mkdir -p "$VANGUARD_BUILD/wine-src" "$VANGUARD_BUILD/wine-obj"
rsync -a --exclude=.git "$PROTON_SOURCE/wine/" "$VANGUARD_BUILD/wine-src/"
docker pull "$VANGUARD_SDK"
git rev-parse HEAD > "$VANGUARD_BUILD/proton-revision.txt"
git -C wine rev-parse HEAD > "$VANGUARD_BUILD/wine-revision.txt"
git -C wine diff > "$VANGUARD_BUILD/wine-working-tree.patch"
sha256sum \
  wine/dlls/ntoskrnl.exe/ntoskrnl.exe.spec \
  wine/dlls/ntoskrnl.exe/sync.c \
  wine/dlls/ntoskrnl.exe/tests/driver.c \
  wine/include/ddk/wdm.h > "$VANGUARD_BUILD/source-hashes.txt"
```

Record untracked source changes separately if present: a normal `git diff`
does not include them. Check copied-file hashes too, as in the initial record.
Never refresh a source copy while a build is using it.

```bash
set -o pipefail
docker run --rm \
  -v "$VANGUARD_BUILD/wine-src:/src" \
  -v "$VANGUARD_BUILD/wine-obj:/build" \
  -w /src --user "$VANGUARD_BUILD_USER" \
  -e HOME=/build/home -e XDG_CACHE_HOME=/build/cache \
  "$VANGUARD_SDK" \
  bash -lc 'mkdir -p "$HOME" "$XDG_CACHE_HOME" && ./autogen.sh &&
    cd /build && /src/configure --enable-win64' \
  2>&1 | tee "$VANGUARD_BUILD/configure.log"
```

A writable container home/cache is required by generators. This intentionally
configures x64 Wine only. It does not validate the i386 ABI or a complete
Proton/WoW64 distribution.

```bash
docker run --rm \
  -v "$VANGUARD_BUILD/wine-src:/src" \
  -v "$VANGUARD_BUILD/wine-obj:/build" \
  -w /build --user "$VANGUARD_BUILD_USER" \
  -e HOME=/build/home -e XDG_CACHE_HOME=/build/cache \
  "$VANGUARD_SDK" \
  bash -lc 'make -j1 V=1 -C dlls/ntoskrnl.exe &&
    make -j1 V=1 -C dlls/ntoskrnl.exe/tests && make -j8 all' \
  2>&1 | tee "$VANGUARD_BUILD/build.log"
```

Building the module and tests alone was insufficient for the initial fresh
prefix: Wineboot needed transitive modules. `make all` builds the runtime
without installing it. Expected test artifacts include
`wine-obj/dlls/ntoskrnl.exe/tests/x86_64-windows/ntoskrnl.exe_test.exe` and
`driver.dll`, `driver2.dll`, `driver3.dll`, `driver_netio.dll`, and
`driver_pnp.dll` beside it. Run the checkout-built test with [TESTING](TESTING.md).

## Full Proton integration build

### Top-level convenience build

With all submodules initialized and a working container engine:

```bash
make build_name=proton-vanguard-experimental install
```

This builds and installs the tool for the current user's Steam. Missing host
dependencies should produce an early error. Restart Steam to discover the tool.
The top-level Makefile normally derives a name from the branch; use `build_name`
to name the experimental fork explicitly. `make help` lists other convenience
targets and options. An installed tool is a build artifact, not a demonstrated
Vanguard-supported release.

### Configure an out-of-tree build

From the source directory:

```bash
PROTON_SOURCE="$(pwd -P)"
mkdir -p ../proton-vanguard-build
cd ../proton-vanguard-build
"$PROTON_SOURCE/configure.sh" --enable-ccache \
  --build-name=proton-vanguard-experimental \
  --proton-sdk-image=registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64@sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9
make
```

`configure.sh` generates a Makefile and checks the container and host tools.
Use a dedicated build directory. The script discovers Docker/Podman or accepts
`--container-engine=<executable>`. `--enable-ccache` mounts `CCACHE_DIR` or the
user's `.ccache` into the container. `--proton-sdk-image=<image>` chooses an
explicit SDK. See `configure.sh --help` for other options.

On SELinux systems, container bind mounts may require compatible labels.
`--relabel-volumes` asks the container engine to relabel them. Review the
[SELinux labels](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/security-enhanced_linux/sect-security-enhanced_linux-working_with_selinux-selinux_contexts_labeling_files)
and [bind-mount documentation](https://docs.docker.com/storage/bind-mounts/)
before using it with shared/system directories.

### Build targets

| Command in the configured build directory | Result |
|---|---|
| `make` | Complete configured build |
| `make install` | Install into the current user's Steam directory |
| `make redist` | Create `redist/`, for manual compatibility-tool installation |
| `make deploy` | Create `deploy/`, the inherited Steamworks deployment layout; this command does not publish through Steamworks |
| `make module=ntoskrnl.exe module` | Iterate on both 32-bit and 64-bit module variants after a full Proton build |
| `make dxvk` / `make vkd3d-proton` | Rebuild the selected graphics component |

The full build/module targets have broad component prerequisites. Use the
isolated Wine recipe for early generic contracts; do not treat a successful
isolated build as proof the complete Proton build passed.

### Find a failing sub-build

Several projects build in parallel, so the actual error can occur long before
the final failure. Preserve pipeline status and the complete output:

```bash
set -o pipefail
make 2>&1 | tee build.log
rg -n '\] Error [0-9]' build.log
```

Inspect the referenced component's preceding diagnostics. The last top-level
`Error 2` usually propagates an earlier failure rather than describing its cause.

### Debug builds and symbols

Use `UNSTRIPPED_BUILD=1` in a clean build directory to retain symbols:

```bash
mkdir ../proton-vanguard-debug-build
cd ../proton-vanguard-debug-build
../proton/configure.sh --enable-ccache --build-name=proton-vanguard-debug
make UNSTRIPPED_BUILD=1 install
```

The relative source path assumes the original clone is named `proton` and the
build directory is its sibling; otherwise use its absolute path. Valve's Steam
Proton `debug` beta is an upstream debugging option, distinct from this fork:
Proton in the Steam library → Properties → Betas → `debug`.

Stripped builds provide companion `.debug` files that debugging tools may need
to load explicitly. Source `wine/tools/gdbinit.py` in GDB and use
`load-symbol-files` (`lsf`) for mapped symbols. Further instructions are in
[DEBUGGING-LINUX](DEBUGGING-LINUX.md) and [DEBUGGING-WINDOWS](DEBUGGING-WINDOWS.md).
Runtime logging/options are described in [RUNTIME](RUNTIME.md).

### ARM64

The inherited build system supports an ARM64 build machine with
`configure.sh --target-arch=arm64`. Its resulting build cannot be used in x86
Steam running via FEX. The recorded Vanguard package and implementation
experiment are x64; ARM64 Vanguard compatibility is not established.

## Install Proton locally

Steam provides standard Proton versions and can discover custom compatibility
tools. Create a named directory under
`~/.steam/root/compatibilitytools.d/` and place the redistributable build there,
or use `make install` for the current user. Restart Steam after adding the tool.
The inherited distribution layout can include:

```text
compatibilitytools.d/proton-vanguard-experimental/
├── compatibilitytool.vdf
├── filelock.py
├── LICENSE
├── proton
├── proton_dist.tar
├── toolmanifest.vdf
├── user_settings.sample.py
└── version
```

Select the build's configured name in Steam's compatibility-tool settings or a
game's compatibility settings. Actual layout depends on the build target and
revision. Successful installation does not establish that Riot Client, Vanguard
or League work. Redistribution must satisfy all component licenses: see
[LICENSES](../LICENSES.md) and the `LICENSE`/`COPYING` files in each component.

## Editor compilation databases

For [clangd](https://clangd.llvm.org/) and similar tooling, CMake/Meson components
generate `compile_commands.json`; Wine generates it through `makedep`. Proton
collects these databases under the full build's `compile_commands/` directory
and translates paths from its source copies to the actual source. Generated
files such as `config.h` can still require the build tree. Wine's
`tools/make_requests` may be useful for generating its otherwise uncommitted
request files in a local source tree.

Configure the editor with the database path directly, create a local `.clangd`,
or symlink a database. For example, in `proton/wine`, with a sibling full build:

```yaml
# .clangd
CompileFlags:
  CompilationDatabase: ../../proton-vanguard-build/compile_commands/wine-x86_64/
```

```bash
# Alternative from proton/wine:
ln -s ../../proton-vanguard-build/compile_commands/wine-x86_64/compile_commands.json .
```

Keep personal editor paths and generated databases out of published changes.
