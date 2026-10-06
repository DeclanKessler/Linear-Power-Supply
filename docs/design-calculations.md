# First-Order Power Supply Calculations

This analysis aid was added during portfolio development to support future design work. It provides estimates from explicit assumptions; it does not document completed hardware tests or establish the project's output ratings.

## Run the calculator

Requires Python 3.10 or newer, with no third-party dependencies. From the repository root:

```powershell
python tools/power_supply_estimator.py --secondary-rms 12 --output 9 --current 0.1
```

**The 12 V RMS input, 9 V output, and 0.1 A load are an illustrative example, not the project's specifications.** Replace them with your design assumptions.

The defaults use the draft's 2,200 µF reservoir capacitor and 60 Hz input. The 0.7 V diode drop, 1.5 V regulator dropout, 25 °C ambient temperature, and 10 °C/W total thermal resistance are illustrative assumptions that need to be replaced with appropriate values for the selected parts and operating conditions.

For machine-readable output:

```powershell
python tools/power_supply_estimator.py --secondary-rms 12 --output 9 --current 0.1 --json
```

## Equations

For a full-wave bridge and capacitor-input reservoir:

| Quantity | First-order equation |
| --- | --- |
| Rectified peak voltage | `V_peak = sqrt(2) × V_secondary_RMS − 2 × V_diode` |
| Ripple frequency | `f_ripple = 2 × f_line` |
| Peak-to-peak ripple | `ΔV = I_load / (f_ripple × C)`; capacitance is in farads |
| Minimum reservoir voltage | `V_min ≈ V_peak − ΔV` |
| Average reservoir voltage | `V_avg ≈ V_peak − ΔV / 2` |
| Dropout margin | `margin = V_min − V_output − V_dropout` |
| Average regulator dissipation | `P ≈ (V_avg − V_output) × I_load`, assuming regulation |
| Estimated junction temperature | `T_j ≈ T_ambient + P × θ_total` |

`θ_total` must represent the complete junction-to-ambient thermal path. For a heatsink-mounted regulator, consider the junction-to-case, interface, and heatsink-to-ambient contributions.

## Interpreting the example

The illustrative command estimates approximately:

- **15.571 V** reservoir peak
- **0.379 V peak-to-peak** ripple at **120 Hz**
- **4.692 V** dropout margin
- **0.638 W** average regulator dissipation
- **31.381 °C** junction temperature under the assumed thermal conditions

A positive nominal margin does not establish performance over line variation, transformer regulation, capacitor tolerance, or temperature. A negative margin means the requested regulated output is unsupported by the estimate; the dissipation and temperature estimates then do not represent actual dropout operation.

## Model boundaries

The calculator assumes a sinusoidal transformer secondary, two conducting bridge diodes, approximately constant load current, and a simple reservoir discharge model. It excludes transformer sag, winding resistance, capacitor ESR, regulator quiescent current, diode charging-current effects, startup transients, and thermal dynamics.

Use the results to select cases for LTspice simulation and bench testing. Compare predicted ripple, minimum input voltage, dissipation, and temperature with appropriate measurements and datasheet limits.

## Verify the calculator

```powershell
python -m unittest discover -s tools -p "test_*.py" -v
```

The tests cover a numerical reference case, full-wave ripple/load scaling, insufficient dropout headroom, and invalid model inputs.
