Proton (steamrt4) SDK
====================

Fork build context
------------------

These SDK recipes are retained from upstream Proton for the experimental open
source [Proton Vanguard compatibility effort](../README.md), which aims to bring
League of Legends back to Linux. The Valve SDK registry and publishing workflow
below are upstream infrastructure, not services controlled by this fork. Local
SDK changes must record the image identity and toolchain in
[test evidence](../docs/TESTING.md); see the fork's
[build guide](../docs/BUILDING.md). A successful SDK or runtime build does not
establish Vanguard acceptance or playable League.

These are the build rules that are used to create docker images to build
Proton. The automated creation of Valve's official upstream images lives in
<https://gitlab.steamos.cloud/proton/steamrt4/sdk>, but this can be
used to create local images too.


Local Changes And Testing
-------------------------

Make changes to the `.Dockerfile.in`

Just run `make proton` in this directory. To use Podman instead run `make
DOCKER=podman proton`.

With the default `BUILD_ARCH=x86_64`, this creates a container image tagged as
`registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64:<STEAMRT_VERSION>-0-dev`
and `registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64:latest`, where
`STEAMRT_VERSION` is defined in this directory's `Makefile`.

Look for lines `successfully tagged` at the bottom of the output.

To use the just built container image for Proton build you can pass the following argument
to `./configure.sh` (assuming you are using the same container engine, Podman or
Docker, for both):
`--proton-sdk-image=registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64:latest`


ARM64 Containers
----------------

To build:

```
make BUILD_ARCH=aarch64 proton-llvm
```

The `proton-llvm` target adds `-llvm` to the architecture-specific image name,
producing `registry.gitlab.steamos.cloud/proton/steamrt4/sdk/arm64-llvm:latest`
and the corresponding `<STEAMRT_VERSION>-0-dev` tag. Select the ARM64 target
explicitly when configuring Proton; changing the SDK image alone does not change
the default target architecture.

To use:

```
$PROTON_SRC/configure.sh --target-arch=arm64 --proton-sdk-image=registry.gitlab.steamos.cloud/proton/steamrt4/sdk/arm64-llvm:latest
```


Upstream Official Images
------------------------

The following retained procedure is for maintainers with access to Valve's
upstream publishing infrastructure. Fork contributors should use local images
and propose changes through the fork's review process.

To update the upstream official Proton SDK images:

1) Update the image build rules and the base `STEAMRT_VERSION` numbers in files
   in this directory, test locally, commit and push the changes.

2) Update `.gitlab-ci.yml` in the
   [Proton SDK](https://gitlab.steamos.cloud/proton/steamrt4/sdk)
   repository to point to the new commit, commit and push to trigger a
   new build of `-dev` images.

3) Once the images are satisfying, tag the version in Proton SDK
   repository and push the tag, this will trigger a new build of the
   images and version them with the same tag as the Git tag.

4) Once the images have been published, update the default `STEAMRT_IMAGE`
   version number in the top-level `Makefile.in` to use the newly built images
   by default.

For that upstream publishing workflow, any change or addition to GPL-ed source
first requires updating or adding
the corresponding source to <https://repo.steampowered.com/proton-sdk>.
The `SOURCES_URLBASE` variable must be used to download the sources
from there, and its SHA256 must be added to validate the sources in the
same way the existing code does.


Technical Details
-----------------

The images are built incrementally, with intermediate images created
for each component of the toolchain, then assembled together in a single
`proton` image.

The reason behind this is to optimize the use of docker cache, so that
components that didn't change do not require to be rebuilt every time,
saving a lot of time in the build process, when only small additions are
made.

It also lets us build several components of the toolchain separately,
in parallel. This is especially the case when building the images on
the <https://gitlab.steamos.cloud> CI.

Because the `ARG` parameter in Dockerfile doesn't behave nicely with
docker caches it is avoided, and `Dockerfile.in` are used with variable
replacements done using `sed`.

The <https://gitlab.steamos.cloud> CI uses Kaniko instead of Docker,
with a bit of script conversion to generate commands usable there. More
details are available in
[Proton SDK](https://gitlab.steamos.cloud/proton/steamrt4/sdk).
