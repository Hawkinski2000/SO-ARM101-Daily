"""
Convert SAGE real-robot CSV output into GapONet's expected .npz motion format.

Usage:
    python csv_to_gaponet_npz.py \
        --real-dir sage/output/real/so101/custom/pick_place \
        --out so101_train.npz

Produces one npz containing a SINGLE motion clip (index 0), matching the
motion_index=0 patch applied to motion_motor_loader.py.
"""
import argparse
import ast
import csv
import numpy as np


def load_control(path):
    """control.csv: type,timestamp,positions -> (T, 6) array of commanded positions"""
    positions = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["type"] != "CONTROL":
                continue
            positions.append(ast.literal_eval(row["positions"]))
    return np.array(positions, dtype=np.float32)


def load_state_motor(path):
    """state_motor.csv: type,timestamp,positions,velocities,torques
    -> three (T, 6) arrays: positions, velocities, torques"""
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--real-dir", required=True, help="dir containing control.csv, state_motor.csv, joint_list.txt")
    ap.add_argument("--out", required=True, help="output .npz path")
    args = ap.parse_args()

    control_path = f"{args.real_dir}/control.csv"
    state_path = f"{args.real_dir}/state_motor.csv"
    joints_path = f"{args.real_dir}/joint_list.txt"

    cmd_pos = load_control(control_path)
    real_pos, real_vel, real_torque = load_state_motor(state_path)
    joint_sequence = load_joint_list(joints_path)

    print(f"control.csv rows:     {cmd_pos.shape}")
    print(f"state_motor.csv rows: {real_pos.shape}")

    # Sanity check: these must line up 1:1 since both are on the same real-robot clock
    n = min(len(cmd_pos), len(real_pos))
    if len(cmd_pos) != len(real_pos):
        print(f"WARNING: row count mismatch (control={len(cmd_pos)}, state_motor={len(real_pos)}). "
              f"Truncating both to {n} rows. Investigate before trusting this data.")
    cmd_pos = cmd_pos[:n]
    real_pos = real_pos[:n]
    real_vel = real_vel[:n]
    real_torque = real_torque[:n]

    # GapONet expects an array of motion clips. AMASS's original data uses dtype=object
    # because motions have varying lengths (ragged arrays). We only have ONE fixed-length
    # motion, so we use a plain rectangular array with a leading dim of 1 instead —
    # this avoids Python pickling entirely (no numpy-version-sensitive object arrays).
    real_dof_positions = np.stack([real_pos])          # shape (1, T, 6), plain float32
    real_dof_velocities = np.stack([real_vel])
    real_dof_positions_cmd = np.stack([cmd_pos])
    real_dof_torques = np.stack([real_torque])

    np.savez(
        args.out,
        real_dof_positions=real_dof_positions,
        real_dof_velocities=real_dof_velocities,
        real_dof_positions_cmd=real_dof_positions_cmd,
        real_dof_torques=real_dof_torques,
        joint_sequence=np.array(joint_sequence),
    )
    print(f"Wrote {args.out} — 1 motion clip, {n} timesteps, {len(joint_sequence)} joints: {joint_sequence}")


if __name__ == "__main__":
    main()
