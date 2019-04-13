/*
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

//import com.lobsterman.JavaGrinders.Tracker.*;

/**
 * demo class to control the sequence grabber classes for tracking objects in specific parts of the window
 *
 * @author      <a href="mailto:lobsterman.bgsu@gmail.com">RH</a>
 * @Version	@(#)ARCControllerMultiCam.java
 */
@SuppressWarnings("unused")
public class ARCControllerMultiCam {
	// define setting for camera ID
	static int 					kCamID1 = 0;
	static int 					kCamID2 = 1;
	// define settings for screen area and number of individuals to track
	static int 					ARC1FoodLeft = 38;
	static int 					ARC1FoodTop = 62;
	static int 					ARC1FoodWidth = 1714;
	static int 					ARC1FoodHeight = 428;
	
	static int 					ARC1AnimalLeft = 16;
	static int 					ARC1AnimalTop = 534;
	static int 					ARC1AnimalWidth = 1768;
	static int 					ARC1AnimalHeight = 278;
	
	static int 					ARC2FoodLeft = 116;
	static int 					ARC2FoodTop = 60;
	static int 					ARC2FoodWidth = 1678;
	static int 					ARC2FoodHeight = 388;
	
	static int 					ARC2AnimalLeft = 88;
	static int 					ARC2AnimalTop = 522;
	static int 					ARC2AnimalWidth = 1728;
	static int 					ARC2AnimalHeight = 255;
	static int 					kNAnimals = 30;
	// define settings for detecting food level
	static int 					kFoodPxThresh = 17;
	static int 					kFoodObjSize = 30;
	static boolean 				kFoodIsDkObj = true;
	// define settings for detecting animal
	static int 					kAnimPxThresh = 12;
	static int 					kAnimObjSize = 75;
	static boolean 				kAnimIsDkObj = true;
	// define tracker settings
	static float 				kFps = 1;
	static int 					kSecsToRun = -1;
	static boolean 				kToFile = true;
	static boolean 				kToScreen = false;
	// define Arduino PWM output pins
	static int					kAnalogPinID1 = 3;
	static int					kAnalogPinID2 = 5;
	static int					kAnalogPinID3 = 6;
	static int					kAnalogPinID4 = 9;
	static int					kAnalogPinID5 = 10;
	static int					kAnalogPinID6 = 11;
	// complete settings
	static OpenCVTracker 		theARCTracker1;
	static OpenCVTracker 		theARCTracker2;
	static Rectangle 			kFoodArea1 = new Rectangle(ARC1FoodLeft,ARC1FoodTop,ARC1FoodWidth,ARC1FoodHeight);
	static Rectangle 			kTrackArea1 = new Rectangle(ARC1AnimalLeft,ARC1AnimalTop,ARC1AnimalWidth,ARC1AnimalHeight);		
	static Rectangle 			kFoodArea2 = new Rectangle(ARC2FoodLeft,ARC2FoodTop,ARC2FoodWidth,ARC2FoodHeight);
	static Rectangle 			kTrackArea2 = new Rectangle(ARC2AnimalLeft,ARC2AnimalTop,ARC2AnimalWidth,ARC2AnimalHeight);		

	
	/** 
	 * Sets an adaptive background for each food area as a solid gray average 
	 * of the backgound pixels in its tracking region
	 */
	private static void setSolidBackGroundRefernceForFoodAreas1() throws Exception {
		RecordProc aProc1 = theARCTracker1.itsRecordProc;
		TrackingJobSettingsGroup aTJGroup1 = theARCTracker1.itsTrackingGroup;
		aProc1.handleReference();
		aProc1.makeImagePixels();
		for (int i=0; i<kNAnimals; i++)
			aProc1.handleAutoReferenceBackground(aTJGroup1.getTrackingJobSetting(i));	
		aProc1.renderReference();
		aProc1.displayReference();
		aProc1.updateTrackingComponent();

	}
	
	private static void setSolidBackGroundRefernceForFoodAreas2() throws Exception {
	
	// set adaptive background for 2nd tracker
	RecordProc aProc2 = theARCTracker2.itsRecordProc;
	TrackingJobSettingsGroup aTJGroup2 = theARCTracker2.itsTrackingGroup;
	aProc2.handleReference();
	aProc2.makeImagePixels();
	for (int i=0; i<kNAnimals; i++)
		aProc2.handleAutoReferenceBackground(aTJGroup2.getTrackingJobSetting(i));	
	aProc2.renderReference();
	aProc2.displayReference();
	aProc2.updateTrackingComponent();
	
	}
	
	/** 
	 * Configures and runs the ARC tracker for animals and dye marks
	 */
	private static void configureARCTracker1() {
		try {			
			//generate an array of Trackjob Settings at specific screen coordinates
			TrackingJobSettingsGroup trackJGroup1 = new TrackingJobSettingsGroup();
			trackJGroup1.addTiledTrackingJobs(TrackingJobSetting.Report_YCOORD,kFoodArea1,kNAnimals,1,kFoodPxThresh,kFoodObjSize,kFoodIsDkObj);
			trackJGroup1.addTiledTrackingJobs(TrackingJobSetting.Report_LOCATION_ONLY,kTrackArea1,kNAnimals,1,kAnimPxThresh,kAnimObjSize,kAnimIsDkObj);
			//create and configure a Tracking Procedure in gray scale and plot object outlines
			OpenCVRecordProc aProc1 = new OpenCVRecordProc();
			aProc1.isGrayScale = true;
			aProc1.drawObject = true;
			aProc1.plotExtended = false;
			//configure, and initialize the tracker for ARC
			theARCTracker1.setApplyFilterBeforeDetection(false);
			theARCTracker1.initializeTracker(kFps,kSecsToRun,trackJGroup1,kToFile,kToScreen,null,aProc1);
			theARCTracker1.setVanishingTrail(10);
			setSolidBackGroundRefernceForFoodAreas1();			
			//setup an Image/VideoProducer
			//ImgProducer theProducer1 = new ImgProducer(null,theARCTracker1.nativeWidth,theARCTracker1.nativeHeight,60000);
			//theProducer1.getItsRenderer().setPlotTargetStyle(FrameRenderer.TargetStyle_RAWIMAGE);
			//theProducer1.setSubRect(kFoodArea);
			//theARCTracker1.setVideoProducer(theProducer1);
		} catch (Exception e) { e.printStackTrace(); }
	}
	private static void configureARCTracker2() {
		try {			
			//generate an array of Trackjob Settings at specific screen coordinates
			TrackingJobSettingsGroup trackJGroup2 = new TrackingJobSettingsGroup();
			trackJGroup2.addTiledTrackingJobs(TrackingJobSetting.Report_YCOORD,kFoodArea2,kNAnimals,1,kFoodPxThresh,kFoodObjSize,kFoodIsDkObj);
			trackJGroup2.addTiledTrackingJobs(TrackingJobSetting.Report_LOCATION_ONLY,kTrackArea2,kNAnimals,1,kAnimPxThresh,kAnimObjSize,kAnimIsDkObj);
			//create and configure a Tracking Procedure in gray scale and plot object outlines
			OpenCVRecordProc aProc2 = new OpenCVRecordProc();
			aProc2.isGrayScale = true;
			aProc2.drawObject = true;
			aProc2.plotExtended = false;
			//configure, and initialize the tracker for ARC
			theARCTracker2.setApplyFilterBeforeDetection(false);
			theARCTracker2.initializeTracker(kFps,kSecsToRun,trackJGroup2,kToFile,kToScreen,null,aProc2);
			theARCTracker2.setVanishingTrail(10);
			setSolidBackGroundRefernceForFoodAreas2();			
			//setup an Image/VideoProducer
			//ImgProducer theProducer2 = new ImgProducer(null,theARCTracker2.nativeWidth,theARCTracker2.nativeHeight,60000);
			//theProducer2.getItsRenderer().setPlotTargetStyle(FrameRenderer.TargetStyle_RAWIMAGE);
			//theProducer2.setSubRect(kFoodArea2);
			//theARCTracker2.setVideoProducer(theProducer2);
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
	//	theARCTracker.addWindowListener(relayIntf);
		ControlDeviceOperator 	pinPWM_1 = new ControlDeviceOperator(kAnalogPinID1);
		ControlDeviceOperator 	pinPWM_2 = new ControlDeviceOperator(kAnalogPinID2);
		ControlDeviceOperator 	pinPWM_3 = new ControlDeviceOperator(kAnalogPinID3);
		ControlDeviceOperator 	pinPWM_4 = new ControlDeviceOperator(kAnalogPinID4);
		ControlDeviceOperator 	pinPWM_5 = new ControlDeviceOperator(kAnalogPinID5);
		ControlDeviceOperator 	pinPWM_6 = new ControlDeviceOperator(kAnalogPinID6);
		try {
			theARCTracker1.itsRecordProc.setExternalData(new Integer(0));
			theARCTracker2.itsRecordProc.setExternalData(new Integer(0));
			relayIntf.addControlDeviceOperator(pinPWM_1);
			relayIntf.addControlDeviceOperator(pinPWM_2);
			relayIntf.addControlDeviceOperator(pinPWM_3);
			relayIntf.addControlDeviceOperator(pinPWM_4);
			relayIntf.addControlDeviceOperator(pinPWM_5);
			relayIntf.addControlDeviceOperator(pinPWM_6);
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
						pinPWM_4.setByteValue(curr_out);
						pinPWM_5.setByteValue(curr_out);
						pinPWM_6.setByteValue(curr_out);
						theARCTracker1.itsRecordProc.setExternalData(new Integer(curr_out));
						theARCTracker2.itsRecordProc.setExternalData(new Integer(curr_out));
						Thread.sleep(pulse_duration);
						pinPWM_1.setByteValue(0);
						pinPWM_2.setByteValue(0);
						pinPWM_3.setByteValue(0);
						pinPWM_4.setByteValue(0);
						pinPWM_5.setByteValue(0);
						pinPWM_6.setByteValue(0);
						Thread.sleep(interpulse_delay);
						theARCTracker1.itsRecordProc.setExternalData(new Integer(0));
						theARCTracker2.itsRecordProc.setExternalData(new Integer(0));
					}
				}
				Thread.sleep(intertrain_delay);
			}
		} catch (Exception e) { e.printStackTrace(); }		
	}

	/** 
	 * Runs the Stimulation Protocol in a thread
	 */
	public static void startArduinoStimulator() {
		Runnable StimulusRunner = new Runnable() {
			public void run() { runArduinoStimulator(); }
		};
		Thread StimulusThread = new Thread(StimulusRunner);
		StimulusThread.start();
	}

	public static void main (String args[]) {
		try {
			theARCTracker1 = new OpenCVTracker("ARC1",kCamID1);
			configureARCTracker1();
			//startArduinoStimulator();
			theARCTracker1.setVisible(true);
			
			theARCTracker2 = new OpenCVTracker("ARC2",kCamID2);
			configureARCTracker2();
			theARCTracker2.setVisible(true);
		} catch (Exception e) { e.printStackTrace(); }
	}
}
