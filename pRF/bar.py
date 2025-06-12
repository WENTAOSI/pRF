#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  4 15:40:16 2025

@author: siwentao
"""

from psychopy import visual, event, core, monitors, logging, gui, data, misc
import numpy as np
import os
import sys
import random
import pandas as pd
from PIL import Image
import pylink
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy

# %% SAVING and LOGGING
# Store info about experiment and experimental run
expName = 'pRF'  # set experiment name here
expInfo = {
    'run': '01',
    'participant': 'test',
    'display': ['DBIC', 'TaylorMacbookPro'],
    'mode': ['experiment','outputMovie'],
    'eyelink':['True', 'False']
    }

# Create GUI at the beginning of exp to get more expInfo
dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
if dlg.OK == False: core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName

# get the path that this script is in and change dir to it
_thisDir = os.path.dirname(os.path.abspath(__file__))  # get current path
parentDir = os.path.dirname(_thisDir)
os.chdir(parentDir)  # change directory to this path


# Name and create specific subject folder
subjFolderName = '%s_SubjData' % (expInfo['participant'])
if not os.path.isdir(subjFolderName):
    os.makedirs(subjFolderName)
# Name and create data folder for the experiment
dataFolderName = subjFolderName + os.path.sep + '%s' % (expInfo['expName'])
if not os.path.isdir(dataFolderName):
    os.makedirs(dataFolderName)
# Name and create specific folder for logging results
logFolderName = dataFolderName + os.path.sep + 'Logging'
if not os.path.isdir(logFolderName):
    os.makedirs(logFolderName)
logFileName = logFolderName + os.path.sep + '%s_%s_Run%s_%s' % (
    expInfo['participant'], expInfo['expName'], expInfo['run'],
    expInfo['date'])
# Name and create specific folder for output
outFolderName = dataFolderName + os.path.sep + 'Output'
if not os.path.isdir(outFolderName):
    os.makedirs(outFolderName)
outFileName = outFolderName + os.path.sep + '%s_%s_Run%s_%s' % (
    expInfo['participant'], expInfo['expName'], expInfo['run'],
    expInfo['date'])
# Name and create specific folder for protocol files
prtFolderName = dataFolderName + os.path.sep + 'Protocols'
if not os.path.isdir(prtFolderName):
    os.makedirs(prtFolderName)

PNGFolderName = dataFolderName + os.path.sep + 'PNG'
if not os.path.isdir(PNGFolderName):
    os.makedirs(PNGFolderName)

# save a log file and set level for msg to be received
logFile = logging.LogFile(logFileName+'.log', level=logging.INFO)
logging.console.setLevel(logging.WARNING)  # set console to receive warningVEs

# %% MONITOR AND WINDOW
# set monitor information:
if expInfo['display'] == 'DBIC':
    distanceMon = 128.7  
    widthMon = 42.8 
    PixW = 1920.0 
    PixH = 1200.0  
elif expInfo['display'] == 'TaylorMacbookPro':
    distanceMon = 50 
    widthMon = 30.41 
    PixW = 3024.0 
    PixH = 1964.0  

moni = monitors.Monitor('testMonitor', width=widthMon, distance=distanceMon)
moni.setSizePix([PixW, PixH]) 

# log monitor info
logFile.write('MonitorDistance=' + str(distanceMon) + 'cm' + '\n')
logFile.write('MonitorWidth=' + str(widthMon) + 'cm' + '\n')
logFile.write('PixelWidth=' + str(PixW) + '\n')
logFile.write('PixelHeight=' + str(PixH) + '\n')

# specificy background color
backColor = [-0.5, -0.5, -0.5]  # from -1 (black) to 1 (white)
# set screen:
myWin = visual.Window(size=(PixW, PixH),
                      screen = 0,
                      winType='pyglet',  # winType : None, ‘pyglet’, ‘pygame’
                      allowGUI=False,
                      allowStencil=True,
                      fullscr=True,  # for psychoph lab: fullscr = True
                      monitor=moni,
                      color=backColor,
                      colorSpace='rgb',
                      units='deg',
                      blendMode='avg',
                      waitBlanking=True
                      )

# %% STIMULI SCHEDULE SETUP
np.random.seed(42)  # Global seed for reproducibility

stim_schedule = []

orientations = [0, 45, 90, 135]
n_steps = 12
n_reps = 12
aperture_radius = 5  # dva

# Sweep offsets from -5° to 5°
base_offsets = np.linspace(-aperture_radius, aperture_radius, n_steps)

for rep in range(n_reps):
    for ori in orientations:
        # Generate new shuffled offset list for each ori × rep
        sweep_offsets = np.copy(base_offsets)
        np.random.shuffle(sweep_offsets)

        angle_deg = ori - 90
        angle_rad = np.deg2rad(angle_deg)
        dx = np.cos(angle_rad)
        dy = np.sin(angle_rad)

        if ori in [45, 135]:
            dx *= -1

        norm = np.sqrt(dx**2 + dy**2)
        dx /= norm
        dy /= norm

        for step_num, offset in enumerate(sweep_offsets):
            pos_x = offset * dx
            pos_y = offset * dy

            stim_schedule.append({
                'rep': rep + 1,
                'orientation': ori,
                'position': (pos_x, pos_y),
                'step': step_num + 1,
                'fix_change': 0
            })

# in case we need fixation task 
'''
# === Pick 30 non-adjacent fixation change indices ===
total_trials = len(stim_schedule)
valid_indices = set(range(total_trials))
selected_indices = []

while len(selected_indices) < num_fix_change and valid_indices:
    candidate = random.choice(list(valid_indices))
    selected_indices.append(candidate)

    # Remove candidate and neighbors to enforce non-adjacency
    for i in [candidate - 1, candidate, candidate + 1]:
        valid_indices.discard(i)

# Apply the fixation changes
for idx in selected_indices:
    stim_schedule[idx]['fix_change'] = 1
'''

# Convert stim_schedule to DataFrame
df = pd.DataFrame(stim_schedule)
df.to_csv(os.path.join(outFolderName, 'stim_schedule.csv'), index=False)

# %% TIME AND TIMING PARAMeTERS
# parameters
'''
totalTrigger = np.sum(Durations)
'''
# get screen refresh rate
for _ in range(10):
    myWin.flip()  # Flip the window a few times
refr_rate = myWin.getActualFrameRate()  # get screen refresh rate

print(f"refr_rate{refr_rate}")

refr_rate = 60.0 # if could not get reliable refresh rate

if refr_rate is not None:
    frameDur = 1.0/round(refr_rate)
else:
    frameDur = 1.0/round(refr_rate)  # couldn't get a reliable measure so guess

logFile.write('RefreshRate=' + str(refr_rate) + '\n')
logFile.write('FrameDuration=' + str(frameDur) + '\n')

# define clock
clock = core.Clock()
logging.setDefaultClock(clock)

# %% STIMULI

# === Geometry ===
bar_length = 10.0   # degrees
bar_width = 0.9     # degrees
n_checks_x = 32     # horizontal grids
n_checks_y = 3      # vertical grids
flicker_rate = 8    # Hz
flicker_interval = 1.0 / flicker_rate


# === Create bar-shaped checkerboard with 3 rows and 32 columns ===
checker_pattern = np.zeros((n_checks_y, n_checks_x))

# Create all-white bar (255 = white)
white_bar = np.full((n_checks_y, n_checks_x), 255, dtype=np.uint8)

for row in range(n_checks_y):
    for col in range(n_checks_x):
        checker_pattern[row, col] = 255 if (row + col) % 2 == 0 else 0

# Optionally scale each check to be 1 pixel (can be upscaled visually)
checker_array = np.kron(checker_pattern, np.ones((1, 1)))

# Convert to image
white_bar_img = Image.fromarray(white_bar)
checker_img = Image.fromarray(checker_array.astype(np.uint8))
checker_img_inv = Image.fromarray((255 - checker_array).astype(np.uint8))

# === Load into PsychoPy
checker_A = visual.ImageStim(
    win=myWin,
    image=checker_img,
    size=(bar_length, bar_width),
    units='deg',
    interpolate=False
)

checker_B = visual.ImageStim(
    win=myWin,
    image=checker_img_inv,
    size=(bar_length, bar_width),
    units='deg',
    interpolate=False
)

# If we want to output movie, we want the white instead of checker board. 
if expInfo['mode'] == 'outputMovie':
    checker_A.image = white_bar_img
    checker_B.image = white_bar_img

# Create a circular aperture of 10° diameter (5° radius)
aperture = visual.Aperture(
    win=myWin,
    size=10.0,  # diameter in degrees
    shape='circle'
)

triggerText = visual.TextStim(
    win=myWin,
    color='white',
    height=0.5,
    pos=(0, 1.5),
    text='Experiment will start soon.\n Waiting for scanner'
    )

instructText = visual.TextStim(
    win=myWin,
    color='white',
    height=0.5,
    pos=(0, 1.5),
    text='Please Fixate on the dot at all times.\n Your fixation is monitored by eyetracker. \n Press 1 immediately to continue'
)

# fixation dot
dotFix = visual.Circle(
    myWin,
    autoLog=False,
    name='dotFix',
    units='pix',
    radius=5,
    fillColor=[1.0, 0.0, 0.0],
    lineColor=[1.0, 0.0, 0.0],
    )


endText = visual.TextStim(
    win=myWin,
    color="white",
    height=0.5,
    text="Please rest until further instructions"
    )
# %% FUNCTION encapsulating stimuli 

def flicker_until_trigger(win, stim_A, stim_B, flicker_rate, position=(0, 0),
                          fix_stim=None, first_run=False, 
                          save_frames=False, outFolder=None):
    flicker_interval = 1.0 / flicker_rate
    clock = core.Clock()
    last_flip_time = clock.getTime()
    global frame_idx
    flicker_index = 0  # ✅ independent counter for flickering

    # === Immediate display if first run
    if first_run:
        stim_A.pos = position
        stim_A.draw()
        if fix_stim and not save_frames:
            fix_stim.draw()
        win.flip()

    while True:
        keys = event.getKeys()
        if 'escape' in keys:
            win.close()
            core.quit()
        if '5' in keys:
            # Redraw final frame for saving
            stim = stim_A if flicker_index % 2 == 0 else stim_B
            stim.pos = position
            stim.draw()
            if fix_stim and not save_frames:
                fix_stim.draw()
            win.flip()

            if save_frames and outFolder is not None:
                win.getMovieFrame(buffer='front')
                win.saveMovieFrames(os.path.join(outFolder, f"frame_{frame_idx:03d}.png"))
            frame_idx += 1  # ✅ increment only ONCE per TR
            break

        now = clock.getTime()
        if now - last_flip_time >= flicker_interval:
            stim = stim_A if flicker_index % 2 == 0 else stim_B
            stim.pos = position
            stim.draw()
            if fix_stim and not save_frames:
                fix_stim.draw()
            win.flip()
            last_flip_time = now
            flicker_index += 1  # ✅ flicker toggling only
            

def show_fixation_until_triggers(win, fix_stim, num_triggers=10, save_frames=False, 
                                 outFolder=None):
    """
    Show fixation stimulus and wait for a specified number of '5' triggers.

    Args:
        win: PsychoPy window
        fix_stim: A visual stimulus (e.g., dotFix) to be drawn
        num_triggers: Number of '5' triggers to wait for
    """
    n_triggers = 0
    global frame_idx
    
    while n_triggers < num_triggers:
        keys = event.getKeys()
        if 'escape' in keys:
            win.close()
            core.quit()
        
        if '5' in keys:
            n_triggers += 1
    
            # Save frame ONLY at trigger
            if save_frames and frame_idx is not None and outFolder is not None:
                win.getMovieFrame(buffer='front')
                win.saveMovieFrames(os.path.join(outFolder, f"frame_{frame_idx:03d}.png"))
                frame_idx += 1
        elif save_frames==False:
            # Just show fixation without saving
            fix_stim.draw()
        win.flip()

# %% EYELINK SETUP
# Set this variable to True if you use the built-in retina screen as your
# primary display device on macOS. If have an external monitor, set this
# variable True if you choose to "Optimize for Built-in Retina Display"
# in the Displays preference settings.
use_retina = False
# Set this variable to True to run the script in "Dummy Mode"
if expInfo['eyelink'] == 'True':
    dummy_mode = False
elif expInfo['eyelink'] == 'False':
    dummy_mode = True
# Set this variable to True to run the task in full screen mode
full_screen = True
# Set up EDF data file name and local data folder
# The EDF data filename should not exceed 8 alphanumeric characters
# use ONLY number 0-9, letters, & _ (underscore) in the filename
edf_fname = 'EYE'
# We download EDF data file from the EyeLink Host PC to the local hard
# drive at the end of each testing session, here we rename the EDF to
# include session start date/time
#time_str = time.strftime("_%Y_%m_%d_%H_%M", time.localtime())
session_identifier = edf_fname
# create a folder for the current testing session in the data folder for the subject 
session_folder = os.path.join(subjFolderName, session_identifier)
if not os.path.exists(session_folder):
    os.makedirs(session_folder)

print(f"session_folder = {session_folder}")

'''
----------------# Connect to the EyeLink Host PC-----------------------
'''
# The Host IP address, by default, is "100.1.1.1".
# the "el_tracker" objected created here can be accessed through the Pylink
# Set the Host PC address to "None" (without quotes) to run the script
# in "Dummy Mode"
if dummy_mode:
    el_tracker = pylink.EyeLink(None)
else:
    try:
        el_tracker = pylink.EyeLink("100.1.1.1")
    except RuntimeError as error:
        print('ERROR:', error)
        core.quit()
        sys.exit()

# Step 2: Open an EDF data file on the Host PC
edf_file =  f"RF_run{expInfo['run']}.EDF"
try:
    el_tracker.openDataFile(edf_file)
except RuntimeError as err:
    print('ERROR:', err)
    # close the link if we have one open
    if el_tracker.isConnected():
        el_tracker.close()
    core.quit()
    sys.exit()
# Add a header text to the EDF file to identify the current experiment name
# This is OPTIONAL. If your text starts with "RECORDED BY " it will be
# available in DataViewer's Inspector window by clicking
# the EDF session node in the top panel and looking for the "Recorded By:"
# field in the bottom panel of the Inspector.
preamble_text = 'RECORDED BY %s' % os.path.basename(__file__)
el_tracker.sendCommand("add_file_preamble_text '%s'" % preamble_text)

# Put the tracker in offline mode before we change tracking parameters
el_tracker.setOfflineMode()

# Get the software version:  1-EyeLink I, 2-EyeLink II, 3/4-EyeLink 1000,
# 5-EyeLink 1000 Plus, 6-Portable DUO
eyelink_ver = 5  # set version to 0, in case running in Dummy mode
if not dummy_mode:
    vstr = el_tracker.getTrackerVersionString()
    eyelink_ver = int(vstr.split()[-1].split('.')[0])
    # print out some version info in the shell
    print('Running experiment on %s, version %d' % (vstr, eyelink_ver))

'''
----------------# Setting up for CALIBRATION and other stuff-----------------------
'''
# File and Link data control
# what eye events to save in the EDF file, include everything by default
file_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT'
# what eye events to make available over the link, include everything by default
link_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON,FIXUPDATE,INPUT'
# what sample data to save in the EDF data file and to make available
# over the link, include the 'HTARGET' flag to save head target sticker
# data for supported eye trackers
if eyelink_ver > 3:
    file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,HTARGET,GAZERES,BUTTON,STATUS,INPUT'
    link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,HTARGET,STATUS,INPUT'
else:
    file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,GAZERES,BUTTON,STATUS,INPUT'
    link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,INPUT'
el_tracker.sendCommand("file_event_filter = %s" % file_event_flags)
el_tracker.sendCommand("file_sample_data = %s" % file_sample_flags)
el_tracker.sendCommand("link_event_filter = %s" % link_event_flags)
el_tracker.sendCommand("link_sample_data = %s" % link_sample_flags)

# Optional tracking parameters
# Sample rate, 250, 500, 1000, or 2000, check your tracker specification
# if eyelink_ver > 2:
#     el_tracker.sendCommand("sample_rate 1000")
# Choose a calibration type, H3, HV3, HV5, HV13 (HV = horizontal/vertical),
el_tracker.sendCommand("calibration_type = HV9")

# Set a gamepad button to accept calibration/drift check target
# You need a supported gamepad/button box that is connected to the Host PC
el_tracker.sendCommand("button_function 5 'accept_target_fixation'")

# Get screen resolution in pixels
scn_width, scn_height = myWin.size

# EyeLink coordinate setup
el_coords = "screen_pixel_coords = 0 0 %d %d" % (scn_width - 1, scn_height - 1)
el_tracker.sendCommand(el_coords)

# Data Viewer setup
dv_coords = "DISPLAY_COORDS  0 0 %d %d" % (scn_width - 1, scn_height - 1)
el_tracker.sendMessage(dv_coords)

os.chdir(_thisDir) # make sure that EyeLinkCoreGraphicsPsychoPy can be read
# Graphics environment setup
#sound.AudioDeviceInfo(deviceIndex = -1, deviceName =u'Microsoft Sound Mapper - Output', inputChannels = 0, outputLatency = (0.09, 0.18), inputLatency = (0.09, 0.18), defaultSampleRate = 44100)
genv = EyeLinkCoreGraphicsPsychoPy(el_tracker, myWin)
print(genv)  # print out the version number of the CoreGraphics library

# Set background and foreground colors for the calibration target
# in PsychoPy, (-1, -1, -1)=black, (1, 1, 1)=white, (0, 0, 0)=mid-gray
foreground_color = (-1, -1, -1)
background_color = myWin.color
genv.setCalibrationColors(foreground_color, background_color)

# Set up the calibration target
# The target could be a "circle" (default), a "picture", a "movie" clip,
# or a rotating "spiral". To configure the type of calibration target, set
# genv.setTargetType to "circle", "picture", "movie", or "spiral", e.g.,
# genv.setTargetType('picture')
#
# Use gen.setPictureTarget() to set a "picture" target
# genv.setPictureTarget(os.path.join('images', 'fixTarget.bmp'))
#
# Use genv.setMovieTarget() to set a "movie" target
# genv.setMovieTarget(os.path.join('videos', 'calibVid.mov'))

# Use a picture as the calibration target
genv.setTargetType('picture')

genv.setPictureTarget(os.path.join(_thisDir,'images', 'fixTarget.bmp'))

# Configure the size of the calibration target (in pixels)
# this option applies only to "circle" and "spiral" targets
# genv.setTargetSize(24)

# Beeps to play during calibration, validation and drift correction
# parameters: target, good, error
#     target -- sound to play when target moves
#     good -- sound to play on successful operation
#     error -- sound to play on failure or interruption
# Each parameter could be ''--default sound, 'off'--no sound, or a wav file
genv.setCalibrationSounds('', '', '')

# resolution fix for macOS retina display issues
if use_retina:
    genv.fixMacRetinaDisplay()

# Request Pylink to use the PsychoPy window we opened above for calibration
pylink.openGraphicsEx(genv)

os.chdir(parentDir) # change dirctory back

'''
 -------------# define a few helper functions for EYELINK handling ---------------------
'''
def clear_screen(win):
    """ clear up the PsychoPy window"""
    win.fillColor = genv.getBackgroundColor()
    win.flip()
    
def show_msg(win, text, wait_for_keypress=True):
    """ Show task instructions on screen"""
    msg = visual.TextStim(win, text,
                          color=genv.getForegroundColor(),
                          wrapWidth=scn_width/2)
    clear_screen(win)
    msg.draw()
    win.flip()
    # wait indefinitely, terminates upon any key press
    if wait_for_keypress:
        event.waitKeys()
        clear_screen(win)

def abort_trial():
    """Ends recording """
    el_tracker = pylink.getEYELINK()
    # Stop recording
    if el_tracker.isRecording():
        # add 100 ms to catch final trial events
        pylink.pumpDelay(100)
        el_tracker.stopRecording()
    # clear the screen
    clear_screen(myWin)
    # Send a message to clear the Data Viewer screen
    bgcolor_RGB = (116, 116, 116)
    el_tracker.sendMessage('!V CLEAR %d %d %d' % bgcolor_RGB)
    # send a message to mark trial end
    el_tracker.sendMessage('TRIAL_RESULT %d' % pylink.TRIAL_ERROR)
    return pylink.TRIAL_ERROR

def terminate_task():
    """ Terminate the task gracefully and retrieve the EDF data file

    file_to_retrieve: The EDF on the Host that we would like to download
    win: the current window used by the experimental script
    """
    el_tracker = pylink.getEYELINK()
    if el_tracker.isConnected():
        # Terminate the current trial first if the task terminated prematurely
        error = el_tracker.isRecording()
        if error == pylink.TRIAL_OK:
            abort_trial()
        # Put tracker in Offline mode
        el_tracker.setOfflineMode()
        # Clear the Host PC screen and wait for 500 ms
        el_tracker.sendCommand('clear_screen 0')
        pylink.msecDelay(500)
        # Close the edf data file on the Host
        el_tracker.closeDataFile()
        # Show a file transfer message on the screen
        #msg = 'EDF data is transferring from EyeLink Host PC...'
        #show_msg(myWin, msg, wait_for_keypress=False)
        # Download the EDF data file from the Host PC to a local data folder
        # parameters: source_file_on_the_host, destination_file_on_local_drive
        local_edf = os.path.join(session_folder, edf_file)
        print("LOCAL_EDF = " + local_edf)
        try:
            el_tracker.receiveDataFile(edf_file, local_edf)
        except RuntimeError as error:
            print('ERROR:', error)
        # Close the link to the tracker.
        el_tracker.close()
    # close the PsychoPy window
    myWin.close()
    # quit PsychoPy
    core.quit()
    sys.exit()
'''
---------------# Set up the camera and calibrate the tracker ---------------------
'''
# Show the task instructions
task_msg = 'In the task, you may press the SPACEBAR to end a trial\n' + \
    '\nPress Ctrl-C to if you need to quit the task early\n'
if dummy_mode:
    task_msg = task_msg + '\nNow, press ENTER to start the task'
else:
    task_msg = task_msg + '\nNow, press ENTER twice to calibrate tracker'
show_msg(myWin, task_msg)

# Calibration 
# skip this step if running the script in Dummy Mode
if not dummy_mode:
    try:
        el_tracker.doTrackerSetup()        
    except RuntimeError as err:
        print('ERROR:', err)
        el_tracker.exitCalibration()

# put tracker in idle/offline mode before recording
el_tracker.setOfflineMode()
# Start recording
# arguments: sample_to_file, events_to_file, sample_over_link,
# event_over_link (1-yes, 0-no)
try:
    el_tracker.startRecording(1, 1, 1, 1)
except RuntimeError as error:
    print("ERROR:", error)
    abort_trial()



# %% SIMPLE FLICKERING CHECKERBOARD BAR — No movement
# Show flickering bar at fixed center position for 5 seconds

aperture.enabled = True  # globally enable masking
first_run = True  # control initial display behavior to display flicker without trigger

# Instruction
instructText.draw()
dotFix.draw()
myWin.flip()
# Wait for keypress
while True:
    keys = event.getKeys()
    if '1' in keys:
        break
    elif 'escape' in keys:
        myWin.close()
        core.quit()

# Scanner ready
triggerText.draw()
dotFix.draw()
myWin.flip()
# Wait for scanner trigger ('5')
while True:
    keys = event.getKeys()
    if '5' in keys:
        break
    elif 'escape' in keys:
        myWin.close()
        core.quit()

# for white bar savinf 
frame_idx = 0

el_tracker.sendMessage(f"EXPERIMENT_START {expInfo['expName']}")

# Beginning fixation
show_fixation_until_triggers(myWin, dotFix, num_triggers=10, 
                             save_frames=(expInfo['mode'] == 'outputMovie'),
                             outFolder=PNGFolderName)

first_run = True
for step in stim_schedule:
    position = step['position']
    orientation = step['orientation']
    
    # Optional: rotate stimuli here if orientation changes
    checker_A.ori = orientation
    checker_B.ori = orientation
    aperture.enabled = True  # enable for current frame
    
    flicker_until_trigger(myWin, checker_A, checker_B, flicker_rate=8,
                      position=position,
                      fix_stim=dotFix,
                      first_run=first_run,
                      save_frames=(expInfo['mode'] == 'outputMovie'),
                      outFolder=PNGFolderName
                      )
    
    
    first_run = False

# End fixation 
show_fixation_until_triggers(myWin, dotFix, num_triggers=16-1, # trigger at the end of each volume should -1 other wise it will be 17
                             save_frames=(expInfo['mode'] == 'outputMovie'),
                             outFolder=PNGFolderName)
# Make up for the last sec
dotFix.draw()
myWin.flip()
core.wait(1.0)

# Byebye
# EYETRACKER CLOSE DISPLAY AND SAVE EDF
os.chdir(parentDir)
el_tracker.stopRecording()
terminate_task()

endText.draw()
myWin.flip()
core.wait(3.0)
myWin.close()
core.quit()
