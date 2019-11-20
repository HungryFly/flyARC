
<!DOCTYPE html>
<html>

<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="https://stackedit.io/style.css" />
</head>

<body class="stackedit">
  <div class="stackedit__html"><h1 id="install-open-source-tools-for-running-the-arc-activity-recording-cafe">Install open-source tools for running the ARC (Activity recording CAFE)</h1>
<p>(<em>from <a href="http://javagrinders-arc.blogspot.com">http://javagrinders-arc.blogspot.com</a></em>)</p>
<p>This guide walks you through the steps needed to run the ARC instrument. It is a system that permits the automated measurement of motion and food consumption of individual fruit flies. It will show you how to download a number of open source software tools, to set them up in a way that they play nicely with each other, and to make them available to the JavaGrinders framework for the control of behavioral experiments. These instructions cover Mac OSX 10.11.6, xUbuntu 16.04, and Raspbian Jessie (for Raspberry Pi 3B), and Ubuntu 16.04 Arm64 (for Odroid C2). Help in adding instructions for Windows 7-9 or Windows 10 are always greatly welcome.</p>
<h2 id="table-of-contents">Table of Contents</h2>
<p><div class="toc">
<ul>
<li><a href="#install-open-source-tools-for-running-the-arc-activity-recording-cafe">Install open-source tools for running the ARC (Activity recording CAFE)</a>
<ul>
<li><a href="#table-of-contents">Table of Contents</a></li>
<li><a href="#what-you-need-...">What you need …</a></li>
<li><a href="#installation-1---java-standard-edition-8-development-kit-java-se-8-jdk">Installation #1 - Java Standard Edition 8 Development Kit (Java SE 8 JDK)</a>
<ul>
<li><a href="#test-whether-java-se-8-sdk-is-already-installed">Test whether Java SE 8 SDK is already installed</a>
<ul>
<li><a href="#installation-instructions---macosx">Installation Instructions - MacOSX:</a></li>
<li><a href="#installation-instructions---linux">Installation Instructions - Linux:</a></li>
</ul>
</li>
</ul>
</li>
<li><a href="#installation-2---java-ide">Installation #2 - Java IDE</a>
<ul>
<li><a href="#test-whether-netbeanseclipseintellij-is-already-installed">Test whether Netbeans/Eclipse/IntelliJ is already installed</a></li>
</ul>
</li>
<li><a href="#installation-3---opencv">Installation #3 - OpenCV</a>
<ul>
<li><a href="#test-whether-opencv-and-java-bindings-are-already-installed">Test whether OpenCV and Java Bindings are already installed</a>
<ul>
<li><a href="#installation-instructions----mac-osx">Installation instructions – Mac OSX:</a></li>
<li><a href="#installation-instructions----linux">Installation instructions – Linux:</a></li>
</ul>
</li>
</ul>
</li>
<li><a href="#installation-4---import-the-arccontroller-project-into-ide-and-run">Installation #4 - Import the ARCController Project into IDE and Run</a>
<ul>
<li><a href="#eclipse">Eclipse</a></li>
<li><a href="#netbeans">NetBeans</a></li>
</ul>
</li>
<li><a href="#installation-5-optional---confirm-that-the-plugged-in-arduino-is-loaded-as-a-usb-communication-device-cdc">Installation #5 (optional) - Confirm that the plugged-in Arduino is loaded as a USB communication device (CDC)</a>
<ul>
<li>
<ul>
<li><a href="#installation-instructions----mac-osx-1">Installation instructions – Mac OSX:</a></li>
<li><a href="#installation-instructions----linux-1">Installation instructions – Linux:</a></li>
</ul>
</li>
</ul>
</li>
<li><a href="#installation-6-optional---install-jarduino-firmware-on-arduino-for-stimulus-delivery">Installation #6 (optional) - Install JArduino Firmware on Arduino for stimulus delivery</a></li>
</ul>
</li>
</ul>
</div></p>
<h2 id="what-you-need-...">What you need …</h2>
<ul>
<li>
<p><strong>Computer running MacOSX or some flavor of Linux.</strong> Preferred and tested OS options are MacOSX 10.11, Xubuntu 18.04, Ubuntu 18.04, Debian Jessie and Stretch. Tracking speed scales up with increased processing power, but even lower hardware specs should be sufficient to run the ARC in its basic capacity.</p>
</li>
<li>
<p><strong>Source of Video Frames.</strong> A wide range of options are supported via standard drivers through any OpenCV compatible source. This includes most webcams, network cameras, or serial camera modules.</p>
</li>
<li>
<p><strong>Administrator Rights on Computer.</strong> Account must have with rights to administer the computer as installation of libraries requires the password.</p>
</li>
<li>
<p><strong>Internet access.</strong>  You need to obtain the libraries and applications from the internet. Some downloads are fairly large, so a connection via ethernet (or a reliable and fast wifi) are needed.</p>
</li>
<li>
<p><strong>Java Integrated Development Environment (IDE).</strong> Eclipse and Netbeans are the dominant players and zipped JavaGrinders_ARC project folders are included for a clean import.</p>
</li>
<li>
<p><strong>Arduino Uno.</strong> This is an open-source, single board microcontroller.</p>
</li>
<li>
<p><strong>Libraries, Drivers, Applications.</strong> A number of libraries, drivers, and applications are required to support the tracking framework and to provide programming access to webcams, usb devices, microcontrollers, and image processing.</p>
</li>
</ul>
<h2 id="installation-1---java-standard-edition-8-development-kit-java-se-8-jdk">Installation #1 - Java Standard Edition 8 Development Kit (Java SE 8 JDK) or higher</h2>
<p>The JDK is a development environment for building and running software written in the Java programming language. Most operating systems come pre-installed with the ability to run Java applications via a Java Runtime Environment (JRE). Developing Java software requires additional tools from Java’s Software Development Kit (SDK), including the Java Compiler ‘javac’.</p>
<h3 id="test-whether-java-se-8-sdk-is-already-installed">Test whether Java SE 8 SDK is already installed</h3>
<p>To test whether Java 8 SDK is available, test for your version of the java compiler ‘javac’. Open a Terminal, found in Applications/Utilities on Mac OSX and Terminal Emulator in Linux, and type…</p>
<pre><code>$ javac -version
</code></pre>
<dl>
<dt>YES:</dt>
<dd> You are fine if the terminal reports any build <b>'1.8.0_*' </b>. <br> This means that you already have a Java Compiler of Version 8. Mine is </dd> </dl>
<pre><code> javac 1.8.0_151
</code></pre>
<p><strong>NO:</strong></p>
<p>If the terminal reports that no SDK is available</p>
<pre><code>-bash: javac: command not found
</code></pre>
<p>or if a version prior to 8 is found, then you need to download and install the <em>Java SE 8 or later Development Kit</em>. The ARC framework works well with the JDK for Java 13 and my recommendation is to use the newest version. Moreover, recent versions of the OpenCV library will require installations of a recent Java tool chain.</p>
<h4 id="installation-instructions---macosx">Installation Instructions - MacOSX:</h4>
<p>You can install the OpenJDK version (preferred), or the version from Oracle. <br />
<ins>OpenJDK</ins>:
Download the MacOSX version you want (currently JDK13+33) from the <a href="http://jdk.java.net/archive/"> OpenJDK archive</a>.
In the default case the file is downloaded into the Downloads folder as <code>openjdk-13_osx-x64_bin.tar.gz</code>.
Extract the archive by double clicking on the .tar.gz archive.
This creates the jdk folder named <code>jdk-13.jdk</code>.
Now move that extracted folder to <code>/Library/Java/JavaVirtualMachines</code>.
This version will now show up as the default. Check with:

<pre class="language-bash"><code class="prism language-bash">$ <span class="token function">sudo</span> java -version
$ <span class="token function">sudo</span> javac -version
</code></pre>

Install the <a href="http://www.oracle.com/technetwork/java/javase/downloads/index.html">Java SE Development Kit 8 from Oracle</a> and download the installation package for OSX or the one that matches your type of Linux. Open the downloaded <em>jdk-8</em> disk image and install the Java framework by following the instructions in the Java SDK 8 Installer.</p>
<p>Add the JAVA_HOME definition for the path to your jre into your <code>/etc/environment</code> login file. You can only do that when you are logged in as ‘root’, then logout from ‘root’ with <code>exit</code>. Touch the new version of <code>/etc/environment</code> with the command <code>source</code>.</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">sudo</span> -i
$ <span class="token keyword">echo</span> <span class="token string">'JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64'</span> <span class="token operator">&gt;&gt;</span> /etc/environment
$ <span class="token keyword">exit</span>
$ <span class="token function">source</span> /etc/environment
</code></pre>
<h4 id="installation-instructions---linux">Installation Instructions - Linux:</h4>
<p>Open the Terminal Emulator and install OpenJDK with …</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">sudo</span> <span class="token function">apt-get</span> update
$ <span class="token function">sudo</span> apt <span class="token function">install</span> default-jdk
</code></pre>
<p>On most recent OS versions this will install Java 11, which works well for our use. You also need to install ant to be able to generate the java bindings for OpenCV</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">sudo</span> <span class="token function">apt-get</span> <span class="token function">install</span> ant
</code></pre>
<p>Follow the online instructions, and agree to the license agreement. You then need to set the JAVA_HOME property to point to the new Oracle Java framework.</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">sudo</span> update-alternatives --config java
</code></pre>
<p>Select the version you want to use as default and copy the path to the installation. In my installation of Ubuntu this is at <code>/usr/lib/jvm/java-8-openjdk/jre/bin/java</code>.</p>
<p>Add the <code>JAVA_HOME</code> definition for the path to your jre into your <code>/etc/environments</code> login file. You can only do that when you are logged in as ‘root’, then logout from ‘root’ with <code>exit</code>. Touch the new version of <code>/etc/environment</code> with the command <code>source</code>.</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">sudo</span> -i
$ <span class="token keyword">echo</span> <span class="token string">'JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64'</span> <span class="token operator">&gt;&gt;</span> /etc/environment
$ <span class="token keyword">exit</span>
$ <span class="token function">source</span> /etc/environment
</code></pre>
<p>After this your <code>$JAVA_HOME</code> path should be set. <code>echo $JAVA_HOME</code> should report</p>
<pre class=" language-bash"><code class="prism  language-bash">usr/lib/jvm/java-8-openjdk-amd64
</code></pre>
<h2 id="installation-2---java-ide">Installation #2 - Java IDE</h2>
<p>Eclipse, Netbeans, and IntelliJ are programming Environments for Java.</p>
<h3 id="test-whether-netbeanseclipseintellij-is-already-installed">Test whether Netbeans/Eclipse/IntelliJ is already installed</h3>
<p>Search for Eclipse, Netbeans, or IntelliJ. If you find it, start the application, open the Preferences dialog by clicking on the <em>Eclipse</em> menu and selecting the <em>Preferences</em> menu item (MacOSX) or clicking on the <em>Windows</em> menu and selecting the <em>Preferences</em> menu item (Linux).</p>
<p>OpenCV 3 requires Java version 8 or higher. To confirm a compatible Java Runtime Environment (JRE) for your programming, expand the node <em>Java</em> in the left hand side of the dialog box. A version of Java 1.8 should be your default version in <em>Installed JREs</em>.</p>
<dl> 
<dt> YES:  </dt>
<dd> You are fine if you have Netbeans or Eclipse with Java already. </dd>
<dd> Proceed to <em>Installation #3</em>. </dd> </dl>
<p><strong>NO:</strong></p>
<p>If you do not find the Eclipse (or Netbeans) Application in your installation, install an IDE.</p>
<p>Download the  <a href="http://www.eclipse.org/downloads/packages/release/Neon/3">Eclipse IDE for Java Developers</a> package for your OS. I am using Eclipse Photon (i.e. version 4.8) along with Java 11. If you prefer Netbeans, go to  <a href="https://netbeans.apache.org/download/index.html">Apache Netbeans Downloads</a>  and use version 9.</p>
<p>Uncompress the archive, and drag the resulting Eclipse Application into your Applications folder. Start Eclipse and confirm the default workspace in the next window. Check the “Use this as the default …” box.</p>
<p>Confirm a compatible Java Runtime Environment (JRE) for your programming by expanding the node <em>Java</em> in the left hand side of the dialog box. A version of Java 1.8 should be your default version in <em>Installed JREs</em>.</p>
<p>Select the Java Browsing Perspective in “Window” -&gt; “Perspective” -&gt; “Open Perspective” -&gt; “Java Browsing”.</p>
<h2 id="installation-3---opencv">Installation #3 - OpenCV</h2>
<p><a href="http://opencv.org/">OpenCV</a> has emerged as the dominant technology to interface with video cameras, read their frame buffers, and process the resulting frames. Use of OpenCV requires successful installation of the library along with its dependencies. This blog guides you through the steps necessary for using OpenCV on MacOSX and Linux.</p>
<h3 id="test-whether-opencv-and-java-bindings-are-already-installed">Test whether OpenCV and Java Bindings are already installed</h3>
<p>Open the Terminal application and test for opencv:</p>
<pre class=" language-bash"><code class="prism  language-bash">$ pkg-config --modversion opencv
</code></pre>
<p>Then check whether opencv contains the java bindings in one of these locations:</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">ls</span> /opt/local/share/OpenCV/java/
$ <span class="token function">ls</span> /usr/local/share/OpenCV/java/
$ <span class="token function">ls</span> /usr/share/OpenCV/java/
</code></pre>
<dl>
<dt><strong>YES:</strong></dt>
<dd>
<p>You are all set if your system reports OpenCV <code>3.2.0</code> or higher<br>
and if the <code>/usr/share/OpenCV/java/</code> folder contains the following file<br>
<code>opencv-320.jar</code></p>
</dd>
<dd>
<p>On Linux, the dynamic library itself has extension ‘<em>.so</em>’ instead of ‘<em>.dylib</em>’ and should be at <code>/usr/lib/jni/</code>. If so, the system already has a recent enough version of the OpenCV library installed, along with the needed bindings. Proceed to <em>Installation #4</em>.</p>
</dd>
</dl>
<p><strong>NO:</strong></p>
<p>If the Terminal reports an earlier version of OpenCV, or does not find this library at all, then you need to download the library.</p>
<h4 id="installation-instructions----mac-osx">Installation instructions – Mac OSX:</h4>
<p>For Mac OSX this set of instructions covers OSX 10.11 (and newer), but may work on older versions of OSX as well (<em>not tested though</em>). The simplest way to install is via the package installer <em>MacPorts</em>.</p>
<p>Select the version of MacPorts for your installed version of OSX from <a href="http://www.macports.org/install.php">here</a> and download it. Double click the MacPorts*.pkg and follow the instructions.</p>
<p>Then open the Terminal In your Applications/Utilities folder and type …</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">sudo</span> port selfupdate
</code></pre>
<p>This will update MacPorts with the most recent information on package versions. The command <code>sudo</code> means <em>“superuser do”</em> and will require that you type in your computer’s password. Once the self-update has completed, it will prompt you to install the Xcode command line tools. Agree to the install as well as accept the license.</p>
<blockquote>
<p>Alternatively, you can manually perform an install of the Xcode Command Line Tools with …</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">sudo</span> xcode-select --install
$ <span class="token function">sudo</span> xcodebuild -license
</code></pre>
</blockquote>
<p>Then install opencv with java bindings using your spanking new version of javac, MacPorts and Xcode tools.</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">sudo</span> port <span class="token function">install</span> opencv +java
</code></pre>
<blockquote>
<p>No worries about <em>"Warning: Xcode does not appear to be installed… "</em> - there is no need for the full version of Xcode here. MacPorts will figure out which libraries are needed for OpenCV, and it will go through installing each one in the correct order. MacPorts will slowly crunch through the dependencies for ant, ffmpeg, and others.</p>
</blockquote>
<p>Be prepared that this may take some time. When you get the Terminal message that no broken links were found, then you are cooking with gas.</p>
<p>The default destination for OpenCV is in directory <code>/opt/local/share/OpenCV/</code>. The java bindings for Opencv are installed in directory <code>/opt/local/share/OpenCV/java/</code>.</p>
<h4 id="installation-instructions----linux">Installation instructions – Linux:</h4>
<p>Install version 3.2 from the repository.</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">sudo</span> <span class="token function">apt-get</span> update  
$ <span class="token function">sudo</span> <span class="token function">apt-get</span> <span class="token function">install</span> libopencv-dev
</code></pre>
<p>This will install the <code>opencv-320.jar</code> file at <code>/usr/share/OpenCV/java/</code> and <code>libopencv-320.so</code> in <code>/usr/lib/jni</code>.</p>
<h2 id="installation-4---import-the-arccontroller-project-into-ide-and-run">Installation #4 - Import the ARCController Project into IDE and Run</h2>
<h3 id="eclipse">Eclipse</h3>
<ol>
<li>
<p>Download the <a href="http://caspar.bgsu.edu/~software/Java_Support/Projects_All/JavaGrinders_ARC.zip">zip compressed eclipse archive</a> for the ARC Controller.</p>
</li>
<li>
<p>Copy the downloaded file into your Eclipse workspace and unzip the archive.</p>
</li>
<li>
<p>In Eclipse, go to your package explorer by clicking on the <em>Windows</em> menu and then selecting <em>Show View</em> &gt; <em>Package Explorer</em> menu items.</p>
</li>
<li>
<p>Start a New Java Project by clicking on the <em>New</em> menu, <em>Project</em> menu item, and then under the <em>Java</em> section, select <em>Java Project</em>.</p>
</li>
<li>
<p>In the <em>Java Project Wizard</em>, enter Project name <strong>JavaGrinders_ARC</strong> and click the <em>Finish</em> Button.<br>
This will import the ARC project into your package explorer.</p>
</li>
<li>
<p>Navigate into your <em>JavaGrinders_ARC</em> -&gt; <em>src</em> -&gt; <em>_ARC</em> and select the file <u>ARCController.java</u>.</p>
</li>
<li>
<p>Under the menu <em>Run</em>, click on the menu item <em>Run</em>.</p>
</li>
</ol>
<p>On startup, the tracker program will first look for a video camera (and your Arduino, if applicable). It will then start the tracker and open the main window.</p>
<h3 id="netbeans">NetBeans</h3>
<ol>
<li>
<p>Download the <a href="http://caspar.bgsu.edu/~software/Java_Support/Projects_NetBeans/JavaGrinders_ARC-netbeans.zip">zip compressed netbeans archive</a> for the ARC Controller.</p>
</li>
<li>
<p>In Netbeans, click on the menu <em>File</em> &gt; <em>Import Project</em> &gt; <em>From ZIP…</em> and browse to the downloaded zip archive.</p>
</li>
<li>
<p>Navigate into your <em>JavaGrinders_ARC</em> &gt; <em>Source Packages</em> &gt; <em>_ARC</em> and select the file ARCController.java.</p>
</li>
<li>
<p>Under the menu <em>Run</em>, click on the menu item <em>Run Project</em>.</p>
</li>
</ol>
<p>On startup, the tracker program will first look for a video camera (and your Arduino, if applicable).  It will then start the tracker and open the main window.</p>
<h2 id="installation-5-optional---confirm-that-the-plugged-in-arduino-is-loaded-as-a-usb-communication-device-cdc">Installation #5 (<em>optional</em>) - Confirm that the plugged-in Arduino is loaded as a USB communication device (CDC)</h2>
<p>Without having the Arduino pluged into a USB port, open the Terminal application, and type</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">ls</span> /dev/tty*
</code></pre>
<p>This will report all currently established devices in this category.</p>
<p>Then plug the Arduino into a USB port and reissue the command. If the system contains a driver for the serial chip of the Arduino and is able to load it, a new device will appear in this list.</p>
<dl>
<dt><strong>YES:</strong></dt>
<dd>You are all set if your system finds a new device of sub-type “abstract control model” (ACM).</dd>
<dd>On mac, this will list something like:</dd>
<dd>
<pre><code>   /dev/tty.usbmodem1A21
</code></pre>
</dd>
<dd>On Linux Ubuntu, it will be something like:</dd>
<dd>
<pre><code>  /dev/ttyACM0
</code></pre>
</dd>
</dl>
<p><strong>NO:</strong></p>
<p>If the Terminal fails to establish a communication channel with the Arduino you will have to delve into drivers.</p>
<h4 id="installation-instructions----mac-osx-1">Installation instructions – Mac OSX:</h4>
<p>Original Arduinos use an FTDI usb to serial chip which should be recognized by the MacOS automatically. If you use a cheaper Arduino clone (like I do), chances are that the manufacturer has replaced the FTDI chip with the cheaper CH34X version from Jiangsu Qinheng Co., Ltd. The likely outcome is that the board is not recognized as a valid serial port until you have downloaded and installed the <a href="https://kig.re/2014/12/31/how-to-use-arduino-nano-mini-pro-with-CH340G-on-mac-osx-yosemite.html">relevant driver</a>. After restarting the computer, your Terminal window should report a valid serial port associated with the Arduino.</p>
<h4 id="installation-instructions----linux-1">Installation instructions – Linux:</h4>
<p>Modern versions of the Linux kernel have the driver for this chip included. Consider upgrading to Ubuntu 18.04 or later.</p>
<h2 id="installation-6-optional---install-jarduino-firmware-on-arduino-for-stimulus-delivery">Installation #6 (<em>optional</em>) - Install JArduino Firmware on Arduino for stimulus delivery</h2>
<p>You need the <a href="https://www.arduino.cc/en/main/software">Arduino IDE</a> to communicate with the Arduino board (currently at version 1.8.5).</p>
<ol>
<li>
<p>Download the <a href="http://caspar.bgsu.edu/~software/Java_Support/JArduino.zip">JArduino Folder</a> containing the JArduino Firmware and place the extracted folder into your Arduino <em>Library</em>.</p>
<blockquote>
<p>(Location is inside your Sketchbook Folder as specified in <em>Arduino</em> &gt; <em>Preferences</em>.)</p>
</blockquote>
</li>
<li>
<p>Choose your Arduino Board in <em>Tools</em> &gt; <em>Board</em> and select your port in <em>Tools</em> &gt; <em>Port</em></p>
</li>
<li>
<p>Click the JArduinoFirmware.ino window’s “Upload button” <sup class="footnote-ref"><a href="#fn1" id="fnref1">1</a></sup><br>
<img src="https://www.arduino.cc/en/uploads/Guide/UNO_Upload.png" alt="Arduino IDE upload button"><br>
to upload the sketch to the board.</p>
</li>
<li>
<p>After completion, shut down the Arduino IDE.</p>
</li>
</ol>
<p>This upload procedure only needs to be done once as the Firmware will remain on the board indefinitely (or until another sketch is manually uploaded over it).</p>
<blockquote>
<p>On Linux, you may run into a permission error in uploading your sketch to the <code>/dev/ttyACM0</code> port.</p>
<p>You can list permission for all ACM* ports with:</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">ls</span> -l /dev/tty.ACM*
</code></pre>
<p>which may report something like:</p>
<pre class=" language-bash"><code class="prism  language-bash">crw-rw---- 1 root dialout 188, 0 5 apr 23.01 ttyACM0
</code></pre>
<p>To access the port, you  need to add your username to the dialout group for access using</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">sudo</span> <span class="token function">usermod</span> -a -G dialout <span class="token operator">&lt;</span>username<span class="token operator">&gt;</span>
</code></pre>
</blockquote>
<p><br><br><br><br><br></p>
<p><strong>Note:</strong></p>
<p>This page was last updated April 12, 2019.</p>
<p>The most recent up-to-date instructions for installations can always be found on the <a href="http://javagrinders-arc.blogspot.com/">JavaGrinders-ARC blog</a> maintained by <a href="https://caspar.bgsu.edu/~lobsterman/Page/index.shtml">Dr. Robert Huber</a> at Bowling Green State University.</p>
<p>For more information and support, please contact the owner of this repo or refer to the Nat Prot <a href="https://www.nature.com/articles/nprot.2017.096">article</a> for contact information .</p>
<hr class="footnotes-sep">
<section class="footnotes">
<ol class="footnotes-list">
<li id="fn1" class="footnote-item"><p>Image from <a href="https://www.arduino.cc/en/Guide/ArduinoUnoWiFi">https://www.arduino.cc/en/Guide/ArduinoUnoWiFi</a> <a href="#fnref1" class="footnote-backref">↩︎</a></p>
</li>
</ol>
</section>
</div>
</body>

</html>

<h1 id="install-open-source-tools-for-running-the-arc-activity-recording-cafe">Install open-source tools for running the ARC (Activity recording CAFE)</h1>
<p>(<em>from <a href="http://javagrinders-arc.blogspot.com">http://javagrinders-arc.blogspot.com</a></em>)</p>
<p>This guide walks you through the steps needed to run the ARC instrument. It is a system that permits the automated measurement of motion and food consumption of individual fruit flies. It will show you how to download a number of open source software tools, to set them up in a way that they play nicely with each other, and to make them available to the JavaGrinders framework for the control of behavioral experiments. These instructions cover Mac OSX 10.11.6, xUbuntu 16.04, and Raspbian Jessie (for Raspberry Pi 3B), and Ubuntu 16.04 Arm64 (for Odroid C2). Help in adding instructions for Windows 7-9 or Windows 10 are always greatly welcome.</p>
<h2 id="table-of-contents">Table of Contents</h2>
<p>[TOC]</p>
<h2 id="what-you-need-...">What you need …</h2>
<ul>
<li>
<p><strong>Computer running MacOSX or some flavor of Linux.</strong> Preferred and tested OS options are MacOSX 10.11, Xubuntu 18.04, Ubuntu 18.04, Debian Jessie and Stretch. Tracking speed scales up with increased processing power, but even lower hardware specs should be sufficient to run the ARC in its basic capacity.</p>
</li>
<li>
<p><strong>Source of Video Frames.</strong> A wide range of options are supported via standard drivers through any OpenCV compatible source. This includes most webcams, network cameras, or serial camera modules.</p>
</li>
<li>
<p><strong>Administrator Rights on Computer.</strong> Account must have with rights to administer the computer as installation of libraries requires the password.</p>
</li>
<li>
<p><strong>Internet access.</strong>  You need to obtain the libraries and applications from the internet. Some downloads are fairly large, so a connection via ethernet (or a reliable and fast wifi) are needed.</p>
</li>
<li>
<p><strong>Java Integrated Development Environment (IDE).</strong> Eclipse and Netbeans are the dominant players and zipped JavaGrinders_ARC project folders are included for a clean import.</p>
</li>
<li>
<p><strong>Arduino Uno.</strong> This is an open-source, single board microcontroller.</p>
</li>
<li>
<p><strong>Libraries, Drivers, Applications.</strong> A number of libraries, drivers, and applications are required to support the tracking framework and to provide programming access to webcams, usb devices, microcontrollers, and image processing.</p>
</li>
</ul>
<h2 id="installation-1---java-standard-edition-8-development-kit-java-se-8-jdk">Installation #1 - Java Standard Edition 8 Development Kit (Java SE 8 JDK)</h2>
<p>The JDK is a development environment for building and running software written in the Java programming language. Most operating systems come pre-installed with the ability to run Java applications via a Java Runtime Environment (JRE). Developing Java software requires additional tools from Java’s Software Development Kit (SDK), including the Java Compiler ‘javac’.</p>
<h3 id="test-whether-java-se-8-sdk-is-already-installed">Test whether Java SE 8 SDK is already installed</h3>
<p>To test whether Java 8 SDK is available, test for your version of the java compiler ‘javac’. Open a Terminal, found in Applications/Utilities on Mac OSX and Terminal Emulator in Linux, and type…</p>
<pre><code>$ javac -version
</code></pre>
<dl>
<dt>YES:</dt>
<dd> You are fine if the terminal reports any build <b>'1.8.0_*' </b>. <br> This means that you already have a Java Compiler of Version 8. Mine is </dd> </dl>
<pre><code> javac 1.8.0_151
</code></pre>
<p><strong>NO:</strong></p>
<p>If the terminal reports that no SDK is available</p>
<pre><code>-bash: javac: command not found
</code></pre>
<p>or if a version prior to 8 is found, then you need to download and install the <em>Java SE 8 or later Development Kit</em>. The ARC framework works well with the JDK for Java 11 and my recommendation is to use the newest version.</p>
<h4 id="installation-instructions---macosx">Installation Instructions - MacOSX:</h4>
<p>Install the <a href="http://www.oracle.com/technetwork/java/javase/downloads/index.html">Java SE Development Kit 8 from Oracle</a> and download the installation package for OSX or the one that matches your type of Linux. Open the downloaded <em>jdk-8</em> disk image and install the Java framework by following the instructions in the Java SDK 8 Installer.</p>
<p>Add the JAVA_HOME definition for the path to your jre into your <code>/etc/environment</code> login file. You can only do that when you are logged in as ‘root’, then logout from ‘root’ with <code>exit</code>. Touch the new version of <code>/etc/environment</code> with the command <code>source</code>.</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">sudo</span> -i
$ <span class="token keyword">echo</span> <span class="token string">'JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64'</span> <span class="token operator">&gt;&gt;</span> /etc/environment
$ <span class="token keyword">exit</span>
$ <span class="token function">source</span> /etc/environment
</code></pre>
<h4 id="installation-instructions---linux">Installation Instructions - Linux:</h4>
<p>Open the Terminal Emulator and install OpenJDK with …</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">sudo</span> <span class="token function">apt-get</span> update
$ <span class="token function">sudo</span> apt <span class="token function">install</span> default-jdk
</code></pre>
<p>On most recent OS versions this will install Java 11, which works well for our use. You also need to install ant to be able to generate the java bindings for OpenCV</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">sudo</span> <span class="token function">apt-get</span> <span class="token function">install</span> ant
</code></pre>
<p>Follow the online instructions, and agree to the license agreement. You then need to set the JAVA_HOME property to point to the new Oracle Java framework.</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">sudo</span> update-alternatives --config java
</code></pre>
<p>Select the version you want to use as default and copy the path to the installation. In my installation of Ubuntu this is at <code>/usr/lib/jvm/java-8-openjdk/jre/bin/java</code>.</p>
<p>Add the <code>JAVA_HOME</code> definition for the path to your jre into your <code>/etc/environments</code> login file. You can only do that when you are logged in as ‘root’, then logout from ‘root’ with <code>exit</code>. Touch the new version of <code>/etc/environment</code> with the command <code>source</code>.</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">sudo</span> -i
$ <span class="token keyword">echo</span> <span class="token string">'JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64'</span> <span class="token operator">&gt;&gt;</span> /etc/environment
$ <span class="token keyword">exit</span>
$ <span class="token function">source</span> /etc/environment
</code></pre>
<p>After this your <code>$JAVA_HOME</code> path should be set. <code>echo $JAVA_HOME</code> should report</p>
<pre class=" language-bash"><code class="prism  language-bash">usr/lib/jvm/java-8-openjdk-amd64
</code></pre>
<h2 id="installation-2---java-ide">Installation #2 - Java IDE</h2>
<p>Eclipse, Netbeans, and IntelliJ are programming Environments for Java.</p>
<h3 id="test-whether-netbeanseclipseintellij-is-already-installed">Test whether Netbeans/Eclipse/IntelliJ is already installed</h3>
<p>Search for Eclipse, Netbeans, or IntelliJ. If you find it, start the application, open the Preferences dialog by clicking on the <em>Eclipse</em> menu and selecting the <em>Preferences</em> menu item (MacOSX) or clicking on the <em>Windows</em> menu and selecting the <em>Preferences</em> menu item (Linux).</p>
<p>OpenCV 3 requires Java version 8 or higher. To confirm a compatible Java Runtime Environment (JRE) for your programming, expand the node <em>Java</em> in the left hand side of the dialog box. A version of Java 1.8 should be your default version in <em>Installed JREs</em>.</p>
<dl> 
<dt> YES:  </dt>
<dd> You are fine if you have Netbeans or Eclipse with Java already. </dd>
<dd> Proceed to <em>Installation #3</em>. </dd> </dl>
<p><strong>NO:</strong></p>
<p>If you do not find the Eclipse (or Netbeans) Application in your installation, install an IDE.</p>
<p>Download the  <a href="http://www.eclipse.org/downloads/packages/release/Neon/3">Eclipse IDE for Java Developers</a> package for your OS. I am using Eclipse Photon (i.e. version 4.8) along with Java 11. If you prefer Netbeans, go to  <a href="https://netbeans.apache.org/download/index.html">Apache Netbeans Downloads</a>  and use version 9.</p>
<p>Uncompress the archive, and drag the resulting Eclipse Application into your Applications folder. Start Eclipse and confirm the default workspace in the next window. Check the “Use this as the default …” box.</p>
<p>Confirm a compatible Java Runtime Environment (JRE) for your programming by expanding the node <em>Java</em> in the left hand side of the dialog box. A version of Java 1.8 should be your default version in <em>Installed JREs</em>.</p>
<p>Select the Java Browsing Perspective in “Window” -&gt; “Perspective” -&gt; “Open Perspective” -&gt; “Java Browsing”.</p>
<h2 id="installation-3---opencv">Installation #3 - OpenCV</h2>
<p><a href="http://opencv.org/">OpenCV</a> has emerged as the dominant technology to interface with video cameras, read their frame buffers, and process the resulting frames. Use of OpenCV requires successful installation of the library along with its dependencies. This blog guides you through the steps necessary for using OpenCV on MacOSX and Linux.</p>
<h3 id="test-whether-opencv-and-java-bindings-are-already-installed">Test whether OpenCV and Java Bindings are already installed</h3>
<p>Open the Terminal application and test for opencv:</p>
<pre class=" language-bash"><code class="prism  language-bash">$ pkg-config --modversion opencv
</code></pre>
<p>Then check whether opencv contains the java bindings in one of these locations:</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">ls</span> /opt/local/share/OpenCV/java/
$ <span class="token function">ls</span> /usr/local/share/OpenCV/java/
$ <span class="token function">ls</span> /usr/share/OpenCV/java/
</code></pre>
<dl>
<dt><strong>YES:</strong></dt>
<dd>
<p>You are all set if your system reports OpenCV <code>3.2.0</code> or higher<br>
and if the <code>/usr/share/OpenCV/java/</code> folder contains the following file<br>
<code>opencv-320.jar</code></p>
</dd>
<dd>
<p>On Linux, the dynamic library itself has extension ‘<em>.so</em>’ instead of ‘<em>.dylib</em>’ and should be at <code>/usr/lib/jni/</code>. If so, the system already has a recent enough version of the OpenCV library installed, along with the needed bindings. Proceed to <em>Installation #4</em>.</p>
</dd>
</dl>
<p><strong>NO:</strong></p>
<p>If the Terminal reports an earlier version of OpenCV, or does not find this library at all, then you need to download the library.</p>
<h4 id="installation-instructions----mac-osx">Installation instructions – Mac OSX:</h4>
<p>For Mac OSX this set of instructions covers OSX 10.11 (and newer), but may work on older versions of OSX as well (<em>not tested though</em>). The simplest way to install is via the package installer <em>MacPorts</em>.</p>
<p>Select the version of MacPorts for your installed version of OSX from <a href="http://www.macports.org/install.php">here</a> and download it. Double click the MacPorts*.pkg and follow the instructions.</p>
<p>Then open the Terminal In your Applications/Utilities folder and type …</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">sudo</span> port selfupdate
</code></pre>
<p>This will update MacPorts with the most recent information on package versions. The command <code>sudo</code> means <em>“superuser do”</em> and will require that you type in your computer’s password. Once the self-update has completed, it will prompt you to install the Xcode command line tools. Agree to the install as well as accept the license.</p>
<blockquote>
<p>Alternatively, you can manually perform an install of the Xcode Command Line Tools with …</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">sudo</span> xcode-select --install
$ <span class="token function">sudo</span> xcodebuild -license
</code></pre>
</blockquote>
<p>Then install opencv with java bindings using your spanking new version of javac, MacPorts and Xcode tools.</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">sudo</span> port <span class="token function">install</span> opencv +java
</code></pre>
<blockquote>
<p>No worries about <em>"Warning: Xcode does not appear to be installed… "</em> - there is no need for the full version of Xcode here. MacPorts will figure out which libraries are needed for OpenCV, and it will go through installing each one in the correct order. MacPorts will slowly crunch through the dependencies for ant, ffmpeg, and others.</p>
</blockquote>
<p>Be prepared that this may take some time. When you get the Terminal message that no broken links were found, then you are cooking with gas.</p>
<p>The default destination for OpenCV is in directory <code>/opt/local/share/OpenCV/</code>. The java bindings for Opencv are installed in directory <code>/opt/local/share/OpenCV/java/</code>.</p>
<h4 id="installation-instructions----linux">Installation instructions – Linux:</h4>
<p>Install version 3.2 from the repository.</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">sudo</span> <span class="token function">apt-get</span> update  
$ <span class="token function">sudo</span> <span class="token function">apt-get</span> <span class="token function">install</span> libopencv-dev
</code></pre>
<p>This will install the <code>opencv-320.jar</code> file at <code>/usr/share/OpenCV/java/</code> and <code>libopencv-320.so</code> in <code>/usr/lib/jni</code>.</p>
<h2 id="installation-4---import-the-arccontroller-project-into-ide-and-run">Installation #4 - Import the ARCController Project into IDE and Run</h2>
<h3 id="eclipse">Eclipse</h3>
<ol>
<li>
<p>Download the <a href="http://caspar.bgsu.edu/~software/Java_Support/Projects_All/JavaGrinders_ARC.zip">zip compressed eclipse archive</a> for the ARC Controller.</p>
</li>
<li>
<p>Copy the downloaded file into your Eclipse workspace and unzip the archive.</p>
</li>
<li>
<p>In Eclipse, go to your package explorer by clicking on the <em>Windows</em> menu and then selecting <em>Show View</em> &gt; <em>Package Explorer</em> menu items.</p>
</li>
<li>
<p>Start a New Java Project by clicking on the <em>New</em> menu, <em>Project</em> menu item, and then under the <em>Java</em> section, select <em>Java Project</em>.</p>
</li>
<li>
<p>In the <em>Java Project Wizard</em>, enter Project name <strong>JavaGrinders_ARC</strong> and click the <em>Finish</em> Button.<br>
This will import the ARC project into your package explorer.</p>
</li>
<li>
<p>Navigate into your <em>JavaGrinders_ARC</em> -&gt; <em>src</em> -&gt; <em>_ARC</em> and select the file <u>ARCController.java</u>.</p>
</li>
<li>
<p>Under the menu <em>Run</em>, click on the menu item <em>Run</em>.</p>
</li>
</ol>
<p>On startup, the tracker program will first look for a video camera (and your Arduino, if applicable). It will then start the tracker and open the main window.</p>
<h3 id="netbeans">NetBeans</h3>
<ol>
<li>
<p>Download the <a href="http://caspar.bgsu.edu/~software/Java_Support/Projects_NetBeans/JavaGrinders_ARC-netbeans.zip">zip compressed netbeans archive</a> for the ARC Controller.</p>
</li>
<li>
<p>In Netbeans, click on the menu <em>File</em> &gt; <em>Import Project</em> &gt; <em>From ZIP…</em> and browse to the downloaded zip archive.</p>
</li>
<li>
<p>Navigate into your <em>JavaGrinders_ARC</em> &gt; <em>Source Packages</em> &gt; <em>_ARC</em> and select the file ARCController.java.</p>
</li>
<li>
<p>Under the menu <em>Run</em>, click on the menu item <em>Run Project</em>.</p>
</li>
</ol>
<p>On startup, the tracker program will first look for a video camera (and your Arduino, if applicable).  It will then start the tracker and open the main window.</p>
<h2 id="installation-5-optional---confirm-that-the-plugged-in-arduino-is-loaded-as-a-usb-communication-device-cdc">Installation #5 (<em>optional</em>) - Confirm that the plugged-in Arduino is loaded as a USB communication device (CDC)</h2>
<p>Without having the Arduino pluged into a USB port, open the Terminal application, and type</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">ls</span> /dev/tty*
</code></pre>
<p>This will report all currently established devices in this category.</p>
<p>Then plug the Arduino into a USB port and reissue the command. If the system contains a driver for the serial chip of the Arduino and is able to load it, a new device will appear in this list.</p>
<dl>
<dt><strong>YES:</strong></dt>
<dd>You are all set if your system finds a new device of sub-type “abstract control model” (ACM).</dd>
<dd>On mac, this will list something like:</dd>
<dd>
<pre><code>   /dev/tty.usbmodem1A21
</code></pre>
</dd>
<dd>On Linux Ubuntu, it will be something like:</dd>
<dd>
<pre><code>  /dev/ttyACM0
</code></pre>
</dd>
</dl>
<p><strong>NO:</strong></p>
<p>If the Terminal fails to establish a communication channel with the Arduino you will have to delve into drivers.</p>
<h4 id="installation-instructions----mac-osx-1">Installation instructions – Mac OSX:</h4>
<p>Original Arduinos use an FTDI usb to serial chip which should be recognized by the MacOS automatically. If you use a cheaper Arduino clone (like I do), chances are that the manufacturer has replaced the FTDI chip with the cheaper CH34X version from Jiangsu Qinheng Co., Ltd. The likely outcome is that the board is not recognized as a valid serial port until you have downloaded and installed the <a href="https://kig.re/2014/12/31/how-to-use-arduino-nano-mini-pro-with-CH340G-on-mac-osx-yosemite.html">relevant driver</a>. After restarting the computer, your Terminal window should report a valid serial port associated with the Arduino.</p>
<h4 id="installation-instructions----linux-1">Installation instructions – Linux:</h4>
<p>Modern versions of the Linux kernel have the driver for this chip included. Consider upgrading to Ubuntu 18.04 or later.</p>
<h2 id="installation-6-optional---install-jarduino-firmware-on-arduino-for-stimulus-delivery">Installation #6 (<em>optional</em>) - Install JArduino Firmware on Arduino for stimulus delivery</h2>
<p>You need the <a href="https://www.arduino.cc/en/main/software">Arduino IDE</a> to communicate with the Arduino board (currently at version 1.8.5).</p>
<ol>
<li>
<p>Download the <a href="http://caspar.bgsu.edu/~software/Java_Support/JArduino.zip">JArduino Folder</a> containing the JArduino Firmware and place the extracted folder into your Arduino <em>Library</em>.</p>
<blockquote>
<p>(Location is inside your Sketchbook Folder as specified in <em>Arduino</em> &gt; <em>Preferences</em>.)</p>
</blockquote>
</li>
<li>
<p>Choose your Arduino Board in <em>Tools</em> &gt; <em>Board</em> and select your port in <em>Tools</em> &gt; <em>Port</em></p>
</li>
<li>
<p>Click the JArduinoFirmware.ino window’s “Upload button” <sup class="footnote-ref"><a href="#fn1" id="fnref1">1</a></sup><br>
<img src="https://www.arduino.cc/en/uploads/Guide/UNO_Upload.png" alt="Arduino IDE upload button"><br>
to upload the sketch to the board.</p>
</li>
<li>
<p>After completion, shut down the Arduino IDE.</p>
</li>
</ol>
<p>This upload procedure only needs to be done once as the Firmware will remain on the board indefinitely (or until another sketch is manually uploaded over it).</p>
<blockquote>
<p>On Linux, you may run into a permission error in uploading your sketch to the <code>/dev/ttyACM0</code> port.</p>
<p>You can list permission for all ACM* ports with:</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">ls</span> -l /dev/tty.ACM*
</code></pre>
<p>which may report something like:</p>
<pre class=" language-bash"><code class="prism  language-bash">crw-rw---- 1 root dialout 188, 0 5 apr 23.01 ttyACM0
</code></pre>
<p>To access the port, you  need to add your username to the dialout group for access using</p>
<pre class=" language-bash"><code class="prism  language-bash">$ <span class="token function">sudo</span> <span class="token function">usermod</span> -a -G dialout <span class="token operator">&lt;</span>username<span class="token operator">&gt;</span>
</code></pre>
</blockquote>
<p><br><br><br><br><br></p>
<p><strong>Note:</strong></p>
<p>This page was last updated April 12, 2019.</p>
<p>The most recent up-to-date instructions for installations can always be found on the <a href="http://javagrinders-arc.blogspot.com/">JavaGrinders-ARC blog</a> maintained by <a href="https://caspar.bgsu.edu/~lobsterman/Page/index.shtml">Dr. Robert Huber</a> at Bowling Green State University.</p>
<p>For more information and support, please contact the owner of this repo or refer to the Nat Prot <a href="https://www.nature.com/articles/nprot.2017.096">article</a> for contact information .</p>
<hr class="footnotes-sep">
<section class="footnotes">
<ol class="footnotes-list">
<li id="fn1" class="footnote-item"><p>Image from <a href="https://www.arduino.cc/en/Guide/ArduinoUnoWiFi">https://www.arduino.cc/en/Guide/ArduinoUnoWiFi</a> <a href="#fnref1" class="footnote-backref">↩︎</a></p>
</li>
</ol>
</section>

