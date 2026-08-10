# SO-ARM101-Daily

Daily build-log for the SO-ARM101. Updating every day, no exceptions, while working through NVIDIA's [Train an SO-101 Robot From Sim-to-Real With NVIDIA Isaac](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/index.html#) course. Public accountability to keep me on track.

## Log

### [Date]

- What I did:
- What I learned:
- What's next:

---

### 2026-08-01

- What I did:
  - I created this repository and README.
  - [Clone the Repository](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/06-get-the-code.html#clone-the-repository): I added files from the [Sim-to-Real-SO-101-Workshop](https://github.com/isaac-sim/Sim-to-Real-SO-101-Workshop) repository.
  - [Build the Teleop and Simulation Container](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/06-get-the-code.html#build-the-teleop-and-simulation-container): I built the teleop and simulation container.
  - [Get the Models](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/06-get-the-code.html#get-the-models): I downloaded the four models from Hugging Face.
- What I learned: Admittedly, not much today since it was mostly just running commands. I suppose I did "learn" that apparently there are four models, not just one. I'm not sure why yet, maybe they're slightly different approaches to the same task.
- What's next: I will need to [Build the Real Robot and Inference Server](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/06-get-the-code.html#build-the-real-robot-and-inference-server), which apparently can take up to an hour to complete. It says I technically don't need it until later modules, but I'd like to just follow the course sequentially whenever possible to keep things simple. After that it looks like I will be calibrating the arm.

### 2026-08-02

- What I did:
  - [Build the Real Robot and Inference Server](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/06-get-the-code.html#build-the-real-robot-and-inference-server): I built the real robot and inference server. This was tricky for two reasons:
    - I encountered an error when running

      ```bash
      ./docker/real/build.sh blackwell
      ```

      similar to the one mentioned in [this issue](https://github.com/isaac-sim/Sim-to-Real-SO-101-Workshop/issues/4), due to this line in `Dockerfile.blackwell`:

      ```dockerfile
      RUN python3 -m pip uninstall -y torch torchvision torchaudio && python3 -m pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu130
      ```

      I believe it's because flash-attention has `-std=c++17` in its [setup.py](https://github.com/Dao-AILab/flash-attention/blob/c46b8144f2d5039d3d3de05da1b668325130bb35/setup.py#L314), but [PyTorch 2.12.0+ requires C++20](https://github.com/pytorch/pytorch/pull/178662). So pinning it to 2.11.0 is a workaround for now.

    - WSL was crashing from this line in `Dockerfile.blackwell`:
      ```dockerfile
      RUN export MAX_JOBS=2 && python3 -m pip install flash-attn --no-build-isolation --no-cache-dir
      ```
      likely due to insufficient memory since apparently the compilation of flash-attn is extremely memory-hungry. So I just used a prebuilt wheel from [mjun0812/flash-attention-prebuild-wheels](https://github.com/mjun0812/flash-attention-prebuild-wheels) matching torch 2.11.0 + cu130 + Python 3.10, instead of having to compile it myself. I replaced that line with:
      ```dockerfile
      RUN python3 -m pip install https://github.com/mjun0812/flash-attention-prebuild-wheels/releases/download/v0.9.4/flash_attn-2.8.3+cu130torch2.11-cp310-cp310-linux_x86_64.whl
      ```

  - [Powering On the Robot](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/07-calibrating-so101.html#powering-on-the-robot): I unpacked all of the cables and powered on the leader/follower robots.
  - [Run the Docker Container for This Course](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/07-calibrating-so101.html#run-the-docker-container-for-this-course): I ran the Docker container, however I had to make some modifications to the provided command because I needed to manually pass in my USB ports due to issues with WSL detecting devices.
  - [Identify the Teleop Arm Port](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/07-calibrating-so101.html#identify-the-teleop-arm-port): I was unable to detect the USB ports using the
    ```bash
    lerobot-find-port
    ```
    command due to running everything in WSL. After some research, I figured out I could use a tool called [usbipd-win](https://github.com/dorssel/usbipd-win), and running:
    ```powershell
    usbipd attach --wsl --busid=<BUSID>
    ```
    in PowerShell made the devices visible to WSL.
  - [Identify the Robot Arm Port](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/07-calibrating-so101.html#identify-the-robot-arm-port): See the above bullet.
  - [Calibration Process](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/07-calibrating-so101.html#calibration-process): I calibrated the leader/follower arms.
  - [Check Your Work](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/07-calibrating-so101.html#check-your-work): I ran
    ```bash
    python docker/real/scripts/so101_check_calibration.py
    ```
    to check that my calibration was correct. Apparently most of the joints had significant deviations from the means of the calibration dataset and most of them said "⚠ WARN" instead of "✓ PASS". Not sure why this was the case because I definitely moved the joints to their absolute limits. Maybe it's just due to some variations in the print model/quality or motors. However, the section does mention "A warning is advisory and does not necessarily mean the calibration is incorrect", so it's most likely fine.
  - [Teleoperation](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/08-operating-so101.html#teleoperation): I was able to teleoperate the robot using the leader arm. This was pretty fun, and admittedly I did practice picking up vials for a bit. It has some quirks and the joints can feel a bit stiff at times, but it's mostly very intuitive to operate.

- What I learned:
  - I may need to invest in additional RAM at some point due to being unable to compile flash-attention on my own machine.
  - Using USB devices with WSL is tricky but possible. I'm hoping this doesn't cause issues with the cameras later.
  - Teleoperating the robot is fairly intuitive.
- What's next: [Camera Setup](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/08-operating-so101.html#camera-setup): I need to set up the wrist-mounted camera and webcam. I'm hoping WSL does not cause major issues with this.

### 2026-08-03

- What I did:
  - I moved the arms from my desk to the workspace.
  - I bought a USB extension cable to reach the arms/cameras in the workspace from my computer.
  - I recalibrated the arms in the workspace and tested picking up some vials.
  - [Camera Setup](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/08-operating-so101.html#camera-setup):
    - I attached the wrist-mounted camera to the follower arm.
    - I attempted to detect the camera in WSL using the
      ```bash
      lerobot-find-cameras opencv
      ```
      command after running
      ```powershell
      usbipd attach --wsl --busid=<BUSID>
      ```
      but was unable to. I will need to investigate this further tomorrow.
- What I learned: As I feared, there may be issues with WSL detecting cameras. The process that worked for detecting the arm USB ports unfortunately did not work for the wrist-mounted camera. I will need to investigate this further.
- What's next: Hopefully I will find a way to detect the wrist-mounted camera and webcam in WSL. Then, the next step is to [Run Teleoperation With Cameras](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/08-operating-so101.html#run-teleoperation-with-cameras).

### 2026-08-04

- What I did:
  - I spent some time trying to get the wrist-mounted camera detected in WSL. Apparently WSL doesn't support USB webcams by default, so I built a custom kernel (with a lot of help from Claude) to fix that.
  - I was able to detect `/dev/video0` in WSL, but hit a new problem: frames come through corrupted, seemingly because streaming video over `usbip` just isn't reliable.
- What I learned: Getting USB cameras to work in WSL is very tricky. I will once again need to do more research.
- What's next: I'm going to try capturing the camera on the Windows side and stream the frames into WSL, apparently that might work. Or maybe I'll find an issue somewhere that mentions a solution.

### 2026-08-05

- What I did:
  - I decided to just install Ubuntu on a separate drive instead of trying to make WSL work. There have been too many workarounds, and I'm afraid things will only get more difficult.
  - I ordered a [2TB SSD](https://a.co/d/0erEIk2Q) to install and boot Ubuntu on. I realize this is likely overkill just for Ubuntu, but I may want the extra storage space in the future for datasets, AI models, etc.
  - I ordered a [128GB flash drive](https://a.co/d/020EsMnX). Yes, also overkill, but it might be useful.
  - I read the [Install Ubuntu Desktop](https://ubuntu.com/desktop/docs/en/latest/tutorial/install-ubuntu-desktop/#install-ubuntu-desktop) tutorial.
- What I learned: Installing Ubuntu is probably not as scary as I'd initially thought. I probably should have done this initially since I was hearing about the difficulties people were having with running the SO-ARM101 and/or cameras with WSL, and early in the course it explicitly mentions in the [Computer Hardware Prerequisites](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/02-how-to-take-this-course.html#computer-hardware-prerequisites) section that they tested the workshop on Ubuntu Linux 24.04, with no mention of other operating systems.
- What's next: I should receive the SSD and flash drive tomorrow. I'll have to open my case to install the SSD but it should be quick. Installing Ubuntu shouldn't be too painful, and then I will have to repeat most of the course to get to where I left off, but I'm already familiar with the process. Hopefully then the cameras will work!

### 2026-08-06

- What I did:
  - I installed the SSD in my computer.
  - I downloaded the Ubuntu image to my flash drive.
  - I installed Ubuntu on my new SSD.
  - I played around with Ubuntu for a bit and installed some basic apps like Chrome and Visual Studio Code.
- What I learned: Installing Ubuntu was pretty easy. It will take some getting used to since the UI, shortcuts, navigating tabs, etc. are very different from Windows.
- What's next: I will need to repeat the [Get the Code and Models](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/06-get-the-code.html#get-the-code-and-models) section of the course now that I'm on Ubuntu, starting with [Build the Teleop and Simulation Container](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/06-get-the-code.html#build-the-teleop-and-simulation-container).

### 2026-08-07

- What I did:
  - [Build the Teleop and Simulation Container](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/06-get-the-code.html#build-the-teleop-and-simulation-container): I built the teleop and simulation container (again) on Ubuntu.
  - [Build the Real Robot and Inference Server](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/06-get-the-code.html#build-the-real-robot-and-inference-server): I built the real robot and inference server (again) on Ubuntu. 
  - [Get the Models](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/06-get-the-code.html#get-the-models): I downloaded the four models from Hugging Face (again) on Ubuntu.
  - I recalibrated and tested the arms.
- What I learned: It's much easier to follow the course when the default commands work, like `lerobot-find-port`, instead of finding workarounds due to WSL quirks.
- What's next: Hopefully now I can get the cameras to work and continue where I left off!

### 2026-08-08

- What I did:
  - [Camera Setup](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/08-operating-so101.html#camera-setup): I was finally able to detect the cameras!
  - [Run Teleoperation With Cameras](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/08-operating-so101.html#run-teleoperation-with-cameras): I ran teleoperation with the wrist-mounted camera and webcam. 
- What I learned: I can see why this might be a tricky task for a model to learn, and why it's probably necessary to have a second external camera, because the wrist-mounted camera only provides a very narrow view of what the arm happens to be currently pointed at.
- What's next: [Sim-to-Real Strategy 1: Domain Randomization](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/09-strategy1-dr-teleop.html#sim-to-real-strategy-1-domain-randomization): It looks like I will be teleoperating the arm in simulation with Isaac Lab, which should be very interesting!

### 2026-08-09

- What I did:
  - I was getting a seg fault when starting Isaac Sim. Apparently it was an issue with the GPU driver so I downgraded that and it worked.
  - I was missing assets for the simulation because the asset files were just Git LFS pointer files, not the real data. I pulled the actual files from the repo and was able to launch the simulation.
  - [Practice Teleoperation in Simulation](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/09-strategy1-dr-teleop.html#practice-teleoperation-in-simulation): I was able to teleoperate the arm in the Isaac Sim simulation which was a very interesting and somewhat strange experience. There are some quirks with the physics and such and the environment had a weird sort of uncanny familiarity to it.
- What I learned: Teleoperating the robot in simulation unfortunately does not feel like a vritual exact replica of the real thing, and there are some subtle but noticable quirks with friction, collisions, gravity, etc.
- What's next: [Start Recording Demonstrations](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/09-strategy1-dr-teleop.html#start-recording-demonstrations): The next step will be to actually start recording dataset examples in the simulation.