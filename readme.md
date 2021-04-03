# Ubuntu Custom Kernel Discovery
This tool finds and downloads the latest version of custom Ubuntu kernels.

## Why?
I am using a notebook with an 11th Gen Intel(R) Core(TM) i7-1165G7 processor, 
which has a different set of power state and is not properly supported by the mainline Ubuntu kernels. 
The upstream kernels have better support after 5.10.4 but the only way to find and download the custom kernels is to open 
the [Ubuntu ppa](https://kernel.ubuntu.com/~kernel-ppa/mainline/) page and perform 
the [same manual steps](https://itsfoss.com/upgrade-linux-kernel-ubuntu/#install-manually).
This tool automatizes the discovery and download process

## Usage
-  Clone the project `git clone https://github.com/lemehmet/kernel-discovery.git`
-  Install the requirements `pip install -r requirements.txt`
-  Get help `python main.py -h`
-  Run `python main.py` with the default options:
    -  Discovers the current kernel version
    -  Finds the latest and greatest version in the ppa
    -  Creates a folder for the version and downloads the `generic` versions.
-  Install new kernel `sudo dpkg -i .deb`

