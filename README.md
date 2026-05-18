# umv_systems_design_data_s1

*DISCLAIMER: This data is released as part of a paper submission only. We do not guarantee maintenance.*

Experimental time series data for Supplementary Data S1 in "System Design of the Ultra Mobility Vehicle".

The provided dataset contains the specific measurements corresponding to the dynamic maneuvers discussed in the main text:

1. Clearance positions for the lateral hopping experiment (Fig. 3);
2. Clearance height, and electrical power demand for the table jump (Fig. 4A);
3. Clearance height for the table jump repeatability experiment (Fig.4B); and
4. Whole-body inertia Iyy and angular velocity during the front flip (Fig. 5).

CoM positions and angular momentum trajectories were also provided for the aforementioned experiments.

All data are provided in MKS units.

## Nomenclature
- `timestamps`: Time corresponding to all data except those associated with motors

- `pos_com_hist`: CoM positions (x, y, z)
- `pos_clear_hist`: Clearance positions (x, y, z)
- `angmom_wb_hist`: Whole-body angular momentum (x, y, z)
- `h_com_hist`: CoM height (z)
- `h_clear_hist`: Clearance height (z)
- `I_hist`: Whole-body inertia (Ixx, Iyy, Izz)
- `angvel_base_hist`: Angular velocity of the Bike (x, y, z)
- `motor_timestamps`: Time corresponding to motor data
- `motor_current`: Total motor current
- `motor_voltage`: Bus voltage
- `motor_power`: Total power draw
