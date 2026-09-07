"""
Convert SAGE real-robot CSV output into GapONet's expected .npz motion format,
auto-discovering all motions under a root folder and splitting them into
train/test sets (like sklearn's train_test_split), in one run.

Usage:
    python csv_to_gaponet_npz.py \
        --motions-root sage/output/real/so101/custom \
        --train-out gaponet/.../so101_train.npz \
        --test-out gaponet/.../so101_test.npz \
        --test-size 0.2 \
        --seed 1337
"""
import argparse
import ast
import csv
import os
import random
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


def discover_motions(root):
    """Find every subdirectory of `root` that looks like a valid motion recording."""
    motion_dirs = []
    for name in sorted(os.listdir(root)):
        d = os.path.join(root, name)
        if os.path.isdir(d) and os.path.exists(os.path.join(d, "state_motor.csv")):
            motion_dirs.append(d)
    return motion_dirs


def build_npz(motion_dirs, out_path):
    """Load, pad, and write a set of motion dirs into one npz file."""
    motions = []
    joint_sequence = None
    for real_dir in motion_dirs:
        name = os.path.basename(real_dir)
        cmd_pos, real_pos, real_vel, real_torque, js = load_one_motion(real_dir)
        print(f"  [{name}] {len(real_pos)} timesteps")
        if joint_sequence is None:
            joint_sequence = js
        elif joint_sequence != js:
            raise ValueError(f"Joint order mismatch in {real_dir}: {js} != {joint_sequence}")
        motions.append((cmd_pos, real_pos, real_vel, real_torque))

    motion_lengths = np.array([m[1].shape[0] for m in motions], dtype=np.int64)
    max_len = int(motion_lengths.max())
    num_dofs = len(joint_sequence)
    num_motions = len(motions)
    print(f"  -> {num_motions} motion(s), lengths {motion_lengths.tolist()}, padding all to {max_len}")

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

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    np.savez(
        out_path,
        real_dof_positions=real_dof_positions,
        real_dof_velocities=real_dof_velocities,
        real_dof_positions_cmd=real_dof_positions_cmd,
        real_dof_torques=real_dof_torques,
        motion_lengths=motion_lengths,
        joint_sequence=np.array(joint_sequence),
    )
    print(f"  Wrote {out_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--motions-root", required=True,
                     help="dir whose subdirectories are each one motion (containing control.csv, state_motor.csv, joint_list.txt)")
    ap.add_argument("--train-out", required=True)
    ap.add_argument("--test-out", required=True)
    ap.add_argument("--test-size", type=float, default=0.2, help="fraction held out for test (default 0.2)")
    ap.add_argument("--seed", type=int, default=1337, help="shuffle seed, for reproducibility")
    args = ap.parse_args()

    motion_dirs = discover_motions(args.motions_root)
    if len(motion_dirs) < 2:
        raise ValueError(f"Found only {len(motion_dirs)} motion(s) under {args.motions_root} — need at least 2 to split.")

    print(f"Discovered {len(motion_dirs)} motions under {args.motions_root}:")
    for d in motion_dirs:
        print(f"  - {os.path.basename(d)}")

    rng = random.Random(args.seed)
    shuffled = motion_dirs.copy()
    rng.shuffle(shuffled)

    n_test = max(1, round(len(shuffled) * args.test_size))
    test_dirs = shuffled[:n_test]
    train_dirs = shuffled[n_test:]

    print(f"\nSplit (seed={args.seed}): {len(train_dirs)} train / {len(test_dirs)} test")
    print("Train:", [os.path.basename(d) for d in train_dirs])
    print("Test: ", [os.path.basename(d) for d in test_dirs])

    print(f"\nBuilding train npz ({len(train_dirs)} motions)...")
    build_npz(train_dirs, args.train_out)

    print(f"\nBuilding test npz ({len(test_dirs)} motions)...")
    build_npz(test_dirs, args.test_out)


if __name__ == "__main__":
    main()