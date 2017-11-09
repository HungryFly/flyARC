/*
			//setup a VideoProducer with a MovieFrameRenderer
			AVIProducer theProducer = new AVIProducer(null,cvTrackerDemo.nativeWidth,cvTrackerDemo.nativeHeight,1f);
			//ImgProducer theProducer = new ImgProducer(null,cvTrackerDemo.nativeWidth,cvTrackerDemo.nativeHeight,1f);
			theProducer.getItsRenderer().setPlotTargetStyle(FrameRenderer.TargetStyle_RAWIMAGE);
			theProducer.setSubRect(new Rectangle(5,5,500,250));
			cvTrackerDemo.setVideoProducer(theProducer);
Permission is hereby granted, without written agreement and without
license or royalty fees, to use, copy, modify, and distribute this
software and its documentation for any purpose, provided that this
notice appears in all copies of this software.

IN NO EVENT SHALL RH BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, 
SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE 
OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF RH HAS BEEN 
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

RH SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT 
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR 
A PARTICULAR PURPOSE. THE SOFTWARE PROVIDED HEREUNDER IS ON AN "AS IS" 
BASIS, AND RH HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, 
UPDATES, ENHANCEMENTS, OR MODIFICATIONS.

Online Documentation for this class can be found at
http://caspar.bgsu.edu/~software/Java/Docs/
 */

package _ARC;

import java.awt.Rectangle;

import com.lobsterman.JavaGrinders.Tracker.FrameRenderer;
import com.lobsterman.JavaGrinders.Tracker.ImgProducer;
import com.lobsterman.JavaGrinders.Tracker.OpenCVRecordProc;
import com.lobsterman.JavaGrinders.Tracker.OpenCVTracker;
import com.lobsterman.JavaGrinders.Tracker.RecordProc;
import com.lobsterman.JavaGrinders.Tracker.TrackingJobSetting;
import com.lobsterman.JavaGrinders.Tracker.TrackingJobSettingsGroup;
import com.lobsterman.JavaGrinders.control.ArduinoInterface;
import com.lobsterman.JavaGrinders.control.ControlDeviceOperator;

/**
 * demo class to control the sequence grabber classes for tracking objects in specific parts of the window
 *
 * @author  <a href="mailto:lobsterman.bgsu@gmail.com">RH</a>
 * @Version	5.6
 */
@SuppressWarnings("unused")
public class ARCController {
	// define setting for camera ID
	static int 						kCamID = 0;
	// define settings for screen area and number of individuals to track
	static int 						ARCFoodLeft = 50;
	static int 						ARCFoodTop = 50;
	static int 						ARCFoodWidth = 900;
	static int 						ARCFoodHeight = 300;
	static int 						ARCAnimalLeft = 50;
	static int 						ARCAnimalTop = 350;
	static int 						ARCAnimalWidth = 900;
	static int 						ARCAnimalHeight = 300;
	static int 						kNAnimals = 30;
	// define settings for detecting food level
	static int 						kFoodPxThresh = 10;
	static int 						kFoodObjSize = 25;
	static boolean 					kFoodIsDkObj = true;
	// define settings for detecting animal
	static int 						kAnimPxThresh = 10;
	static int 						kAnimObjSize = 25;
	static boolean 					kAnimIsDkObj = true;
	// define tracker settings
	static float 					kFps = 1;
	static int 						kSecsToRun = -1;
	static boolean 					kToFile = true;
	static boolean 					kToScreen = true;
	// define Arduino PWM output pins
	static int						kAnalogPinID1 = 3;
	static int						kAnalogPinID2 = 5;
	static int						kAnalogPinID3 = 6;
	// complete settings
	static OpenCVTracker		 	theARCTracker;
	static Rectangle 				kFoodArea = new Rectangle(ARCFoodLeft,ARCFoodTop,ARCFoodWidth,ARCFoodHeight);
	static Rectangle 				kTrackArea = new Rectangle(ARCAnimalLeft,ARCAnimalTop,ARCAnimalWidth,ARCAnimalHeight);		

	/** 
	 * Sets an adaptive background for each food area as a solid gray average 
	 * of the background pixels in its tracking region
	 */
	private static void setSolidBackGroundRefernceForFoodAreas() throws Exception {
		RecordProc aProc = theARCTracker.itsRecordProc;
		TrackingJobSettingsGroup aTJGroup = theARCTracker.itsTrackingGroup;
		aProc.handleReference();
		aProc.makeImagePixels();
		for (int i=0; i<kNAnimals; i++)
			aProc.handleAutoReferenceBackground(aTJGroup.getTrackingJobSetting(i));	
		aProc.renderReference();
		aProc.displayReference();
		aProc.updateTrackingComponent();
	}

	/** 
	 * Configures and runs the ARC tracker for animals and dye marks
	 */
	private static void configureARCTracker() {
		try {			
			//generate an array of Trackjob Settings at specific screen coordinates
			TrackingJobSettingsGroup trackJGroup = new TrackingJobSettingsGroup();
			trackJGroup.addTiledTrackingJobs(TrackingJobSetting.Report_YCOORD,kFoodArea,kNAnimals,1,kFoodPxThresh,kFoodObjSize,kFoodIsDkObj);
			trackJGroup.addTiledTrackingJobs(TrackingJobSetting.Report_LOCATION_ONLY,kTrackArea,kNAnimals,1,kAnimPxThresh,kAnimObjSize,kAnimIsDkObj);
			//create and configure a Tracking Procedure in gray scale and plot object outlines
			OpenCVRecordProc aProc = new OpenCVRecordProc();
			aProc.isGrayScale = true;
			aProc.drawObject = true;
			aProc.plotExtended = false;
			//configure, and initialize the tracker for ARC
			theARCTracker.setApplyFilterBeforeDetection(false);
			theARCTracker.initializeTracker(kFps,kSecsToRun,trackJGroup,kToFile,kToScreen,null,aProc);
			theARCTracker.setVanishingTrail(10);
			setSolidBackGroundRefernceForFoodAreas();			
			//setup an Image/VideoProducer
			//ImgProducer theProducer = new ImgProducer(null,theARCTracker.nativeWidth,theARCTracker.nativeHeight,60000);
			//theProducer.getItsRenderer().setPlotTargetStyle(FrameRenderer.TargetStyle_RAWIMAGE);
			//theProducer.setSubRect(kFoodArea);
			//theARCTracker.setVideoProducer(theProducer);
		} catch (Exception e) { e.printStackTrace(); }
	}

	/** 
	 * Patterns the Stimulation Protocol for Arduino microcontroller kit
	 */
	private static void runArduinoStimulator() {
		int base_voltout = 55; 				// base duty cycle output
		int incr_voltout = 40; 				// increases in duty cycle output
		int pulse_count = 5; 				// number of individual vibrations
		int pulse_duration = 200; 			// duration of individual vibration [mS]
		int interpulse_delay = 800; 		// pause between individual vibrations [mS]
		int stim_count = 5; 				// number of vibration intensities 
		int interstim_delay = 15000; 		// pause between vibration intensities [mS]
		int intertrain_delay = 3600000;		// pause between stimuli sets [mS]
		int initial_delay = 1800000;
		ArduinoInterface relayIntf = new ArduinoInterface(20);
		theARCTracker.addWindowListener(relayIntf);
		ControlDeviceOperator 	pinPWM_1 = new ControlDeviceOperator(kAnalogPinID1);
		ControlDeviceOperator 	pinPWM_2 = new ControlDeviceOperator(kAnalogPinID2);
		ControlDeviceOperator 	pinPWM_3 = new ControlDeviceOperator(kAnalogPinID3);
		try {
			theARCTracker.itsRecordProc.setExternalData(new Integer(0));
			relayIntf.addControlDeviceOperator(pinPWM_1);
			relayIntf.addControlDeviceOperator(pinPWM_2);
			relayIntf.addControlDeviceOperator(pinPWM_3);
			relayIntf.listDeviceOperators();
			Thread.sleep(initial_delay);
			while (true) {
				for (int stims=0; stims<stim_count; stims++) {
					Thread.sleep(interstim_delay);
					for (int vibs=1; vibs<pulse_count+1; vibs++) {
						int curr_out = stims*incr_voltout+base_voltout;
						pinPWM_1.setByteValue(curr_out);
						pinPWM_2.setByteValue(curr_out);
						pinPWM_3.setByteValue(curr_out);
						theARCTracker.itsRecordProc.setExternalData(new Integer(curr_out));
						Thread.sleep(pulse_duration);
						pinPWM_1.setByteValue(0);
						pinPWM_2.setByteValue(0);
						pinPWM_3.setByteValue(0);
						Thread.sleep(interpulse_delay);
						theARCTracker.itsRecordProc.setExternalData(new Integer(0));
					}
				}
				Thread.sleep(intertrain_delay);
			}
		} catch (Exception e) { e.printStackTrace(); }		
	}

	/** 
	 * Runs the Stimulation Protocol in a thread
	 */
	private static void startArduinoStimulator() {
		Runnable StimulusRunner = new Runnable() {
			public void run() { runArduinoStimulator(); }
		};
		Thread StimulusThread = new Thread(StimulusRunner);
		StimulusThread.start();
	}

	/** 
	 * Main function that instantiates, configures and runs the ARC trackers
	 * 
	 * @param args arguments (ignored)
	 */
	public static void main (String args[]) {
		try {
			theARCTracker = new OpenCVTracker("ARC",kCamID);
			configureARCTracker();
			//startArduinoStimulator();
			theARCTracker.setVisible(true);
		} catch (Exception e) { e.printStackTrace(); }
	}
}