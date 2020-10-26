# JavaGrinders_ARC with OpenCV 3.2.0 and OpenJDK11 --- installation support instructions

(Updated 10/25/2020 by [Scarlet Park](mailto:jpark@scripps.edu))

Versions used in this instruction support:
- Mac OS X Catalina
- Java (OpenJDK 11)
- JavaGrinders Library version 56
- OpenCV 3.2.0
- Eclipse Photon

## Useful keyboard shortcuts and commands
|      Function							 	|	Shortcut / command |
|-------------------------------------------|----------------------| 
|**Go to folder (in Finder)**				| *Command+Shift+G*
|**Show hidden files and folders in Finder**| *Command+Shift+.*
|**Change directory in Terminal**			| `cd`
|**Execute a command in Terminal with superuser privilege**| type `sudo` (<u>su</u>peruser <u>do</u>) before the command you want to execute. (If Terminal output says "access denied" or "permission denied")|

## Install necessary tools, packages, and dependencies

### Xcode
[Xcode](https://developer.apple.com/xcode/) is a package provided by Apple containing compilers, libraries and additional tools required to develop applications for macOS.

Install Xcode following the instructions [here](https://guide.macports.org/#installing.xcode).

### Homebrew

Install Homebrew, a useful package manager for macOS, by entering the following command in Terminal:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
```
  (Note: most up-to-date installation instructions can be found on the [Homebrew official website]("https://brew.sh/").)

Once Homebrew is installed, install `pkg-config` as follows (in Terminal):
```bash
brew install pkg-config
```
> [`pkg-config`](https://formulae.brew.sh/formula/pkg-config) helps you keep track of installed packages


---
### OpenJDK11
For OpenCV 3.2.0 and JavaGrinders version 56, we recommend Java 11, which is nicely backwards compatible, or Java 1.8. In this example, we'll use Java 11 from OpenJDK.

To check whether you have Java installed, open Terminal and execute command:
```bash
java -version
javac -version
```
*<u>If the reported version of Java is higher than 11:</u>*
Navigate to /Library/Java/JavaVirtualMachines/ and delete the jdk folder to uninstall that version of Java.

Download and extract`openjdk-11_osx-x64_bin.tar` from [here](https://drive.google.com/file/d/12v5Qyl6vZnNQIIITkw7BYnJ7uZJTuIiv/view?usp=sharing) or the [official website](https://jdk.java.net/archive/).
Move the extracted `openjdk-11` folder to `/Library/Java/JavaVirtualMachines/`

Open Terminal and execute the command:
```bash
sudo java -version
sudo javac -version
```
   > Your security setting may block Terminal from correctly accessing Java. A pop-up window will give you only two choices---move the downloaded file to Trash or cancel operation. In such case, go to your System Settings > Security. There, you can unblock access to the file. Now if you return to Terminal and execute `sudo java -version` again, the pop-up window will have 3 options: Open, Move to Trash, or Cancel. Click Open.

If the output reports Java 11 and Open JDK 11, you're good to go.
Execute the following command to add the `JAVA_HOME` path to `~/.profile`.
```bash
echo 'export JAVA_HOME=$(/usr/libexec/java_home -v11)'>>~/.profile
source ~/.profile
```
----
### If trying to reinstall OpenCV, use the following steps to check for and uninstall previous builds / installations of OpenCV before proceeding

Check whether OpenCV is installed with
```bash
pkg-config --modversion opencv
```
#### *If you're extremely lucky and you know / remember how you built or installed OpenCV:*
|  Installation method 	| How to uninstall |
|-----------------------|-------------------------|
| Homebrew			   	| `brew uninstall opencv` <br> (if `brew info opencv` shows that opencv is installed) |
| MacPorts				| `sudo port uninstall opencv` |
| CMake					| If you have a `cmake` build folder you (or someone else) used to install OpenCV (and can find the said directory), navigate to that directory and execute in Terminal: `$ make uninstall` |

#### If you're unlucky like I am and don't know how OpenCV was installed:
To manually remove files associated with OpenCV,
```bash
sudo rm -rf /opt/local/lib/libopencv*
rm -rf /usr/local/include/opencv*
```
And you can further manually check and decide to keep or remove OpenCV-related files with the following command:
```bash
sudo find / -name "opencv" -exec rm -i {} \;
```
Verify that OpenCV is uninstalled with:
```bash
pkg-config --modversion opencv
```

#### *(Optional, but recommended) Uninstall all packages for a clean install of OpenCV and JavaGrinders ARC*
If you're trying to set up JavaGrinders for ARC on a Mac that's not used for anything else, I recommend uninstalling all packages installed with package managers such as brew or MacPorts.

For **Homebrew** installed packages:
```bash
brew list 		# This will return all formulae installed with brew
brew remove --force $(brew list) --ignore-dependencies
brew cask remove --force $(brew list --cask)
brew cleanup
brew list 		# Confirm that everything is deleted
```
If you decide to uninstall all Homebrew installed packages, *re-install `pkg-config` before proceeding to the next step*.
```bash
brew install pkg-config
```
For **MacPorts** installed packages:
```bash
sudo port selfupdate
sudo port -fp uninstall installed
sudo port -d selfupdate
```
> Sometimes, for some reason, you (or one of your co-workers) may have installed some packages with MacPorts but your bash may say port: command not found. In that case, simply install a new version of MacPorts (download binary from [here](https://drive.google.com/file/d/1tB2OiZlVLn2_JyHm9fnQVSclAzd1Fo_o/view?usp=sharing) or the [official website](https://www.macports.org/install.php). You need to have installed Xcode already.) and then execute the commands above.

---
### Installing necessary packages and OpenCV dependencies with Homebrew
Install `wget`:
```bash
brew install wget
```
We also need to install `ant`. In Homebrew, `ant` requires `openjdk` formula as a dependency, which currently (Oct 25, 2020) defaults to jdk-14. This version of jdk will not be compatible with our OpenCV and JavaGrinders libraries. So a workaround is to install `ant` with the `openjdk` dependency and then uninstall the `openjdk`.
```bash
brew install ant && brew uninstall --ignore-dependencies openjdk
```
Test whether `ant` is installed:
```bash
ant -v
```
Now, we have to add `$ANT_HOME` path to `~/.profile`.

```bash
echo 'export ANT_HOME=(/usr/local/Cellar/ant/1.10.9/libexec/)'>>~/.profile
source ~/.profile
```
### Check `.profile` and update `.bash_profile`
At this point, we've installed a lot of things and added a couple of lines to our `.profile` file, we should check to make sure we have everything we need in there.
```bash
nano ~/.profile
```
This should look something like this:    
```
# JAVA_HOME path
export JAVA_HOME=$(/usr/libexec/java_home -v11)

# ANT_HOME path    
export ANT_HOME=$(/usr/local/Cellar/ant/1.10.9/libexec/)
```
  > There could be some additional lines there (for example, if you installed MacPorts, there will be a MacPorts PATH environmental variable there as well. But for now, what's important is that the `JAVA_HOME` and `ANT_HOME` are in there.

Press *Control+c* to exit `nano` (and save changes if you made any).
Now, let's reload the `.profile` and make sure `JAVA_HOME` and `ANT_HOME` work.
```bash
source ~/.profile
echo $JAVA_HOME
echo $ANT_HOME
```
Once you've verified that the `JAVA_HOME` and `ANT_HOME` paths are correctly set, we need to make sure that `.bash_profile` will pull up `.profile` when the Terminal shell starts. ([StackExchange: What is the difference between ~/.profile and ~/.bash_profile?](https://unix.stackexchange.com/questions/45684/what-is-the-difference-between-profile-and-bash-profile))
```bash
nano ~/.bash_profile
```
Insert the line
```bash
. ~/.profile
```
at the beginning of the `/.bash_profile`. So it should look like:
```
. ~/.profile
export PATH=/usr/local/bin:$PATH
```
Save and exit.

We're almost there!

---
### Install CMake GUI
OpenCV 3.2.0 is the version we want for the JavaGrinders_ARC. (OpenCV 3.3.x had USB unidentifiable serial connection issues and OpenCV 4.x require newer Java & JavaGrinders library---in development.) But with Homebrew and MacPorts, OpenCV installation defaults to either 3.4.x or 4.x. So it's best to build OpenCV 3.2.0 from source.

To do so, we need CMake (and the GUI, optional but recommended).

Download and install CMake GUI with a binary from [here](https://drive.google.com/file/d/1Q53nhU_l59t3GiQuVtBdLQ-O6JhwDmcF/view?usp=sharing) or from the [official website](https://cmake.org/download/).

___
<br><br>

## Installing OpenCV 3.2.0
Now we can proceed with installing OpenCV!

A lot of online instructions will recommend building OpenCV with package managers such as Homebrew of MacPorts. However, the package managers install OpenCV 4.x by default or even when you specify OpenCV3, it'll install OpenCV 3.4 (at least right now in October 2020 it does).

So we want to build OpenCV 3.2.0 from source.

First, download OpenCV 3.2.0 source code from [here](https://drive.google.com/file/d/1617qaP2ayDKBnS5S4nogD_yHoU5QaAsb/view?usp=sharing) or from [OpenCV GitHub release](https://github.com/opencv/opencv/releases/tag/3.2.0) and extract the archive somewhere. 
In this instruction, I'm going to assume you extracted the archive in your **Documents** folder. So there should be a opencv-3.2.0 folder in your Documents.

Navigate to <u>/Documents/opencv-3.2.0/</u> in Finder, and inside, create a new folder and name it **build**. 
Now the folder tree should look something like:

```
Documents
|	...
|
└───opencv-3.2.0
	|	.tgitconfig
	|	CMakeLists.txt
	|	CONTRIBUTING.md
	|	LICENSE
	|	README.md
	|
	└───build
	└───3rdparty
	└───apps
	└───cmake
	└───data
	└───doc
	└───include
	└───modules
	└───samples
```

Great, now we can start building OpenCV 3.2.0.

If you want to use the configuration that I used, download **CMakeCache.txt** from [here](https://docs.google.com/document/d/12XPXmZAUnJWrFU9B7U27_SNFc0fH1xkU7a0hljrV4r0/edit?usp=sharing) and place it in the `build` folder.

Alternatively, you can go through the different options and specify your own configuration. 
>(You'll have to do this if you aren't exactly following the instructions I've outlined. For example, Java version, where you extracted the opencv-3.2.0 folder ...)

<br>

In **Terminal**, navigate to `/Documents/opencv-3.2.0/build`.
```bash
cd /Users/YOUR_USERNAME_GOES_HERE/Documents/opencv-3.2.0/build
```
Make sure you replace `YOUR_USERNAME_GOES_HERE` in the command above with your username! In my case, my username on Mac is jalab. So my command would be `cd /Users/jalab/Documents/opencv-3.2.0/build`.

Now, launch the CMake GUI from Applications. 
The icon will look like: <br/>
![CMake icon](https://cmake.org/wp-content/uploads/2018/11/cmake_logo_slider.png)

Next to **Where is the source code:**, enter 
`/Users/YOUR_USERNAME_GOES_HERE/Documents/opencv-3.2.0`.
Next to **Where to build the binaries:**, enter 
`/Users/YOUR_USERNAME_GOES_HERE/Documents/opencv-3.2.0/build`.

Now, click the **Configure** button. If you downloaded the CMakeCache.txt and placed it in the build folder, the fields should auto-fill. If there are any red lines after you've clicked Configure two times, check those settings and fill them in appropriately.

Now, you can click the **Generate** button, and wait for the build to finish.
Go back to **Terminal**, and type the following command:
```bash
make install
```
This will install OpenCV 3.2.0 in `/usr/local/share/OpenCV`.
<br>

Now, you can verify that OpenCV 3.2.0 was installed using the following command:
```bash
pkg-config --modversion opencv
```
which should report
```bash 
3.2.0
```

You can also manually check that the `opencv320.jar` and `opencv320.dylib` files are present by navigating to **/usr/local/share/OpenCV/java** from Finder. (Remember the "Go to ..." command? *Command+Shift+G*)

## Install Eclipse IDE for Java Developers

### Download and install Eclipse

We recommend using Eclipse **Photon**, as previous versions don't support Java 11 well. Download Eclipse Photon for Java Developers [here](https://drive.google.com/file/d/1fyBQNxGmIP41LYKGckik5SYmClzqkvgw/view?usp=sharing) or from the official Eclipse website ([release page](https://www.eclipse.org/downloads/packages/release/photon/r/eclipse-ide-java-developers) or [direct download link](https://www.eclipse.org/downloads/download.php?file=/technology/epp/downloads/release/photon/R/eclipse-java-photon-R-macosx-cocoa-x86_64.dmg)).

Follow the on-screen instructions to install Eclipse.

### Setting up Eclipse
When you first start Eclipse, it will ask you to set a workspace directory. A workspace is just a directory that Eclipse will use to place new projects in.
Doesn't matter where you put it. It could be in your Documents, it could be in your Home (/Users/*YOUR_USERNAME*). The suggested location is fine. 
Click the **Use this as the default and do not ask again** checkbox, and then click OK.

#### Check default Java build path and compiler:
Follow the instructions [here](https://www.concretepage.com/ide/eclipse/how-to-change-eclipse-java-version-for-compiler-and-jre) to verify/change Java version for compiler and JRE in Eclipse. 
> The demo uses Java 1.8, but you want to activate Java 11!

#### Disabling Polling News Feed:
Does a "Polling News Feed" error keep popping up? 
You can go to Eclipse > Preferences, and in the "type filter text" box, type **News**. Un-check the *Enable automatic news polling option*. ([source](https://web.stanford.edu/class/archive/cs/cs106a/cs106a.1198//eclipse.html#:~:text=Finally%2C%20we%20need%20to%20disable,Enable%20automatic%20news%20polling%20option%22.))


## Import JavaGrinders_ARC and OpenCVTest

Last step! We're going to import two projects: JavaGrinders_ARC and OpenCV. 

### Download project folders

JavaGrinders_ARC
- This contains the JavaGrinders library file `JavaGrinders.jar` and the class files used to run the automated animal & food tracking.
- [Download link for JavaGrinders_ARC](https://drive.google.com/drive/folders/1nzrDxsqhuAkREa7OvQn64D3hXJSprGgV?usp=sharing)
<br>

OpenCVTest
- OpenCVTest contains few classes for testing whether OpenCV can detect cameras that are connected to your computer. 
- You can use this to help troubleshoot where the problems is if you're having trouble with JavaGrinders_ARC.
- [Download link for OpenCVTest](https://drive.google.com/drive/folders/1RXTNZlSu59gfDR2x52tb-iwLqSM1tsYm?usp=sharing)

Move the **OpenCVTest** and **JavaGrinders_ARC** folders into your Eclipse workspace, so the folder tree might look like this:
```
Workspace
└───OpenCVTest
└───JavaGrinders_ARC
```

### Loading JavaGrinders_ARC
In Eclipse, create new Java Project <br/>
![](https://drive.google.com/uc?export=view&id=1cifaq36X2Xr_zBABQ_uhhNyMb1q9zged)

Enter "JavaGrinders_ARC" in the Project name and the rest should auto fill. Then click next.<br/>
![](https://drive.google.com/uc?export=view&id=1jRd_80CaG4YvDj8H3SOtva_14QGGvnp9)
> The image shows "OpenCVTest" in Project name. *Replace that with **"JavaGrinders_ARC"***.
> Your default JRE should say JDK 11. I was using Java 1.8 when I took this screenshot.

On the next screen, **uncheck the box for *Create module-info.java file***.<br/>
![](https://drive.google.com/uc?export=view&id=19hDFQeVTm3LLJ9L7QfbS-onbXtioEchX)

Click "Finish", and you're good to go!


### START 'ER UP!
In the **Package Explorer** window, navigate to **JavaGrinders_ARC** > **src** > **_ARC**. Double click on **ARCController.java** to open the class file.

Click the green "play" button in the tool bar to start the tracking software! <br/>
![RUN](https://drive.google.com/uc?export=view&id=11kvYr6ONwblv2cENMPE8AlwLkxtMGKbM)

### Troubleshooting with OpenCVTest

Does ARCController.java not work? Then we can at least see if it's the OpenCV library that's flawed using the class files in OpenCVTest.

In Eclipse, create new Java Project <br/>
![](https://drive.google.com/uc?export=view&id=1cifaq36X2Xr_zBABQ_uhhNyMb1q9zged)

Enter "OpenCVTest" in the Project name and the rest should auto fill. Then click next.<br/>
![](https://drive.google.com/uc?export=view&id=1jRd_80CaG4YvDj8H3SOtva_14QGGvnp9)
> Your default JRE will probably say JDK 11. I was just using Java 1.8 when I took this screenshot.

On the next screen,
First, **uncheck the box for *Create module-info.java file***.<br/>
![](https://drive.google.com/uc?export=view&id=19hDFQeVTm3LLJ9L7QfbS-onbXtioEchX)

Then, under "Libraries", click "Add Library..."<br/>
![](https://drive.google.com/uc?export=view&id=1gCoCs_jD0-pNJwHFXDNpNQ45vGV-dVLw)

Select "User Library" and click "Next"<br/>
![](https://drive.google.com/uc?export=view&id=1TS_20-V6jH7v5WlwkfwrU7FHsY76LThv)

Click on "User Libraries...", then "New...", and enter "OpenCV" in the User library name and click "OK".<br/>
![](https://drive.google.com/uc?export=view&id=1EjKM2np0_lpAN1C-m3TyHdBdsXGIMLRP)

Now with the "OpenCV" selected, click on "Add External JARS..."<br/>
![](https://drive.google.com/uc?export=view&id=14QKD7yNgCH3mCaju1O5smsLIW_ysGdma)

Now you need to navigate to where your OpenCV JAR is. It's probably in `/opt/local/share/OpenCV/java`. Enter your path and click Go.<br/>
![](https://drive.google.com/uc?export=view&id=1iWJdexXXHCMWoUheN5EtEucXDgAvmZom)

Select the opencv-320.jar file and click Open.<br/>
![](https://drive.google.com/uc?export=view&id=12f13_75R9iHl7wR86sgzCs84epi6PCIZ)

Now, select "Native library location: (None)" and click Edit<br/>
![](https://drive.google.com/uc?export=view&id=1vhV3uY2m7QQ_aO1YOhwqBJFD2B4jRGup)

Click "External Folder...", click "Open", and then "OK"<br/>
![](https://drive.google.com/uc?export=view&id=16QOZCl8cYpEovhLQ0aIkzSehYyzL0O5O)

Click "OK"<br/>
![](https://drive.google.com/uc?export=view&id=1PkMnABbuppcB-uWlOv_COTrlixEtOixL)

Click "Finish"<br/>
![](https://drive.google.com/uc?export=view&id=1WUkW2ZKYTIe357fGRLc6HNTuFcncS_4Y)

Click "Finish"<br/>
![](https://drive.google.com/uc?export=view&id=1OLm8fNmhRyDNfjeXS0OS4oUWAj5Wa6NY)

Navigate to **Count.java** and run it to see if OpenCV can access any camera<br/>
![](https://drive.google.com/uc?export=view&id=1xA5bVdRLeKyKao4xtumpdzaUVesAdsmf)
