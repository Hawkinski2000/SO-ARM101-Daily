"""
Convert SAGE real-robot CSV output into GapONet's expected .npz motion format.

Supports multiple motions of different lengths. Every motion is zero-padded to
the length of the longest one; true (un-padded) lengths are stored in
`motion_lengths` so motion_motor_loader.py can still end episodes at the right
point. This avoids dtype=object entirely (no pickling), sidestepping the
numpy-version-sensitive pickle issue we hit earlier.

Usage:
    python csv_to_gaponet_npz.py \
        --real-dirs sage/output/real/so101/custom/pick_place sage/output/real/so101/custom/custom_motion \
        --out so101_train.npz
"""
import argparse
import ast
import csv
import numpy as np


def load_control(path):
    positions = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["type"] != "CONTROL":
                continue
            positions.append(ast.literal_eval(row["positions"]))
    return np.array(positions, dtype=np.float32)


def load_state_motor(path):
    positions, velocities, torques = [], [], []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["type"] != "STATE_MOTOR":
                continue
            positions.append(ast.literal_eval(row["positions"]))
            velocities.append(ast.literal_eval(row["velocities"]))
            torques.append(ast.literal_eval(row["torques"]))
    return (
        np.array(positions, dtype=np.float32),
        np.array(velocities, dtype=np.float32),
        np.array(torques, dtype=np.float32),
    )


def load_joint_list(path):
    with open(path) as f:
        return [line.strip() for line in f if line.strip()]


def load_one_motion(real_dir):
    """Returns (cmd_pos, real_pos, real_vel, real_torque, joint_sequence) for one motion dir."""
    cmd_pos = load_control(f"{real_dir}/control.csv")
    real_pos, real_vel, real_torque = load_state_motor(f"{real_dir}/state_motor.csv")
    joint_sequence = load_joint_list(f"{real_dir}/joint_list.txt")

    n = min(len(cmd_pos), len(real_pos))
    if len(cmd_pos) != len(real_pos):
        print(f"  WARNING [{real_dir}]: row count mismatch (control={len(cmd_pos)}, "
              f"state_motor={len(real_pos)}). Truncating both to {n}.")
    return cmd_pos[:n], real_pos[:n], real_vel[:n], real_torque[:n], joint_sequence


def pad_to(arr, target_len):
    """Zero-pad a (T, D) array up to (target_len, D)."""
    if arr.shape[0] == target_len:
        return arr
    pad_width = target_len - arr.shape[0]
    return np.pad(arr, ((0, pad_width), (0, 0)), mode="constant")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--real-dirs", nargs="+", required=True,
                     help="one or more dirs, each containing control.csv, state_motor.csv, joint_list.txt")
    ap.add_argument("--out", required=True, help="output .npz path")
    args = ap.parse_args()

    motions = []
    joint_sequence = None
    for real_dir in args.real_dirs:
        print(f"Loading {real_dir} ...")
        cmd_pos, real_pos, real_vel, real_torque, js = load_one_motion(real_dir)
        print(f"  {len(real_pos)} timesteps")
        if joint_sequence is None:
            joint_sequence = js
        elif joint_sequence != js:
            raise ValueError(f"Joint order mismatch in {real_dir}: {js} != {joint_sequence}")
        motions.append((cmd_pos, real_pos, real_vel, real_torque))

    motion_lengths = np.array([m[1].shape[0] for m in motions], dtype=np.int64)
    max_len = int(motion_lengths.max())
    num_dofs = len(joint_sequence)
    num_motions = len(motions)
    print(f"\n{num_motions} motion(s), lengths {motion_lengths.tolist()}, padding all to {max_len}")

    real_dof_positions = np.zeros((num_motions, max_len, num_dofs), dtype=np.float32)
    real_dof_velocities = np.zeros((num_motions, max_len, num_dofs), dtype=np.float32)
    real_dof_positions_cmd = np.zeros((num_motions, max_len, num_dofs), dtype=np.float32)
    real_dof_torques = np.zeros((num_motions, max_len, num_dofs), dtype=np.float32)

    for i, (cmd_pos, real_pos, real_vel, real_torque) in enumerate(motions):
        t = motion_lengths[i]
        real_dof_positions[i, :t] = real_pos
        real_dof_velocities[i, :t] = real_vel
        real_dof_positions_cmd[i, :t] = cmd_pos
        real_dof_torques[i, :t] = real_torque

    np.savez(
        args.out,
        real_dof_positions=real_dof_positions,
        real_dof_velocities=real_dof_velocities,
        real_dof_positions_cmd=real_dof_positions_cmd,
        real_dof_torques=real_dof_torques,
        motion_lengths=motion_lengths,
        joint_sequence=np.array(joint_sequence),
    )
    print(f"\nWrote {args.out} — {num_motions} motion(s), joints: {joint_sequence}")


if __name__ == "__main__":
    main()