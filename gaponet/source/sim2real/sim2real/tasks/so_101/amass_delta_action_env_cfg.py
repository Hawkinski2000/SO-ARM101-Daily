# Copyright (c) 2022-2025, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import os
from dataclasses import MISSING

from sim2real_assets import SO101_CFG

from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import ArticulationCfg
from isaaclab.envs import DirectRLEnvCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sim import PhysxCfg, SimulationCfg
from isaaclab.utils import configclass

MOTIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "motions")

ROBOT_DICT = {
    "so101": {"model": SO101_CFG, "motion_dir": "so101_motions"},   # no urdf_path key — we're skipping Pinocchio torque
}


@configclass
class SO101EnvCfg(DirectRLEnvCfg):

    robot_name: str = "so101"
    if_torque_input = False    # explicit, unconditional — no more relying on the urdf_path branch

    # env
    episode_length_s = 1.0
    decimation = 4
    mode = "train"
    task_name = "so_101"

    # spaces — 6 DOF, not 10
    observation_space = 25 * 6
    action_space = 1 * 6
    state_space = 0
    num_amp_observations = 5
    amp_observation_space = 5 * 6

    min_runs = 1
    early_termination = False       # arm is bolted down, can't "fall"
    reference_body = "base"         # per the FrameTransformerCfg evidence

    reset_strategy = "random"

    sim: SimulationCfg = SimulationCfg(
        dt=1 / 200,
        render_interval=decimation,
        physx=PhysxCfg(
            gpu_found_lost_pairs_capacity=2**24,
            gpu_total_aggregate_pairs_capacity=2**24,
        ),
    )

    scene: InteractiveSceneCfg = InteractiveSceneCfg(num_envs=4096, env_spacing=10.0, replicate_physics=True)

    robot: ArticulationCfg = ROBOT_DICT[robot_name]["model"].replace(prim_path="/World/envs/env_.*/Robot")

    motion_dir = MOTIONS_DIR
    motion_path = os.path.join(motion_dir, f"motion_amass/{ROBOT_DICT[robot_name]['motion_dir']}")
    train_motion_file = os.path.join(motion_path, "so101_train.npz")   # placeholder name
    test_motion_file = os.path.join(motion_path, "so101_test.npz")    # placeholder name