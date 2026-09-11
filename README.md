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

### 2026-08-10

- What I did: [Recording Demonstrations](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/09-strategy1-dr-teleop.html#recording-demonstrations): I recorded my first 5 demonstrations in simulation. I had to stop there because Isaac Sim would crash, but only and consistently after trying to save the second recording in that session. I think it might be related to a "Svt[warn]: Failed to set thread priority: Invalid argument" error I was getting after the episode gets copied to the CPU to be processed and saved.
- What I learned: Recording demonstrations is actually surprisingly hard, but it seems like I'm rapidly improving.
- What's next: I will need to investigate the crashing issue since setting up Isaac Sim for every recording is very time-consuming, and apparently I should aim for at least 70 of them.

### 2026-08-11

- What I did: I discovered that the issue from yesterday that was causing Isaac Sim to crash was actually a memory issue, not anything related to the "Svt[warn]: Failed to set thread priority: Invalid argument" warning. After saving an episode, it seems like they accumulate in memory for some reason. Attempting to save a second episode was using up all of my memory, so Isaac Sim was being killed. I added a 16GB swapfile as a workaround and successfully recorded ~6 demonstrations in a row with no crashes.
- What I learned: Once again, I have more evidence that maybe I need to invest in more RAM.
- What's next: I think now I can actually (hopefully) start recording a meaningful number of demonstrations without interruptions.

### 2026-08-12

- What I did: I started a new dataset from scratch because the previous one was cluttered with tests from when I was debugging the crashing issue, and I only had 12 recordings anyway. Today I recorded 10 high quality demonstrations in a row without a single crash.
- What I learned: I'm getting a bit better at racking vials smoothly and efficiently.
- What's next: I will need to continue recording demonstrations until I reach at least 70, or ideally maybe more like 100. I'll probably try to do at least 10-20 per day.

### 2026-08-13

- What I did: I just recorded 10 more demonstrations today. I'm at 20 now.
- What I learned: Not really much today besides improving slightly at operating the arm, if that counts.
- What's next: I will need to continue recording demonstrations until I reach at least 70, or ideally maybe more like 100. I'll probably try to do at least 10-20 per day.

### 2026-08-14

- What I did: I just recorded 30 more demonstrations today. I'm at 50 now.
- What I learned: Not really much today besides improving slightly at operating the arm, if that counts.
- What's next: I will need to continue recording demonstrations until I reach at least 70, or ideally maybe more like 100. I'll probably try to do at least 10-20 per day.

### 2026-08-15

- What I did:
  - I recorded another 50 demonstrations today. I'm at 100 now. I think that should be enough.
  - I read the remainder of the [Sim-to-Real Strategy 1: Domain Randomization](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/09-strategy1-dr-teleop.html#sim-to-real-strategy-1-domain-randomization) section.
- What I learned: I learned more about domain randomization and what specific conditions are randomized between resets of the simulation.
- What's next: Next is the [Isaac GR00T: Vision-Language-Action Models](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/10-groot.html#isaac-gr00t-vision-language-action-models) section, which should be very interesting!

### 2026-08-16

- What I did: I read through the [Isaac GR00T: Vision-Language-Action Models](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/10-groot.html#isaac-gr00t-vision-language-action-models) page.
- What I learned: I learned about GR00T and how to post-train it on a dataset.
- What's next: I will likely try to complete the [Hands-On: Run GR00T Post-Training Yourself](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/10-groot.html#hands-on-run-gr00t-post-training-yourself) section rather than just using the provided fine-tuned models. I think it should be an interesting learning experience.

### 2026-08-17

- What I did: I attempted the [Hands-On: Run GR00T Post-Training Yourself](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/10-groot.html#hands-on-run-gr00t-post-training-yourself) section, but the script that ran on the Brev instance failed. I think I found a workaround, but I will need to attempt the fine-tuning tomorrow when I have more time.
- What I learned: Brev is cool. I have used cloud GPU instances in the past like Lambda and Runpod, but it seems like Brev's "Launchables" are more like pre-configured projects that makes the setup a lot faster/easier than just using a generic empty machine.
- What's next: Hopefully I will figure out the fine-tuning tomorrow.

### 2026-08-18

- What I did: I was able to start fine-tuning GR00T on the Brev instance, however I had to stop it at ~20% progress because it's going to take another 2+ hours to complete, and I'm out of time tonight. Unfortunately, for some reason a checkpoint was not saved, so I will have to restart it in the morning. Brev preserves all files on the instance when it's stopped though, so it should be fairly quick to get started tomorrow morning.
- What I learned: Time management and checkpoints are important for training models.
- What's next: Hopefully I will finally be able to fine-tune GR00T on my dataset. After that is the [Sim Evaluation](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/11-sim-evaluation.html#sim-evaluation) section.

### 2026-08-19

- What I did: I successfully fine-tuned GR00T on my dataset of recordings on the Brev instance and then uploaded the model to a [Hugging Face repo](https://huggingface.co/Hawkinski/grootn16-finetune_Hawkinski_SOARM-101/tree/main). It took much longer than expected so I'm glad I started it early today.
- What I learned: Training/fine-tuning GR00T takes a very long time, even for an H100.
- What's next: Tomorrow I will start the [Sim Evaluation](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/11-sim-evaluation.html#sim-evaluation) section.

### 2026-08-20

- What I did: I completed the [Sim Evaluation](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/11-sim-evaluation.html#sim-evaluation) section. It was pretty interesting seeing the model I trained replicating the movements I recorded during the demonstrations, however the policy was not able to put a single vial in the rack, though it was able to pick one up a few times. It usually just gets close to the vials like it's thinking about picking one up but rarely actually does.
- What I learned: It's very interesting how, despite only training on 100 examples, the model has clearly learned about the "putting vials in the rack" task. It was clearly moving towards them and opening the gripper very similar to the way I did during the demonstrations.
- What's next: I'm curious why my policy is struggling to even put a single vial in the rack. I think I'll try using the provided `aravindhs-NV/grootn16-finetune_sreetz-so101_teleop_vials_rack_left` model just to see if the performance is noticably different.

### 2026-08-21

- What I did: I tested the [Sim Evaluation](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/11-sim-evaluation.html#sim-evaluation) section again, but this time I tried the provided `aravindhs-NV/grootn16-finetune_sreetz-so101_teleop_vials_rack_left` model. It actually performed significantly better than my model, despite only being trained on 75 demonstrations instead of my 100. It was only able to put a single vial in the rack in the time that I was watching it, however it was much more capable of actually picking up the vials, which my model seriously struggled with for some reason. I can only imagine I must have been a bit too fast during the demonstrations, and maybe moving more slowly and deliberately would have resulted in better performance.
- What I learned: If the difference in model performance is due to the dataset I trained mine on, then I think it must have something to do with how quickly I was moving the arm during my demonstrations. In theory, this seems like plausible explanation for the discrepancy, because I can imagine that maybe the model's actual inference time in practice is not capable of keeping up with fast, aggressive movements during the demonstrations, which may be why the arm seems to freeze up and almost get confused before picking up a vial when running my model.
- What's next: I'm considering extending my dataset or even creating a new one with some slower, more deliberate demonstrations, in hopes of seeing better performance when running the model trained on it.

### 2026-08-22

- What I did: I completed the [Real Evaluation](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/12-real-evaluation.html#real-evaluation) section. As expected, this was very interesting to watch, however the sim-to-real gap is definitely very real. For some reason, the real arm had very choppy, almost "pulsating" movements. I'm not sure what could be causing this. What's even more interesting is when switching from my model to the provided `aravindhs-NV/grootn16-finetune_sreetz-so101_teleop_vials_rack_left` model, it did perform a bit better, but still had that choppy movement, so I'm thinking it's something related to the actual arm, cameras, or workspace itself, rather than the model. The arm was unable to pick up a vial on its own, however with some minor "assistance", I was able to get it to actually rack a vial, which was very exciting to watch.
- What I learned: It seems that the sim-to-real gap is very real, and can result in some weird, unexpected behavior. However, I can tell that the model is definitely still working. It's clearly attempting to replicate what it learned from the simulated demonstrations on the real arm. I helped the arm out by putting a vial in its gripper, and shortly after it cleanly placed it in the rack with surprising grace. This makes me think that the sim-to-real gap may exist, however it may not be as hopelessly wide as one might expect.
- What's next: The next section is [Sim-to-Real Strategy 2: Co-Training With Real Data](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/13-strategy2-cotraining.html#sim-to-real-strategy-2-co-training-with-real-data).

### 2026-08-23

- What I did: I just read through the [Sim-to-Real Strategy 2: Co-Training With Real Data](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/13-strategy2-cotraining.html#sim-to-real-strategy-2-co-training-with-real-data) section today.
- What I learned: Co-training is an interesting strategy, and I was actually thinking something exactly like this might help reduce the sim-to-real gap and could improve the weird choppy movement. It seems sort of like just another form of fine-tuning, where the "base" model trained on demonstrations in simulation is being fine-tuned on real life demonstrations to try to close the gap.
- What's next: Tomorrow I will actually complete the [Sim-to-Real Strategy 2: Co-Training With Real Data](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/13-strategy2-cotraining.html#sim-to-real-strategy-2-co-training-with-real-data) section.

### 2026-08-24

- What I did: I completed the [Sim-to-Real Strategy 2: Co-Training With Real Data](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/13-strategy2-cotraining.html#sim-to-real-strategy-2-co-training-with-real-data) section.
- What I learned: I was skeptical that combining just 5 real demonstrations with the simulated ones and training on that would do anything noticable, but it seemed like the `aravindhs-NV/grootn16-finetune_sreetz-so101_teleop_vials_rack_left_sim_and_real` model was running much more smoothly than the original, which was trained on only simulated demonstrations. The arm appeared to be much more determined to get the vials into the rack this time, however its actual success rate at this was still not very good.
- What's next: Tomorrow I will start the [Sim-to-Real Strategy 3: Augmenting Datasets With Cosmos](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/14-strategy3-cosmos.html) section.

### 2026-08-25

- What I did: I just read the [Sim-to-Real Strategy 3: Augmenting Datasets With Cosmos](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/14-strategy3-cosmos.html) section because I was a bit short on time today.
- What I learned: I figured we would be generating or augmenting data in some way instead of just manually performing all of the demonstrations. Cosmos seems super interesting. Apparently it's a "world foundation model", so I wonder if it's similar at all to "JEPA" which I've also heard is a world model, and which Yann LeCun has made some interesting claims about.
- What's next: Tomorrow I will actually complete the [Sim-to-Real Strategy 3: Augmenting Datasets With Cosmos](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/14-strategy3-cosmos.html) section.

### 2026-08-26

- What I did: I tried the first model (`aravindhs-NV/so100-orig-groot-vials-rack-left-cosmos-70`) in the [Sim-to-Real Strategy 3: Augmenting Datasets With Cosmos](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/14-strategy3-cosmos.html) section.
- What I learned: The `aravindhs-NV/so100-orig-groot-vials-rack-left-cosmos-70` model did not perform as well as I'd hoped. The arm consistently gets stuck when trying to pick up a vial and just sort of rests its gripper on the mat and gives up. Maybe the nearly 1:1 ratio of 75 sim episodes + 70 Cosmos-augmented episodes is the problem, specifically the number of Cosmos-augmented episodes may be excessive.
- What's next: I'll try the other `aravindhs-NV/sreetz-so101_teleop_vials_rack_left_augment_02` model tomorrow, which was only trained on 7 Cosmos-augmented episodes. Maybe the augmented episodes can help in smaller amounts but they can become detrimental if they start to overpower the actual sim or real recordings.

### 2026-08-27

- What I did: I tried the other (`aravindhs-NV/sreetz-so101_teleop_vials_rack_left_augment_02`) model in the [Sim-to-Real Strategy 3: Augmenting Datasets With Cosmos](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/14-strategy3-cosmos.html) section today.
- What I learned: The `aravindhs-NV/sreetz-so101_teleop_vials_rack_left_augment_02` model did not perform noticably better than the other model. I'm wondering if maybe this is just a typical sim-to-real gap, and maybe I should try actually training on some demonstrations in my actual workspace.
- What's next: I'll continue with the course and start the [Sim-to-Real Strategy 4: Measuring and Closing the Gap With SAGE + GapONet](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/15-strategy4-sage.html#sim-to-real-strategy-4-measuring-and-closing-the-gap-with-sage-gaponet) section, however I will likely return to some of these previous sections to see how I could possibly modify things to improve the performance.

### 2026-08-28

- What I did: I read through the [Sim-to-Real Strategy 4: Measuring and Closing the Gap With SAGE + GapONet](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/15-strategy4-sage.html#sim-to-real-strategy-4-measuring-and-closing-the-gap-with-sage-gaponet) section today.
- What I learned: SAGE and GapONet are super interesting. I figured there must be a more elegant way to close the sim-to-real gap than just trial and error. It's funny to me that training a neural net like GapONet can help solve problems related to the training of other neural nets. I think they may potentially be useful for improving some of the issues I've had with my arm's performance. 
- What's next: Tomorrow I will look into SAGE and GapONet further.

### 2026-08-29

- What I did: I completed the [Run Simulation Data Collection](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/15-strategy4-sage.html#run-simulation-data-collection) step in the [Sim-to-Real Strategy 4: Measuring and Closing the Gap With SAGE + GapONet](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/15-strategy4-sage.html#sim-to-real-strategy-4-measuring-and-closing-the-gap-with-sage-gaponet) section today. The arm just sort of scraped its gripper along the ground in Isaac Sim which was a bit odd.
- What I learned: I'll need to actually complete the [Run Real Robot Data Collection](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/15-strategy4-sage.html#run-real-robot-data-collection) step tomorrow, but if I understand correctly, the robot will do what it just did in the simulation in real life and the error or deviation between the joint positions, velocities, and torques will be measured.
- What's next: Tomorrow I'll complete the [Run Real Robot Data Collection](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/15-strategy4-sage.html#run-real-robot-data-collection) step.

### 2026-08-30

- What I did: I completed the [Run Real Robot Data Collection](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/15-strategy4-sage.html#run-real-robot-data-collection) step in the [Sim-to-Real Strategy 4: Measuring and Closing the Gap With SAGE + GapONet](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/15-strategy4-sage.html#sim-to-real-strategy-4-measuring-and-closing-the-gap-with-sage-gaponet) section today. I had the arm perform the same "pick_place" motion in real life where, as expected, the arm sort of just scraped its gripper along the floor of the workspace.
- What I learned: There are definitely some significant deviations between the sim and real data judging by the plots generated for the pick_place motion. The position plots are generally fairly close or even almost exactly the same between sim and real, however the velocity and torque plots are extremely far off at times.
- What's next: It looks like GapONet may not be integrated with GR00T and the SO-101 yet, however it seems very promising for closing this sim-to-real gap. Tomorrow I may look into it in more detail and see how feasible it might be to try integrating it.

### 2026-08-31

- What I did: I just did some brief investigation into the [GapONet](https://github.com/jiemingcui/gaponet) repository today.
- What I learned: While it seems like GapONet is mainly designed for humanoid robots at the moment, the course explicity mentions and shows an example of how it was used for the SO-101, so there is definitley a way to get it working.
- What's next: I'll need to read through the SAGE/GapONet repositories more thoroughly.

### 2026-09-01

- What I did: I just did some more reading of the [GapONet](https://github.com/jiemingcui/gaponet) repository today.
- What I learned: If I understand correctly, GapONet uses my sim and real SAGE outputs for specific motions with its RL model. I think a small issue is that the sim and real outputs were sampled at different frequencies (50Hz for real and 200Hz for sim). I might be able to just modify the command provided in the course for the [Run Simulation Data Collection](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/15-strategy4-sage.html#run-simulation-data-collection) section and repeat the data collection at the correct frequency.
- What's next: I'll try modifying that command and repeating the sim data collection tomorrow.

### 2026-09-02

- What I did: I went through the [Installation](https://github.com/jiemingcui/gaponet#installation) steps for [GapONet](https://github.com/jiemingcui/gaponet) today.
- What I learned: I may have been mistaken about needing both the real and sim motion data, so the different sampling rates may not be an issue. According to the [Motion Data](https://github.com/jiemingcui/gaponet#motion-data) section of the README, the expected format for the motion data only appears to contain keys for real data.
- What's next: I'll start working through the [Adding a New Robot](https://github.com/jiemingcui/gaponet#adding-a-new-robot) section of the README tomorrow to see if I can use the SO-101 with GapONet.

### 2026-09-03

- What I did: I started adding the files/folders mentioned in the [Adding a New Robot](https://github.com/jiemingcui/gaponet#adding-a-new-robot) section of the GapONet README for the SO-101.
- What I learned: I'm realizing adapting the GapONet repository to work with the SO-101 is a pretty significant task, but I think it's possible.
- What's next: I'll continue adapting the files/code for the SO-101. This will likely require extensive reading and comparing of the existing code/files of the repository to understand how everything is supposed to fit together.

### 2026-09-04

- What I did: I continued modifying the files I copied in GapONet to work with the SO-101, like `gaponet/source/sim2real/sim2real/tasks/so_101/__init__.py`, and parts of `gaponet/source/sim2real/sim2real/tasks/so_101/so_101_env.py` and `gaponet/source/sim2real/sim2real/tasks/so_101/so_101_env_cfg.py`.
- What I learned: Some of the files I'm supposed to modify according to the [Adding a New Robot](https://github.com/jiemingcui/gaponet#adding-a-new-robot) section of the README look pretty scary. Like, for example, `gaponet/source/sim2real/sim2real/tasks/so_101/so_101_env.py`, which is currently 1,033 lines long. I'm hoping much of this is either redundant for the SO-101 or does not depend on a specific robot and can be left alone.
- What's next: I'll continue adapting the files/code for the SO-101.

### 2026-09-05

- What I did:
  - I continued modifying the files I copied in GapONet to work with the SO-101.
  - I added a `csv_to_gaponet_npz.py` script to convert SAGE motion outputs for the "pick_place" motion to the `.npz` format that GapONet expects.
  - I was able to perform 50 training iterations on the CPU with `--num_envs=256`, and the model appeared to be converging.
- What I learned: Adapting the code to work with the SO-101 took some time and a lot of AI assistance, but it wasn't as bad as expected. However, I had to run the training on the CPU because of an issue with the default version of Isaac Sim not being compatible with my GPU (5070 TI).
- What's next: I will see if I can upgrade to a newer version of Isaac Sim so I can run the training on the GPU.

### 2026-09-06

- What I did: I collected recordings for all 50 of the so101 motions in the SAGE repo to use as train/test data with GapONet.
- What I learned: I decided to just skip trying to upgrade Isaac Sim because apparently it will be quite a significant refactor since there are breaking API changes. I'll just try training the GapONet model on the CPU for now and see if that's feasible.
- What's next: Now that I've collected data for the 50 motions, I will attempt a serious GapONet training run tomorrow.

### 2026-09-07

- What I did:
  - I trained the GapONet MLP model for 2,000 steps on a train split of data from 40 (80%) of the SAGE motions I recorded yesterday.
  - I ran `play.py` on the test split of data from the remaining 10 (20%) of the SAGE motions. I first tested the untrained `model_0.pt` checkpoint to get a baseline to compare to. It got the following error values for each of the 6 joints (lower is better):

    | Rotation | Pitch | Elbow | Wrist_Pitch | Wrist_Roll | Jaw
    | --- | --- | --- | --- | --- | --- |
    | 297.1616 | 248.1729 | 259.5990 | 244.6589 | 389.6175 | 140.4636

    I then tested it again but on the final `model_1999.pt` checkpoint to see if the model actually learned to generalize to new motions during training, and got the following results:

    | Rotation | Pitch | Elbow | Wrist_Pitch | Wrist_Roll | Jaw
    | --- | --- | --- | --- | --- | --- |
    | 246.3926 | 213.1960 | 210.8976 | 125.2883 | 65.9685 | 47.3049

- What I learned: The model definitely learned to generalize to new motions during training judging by the error values for certain joints being significantly lower for the `model_1999.pt` checkpoint compared to the untrained `model_0.pt` checkpoint. In theory, this means it should be able to compensate somewhat for the sim-to-real gap. I'm not sure how meaningful these results are, however, since some of the error differences for certain joints were not as significant even after 2,000 steps of training. 

- What's next: The next step is to test if the trained GapONet model actually meaningfully narrows the sim-to-real gap when used with the actual arm. I can either use the model in the simulation environment when collecting demonstrations so the simulated arm's movement better matches the real arm's movement, or I can use the model on the real arm during inference time so actions are corrected before execution. I'll probably try GapONet on the real arm first since this does not require collecting an entire dataset and fine-tuning GR00T again.

### 2026-09-08

- What I did: I tried a script that corrects actions in `so101_eval.py` using the exported GapONet `policy.pt` model.
- What I learned: The arm flails wildly when its actions are corrected by the GapONet model. I'm not sure if this is an issue with the script or the model itself. Interestingly, when viewing the joint positions in rerun (with the real arm disabled of course), all 6 joints seem to oscillate together rapidly in a synchronized manner, which is very bizarre. This could be a bug in the script, or the model may have "learned" a strange shortcut for minimizing the error.
- What's next: I'll need to debug this issue tomorrow. I think I might try different checkpoints to see if the behavior differs, which would indicate that this may be a model/training issue.

### 2026-09-09

- What I did: I made some interesting findings today involving the weird synchronized oscillating behavior. First, if the workspace light is turned off, the oscillating sawtooth patterns on the joint positions in rerun disappear almost immediately, and the joint positions become very calm and flat. Shortly after turning the light on they become choppy again. Second, and perhaps more importantly, I had not noticed that this sawtooth pattern actually appears on the joint positions even with the GapONet correction disabled, however it's more subtle. This means it's a fundamental issue with GR00T itself, and GapONet may just be amplifying this for some reason. This is likely related to the choppy movement I noticed in the arm starting back on 08-22. 
- What I learned: GapONet may not be the issue at all. I will need to investigate the GR00T model further.
- What's next: I may try different GR00T checkpoints tomorrow to try to narrow down what, if anything, seems to be correlated with the choppy movement, assuming for now this is a GR00T/model issue.

### 2026-09-10

- What I did: I did some more experiments to narrow down the source of the choppy joint plots. 
- What I learned: My own fine-tuned GR00T checkpoint appears to cause the same sawtooth pattern, however it was trained in the same simulation as the `aravindhs-NV/grootn16-finetune_sreetz-so101_teleop_vials_rack_left` model, so they should be fairly similar. I tried moving the arm closer to my computer so I could skip the USB extension cable and connect the arm/cameras directly, and I also tried a different USB hub for the arm and camera cables. This had no noticable effect, which rules out a cable issue. Considering the waves in the rerun joint plots seemed to increase in frequency when a light is shined on the cameras, I'm thinking this is an issue with the lighting in my real environment not resembling the lighting in the simulated demonstrations GR00T was fine-tuned on.
- What's next: I think I'll try the "co-trained" `aravindhs-NV/grootn16-finetune_sreetz-so101_teleop_vials_rack_left_sim_and_real` model from the [Sim-to-Real Strategy 2: Co-Training With Real Data](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/13-strategy2-cotraining.html#sim-to-real-strategy-2-co-training-with-real-data) section tomorrow. I'm curious to see if the inclusion of real demonstrations in the dataset GR00T was fine-tuned on will have any effect on the choppy joint plots. If it does, that would indicate that this may be a sim-to-real gap between the lighting in the simulation and the lighting in my actual workspace, despite the domain randomization.