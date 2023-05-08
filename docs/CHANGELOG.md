# Changelog

## v1.3.0 (Rider)

-----------------------------------------------------------------------

### **Git commit**: `b29fa6eb243c1c22130f3ab6b4faa12eeb3dc491`
*By* ***MolassesLover*** 

-----------------------------------------------------------------------

I moved the Python (`.py`) files into the [`src/`](../src/) directory,
moved the non-English README files into the [`docs/`](../docs/) directory,
and moved the logo art into the [`docs/img/`](../docs/img/) directory.

I also replaced the plain text AGPL v3.0 license with its Markdown
variation, sourced directly from [gnu.org](https://www.gnu.org/).

Lastly, the Python (`.py`) files were reformatted with the
[Black code formatter](https://pypi.org/project/black/23.3.0/).

-----------------------------------------------------------------------

### **Git commit**: `f6ba0b92e65911e2981e2701918d5d9d0d7ce02f`
*By* ***MolassesLover*** 

-----------------------------------------------------------------------

I decided to replace the `os.system()` calls with `subprocess.run()` as
`os.system()` is very vulnerable to shell injection. Regardless, it's
deprecated.

The code in this commit is untested, and might not run.

-----------------------------------------------------------------------

### **Git commit**: `0e8eafe228e207e66c38eaf3cd22ea0b28a53de7`
*By* ***MolassesLover*** 

-----------------------------------------------------------------------

Before creating `/mnt/{mntdir}` or `/mnt/boot/efi`, the script will
now check whether or not the directory has already been made.

-----------------------------------------------------------------------

## **Git commit**: `244539a070d10b05946d366c63cf4fd3d2e9244b`
*By* ***MolassesLover*** 

-----------------------------------------------------------------------

Added the Arch live image profile, and created a basic SConstruct file
to build the image.

I also updated shebangs to be more consistent, and  inclusive.

-----------------------------------------------------------------------

## **Git commit**: `ac43e290aeb9d3d82f0b3b7142ab5b80a7b42b32`
*By* ***MolassesLover*** 

-----------------------------------------------------------------------

This commit introduced the "Run live image in QEMU" task for
Visual Studio Code. As the name might suggest, it loads the live image
into QEMU. The task specifically runs the
[run_in_qemu.sh](src/dev/run_in_qemu.sh) script