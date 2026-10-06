# Dial-Operated Linear Power Supply

An in-progress electrical engineering project to design a dial-operated, adjustable linear DC power supply. This repository contains the initial LTspice design, simulation artifacts, and a component cost breakdown.

## Project status

**Design and simulation stage.** The current files document an early circuit draft and component selection. Hardware measurements, an assembled prototype, and verified output specifications have not yet been documented here.

## Design overview

The draft models the following signal path:

**AC source → coupled-inductor transformer model → diode bridge → reservoir capacitor → adjustable linear regulator → output load**

| Block | Current design files |
| --- | --- |
| AC input | 60 Hz sinusoidal source with a 169.7 V peak amplitude |
| Transformer | Coupled-inductor model; parts list specifies a Triad Magnetics FP16-3000 transformer |
| Rectifier | Four simulated diodes; parts list specifies a GBU602 bridge rectifier |
| Input filtering | 2,200 µF reservoir capacitor |
| Regulation | LT1085 symbol/model in the simulation; LD1085V in the parts list |
| Voltage adjustment | 750 Ω feedback resistor and a 5 kΩ resistance in the draft |
| Output | 10 µF capacitor and 100 Ω simulated load |

These values describe the current draft, rather than verified hardware performance.

## Repository guide

| File | Purpose |
| --- | --- |
| [Draft2.asc](Draft2.asc) | Editable LTspice schematic; start here to inspect the circuit |
| [Draft2.net](Draft2.net) | Generated SPICE netlist |
| [Draft2.log](Draft2.log) | Simulation log reporting successful operating-point convergence |
| [Draft2.op.raw](Draft2.op.raw) | Saved operating-point simulation data |
| [Parts list and cost](Parts%20list%20and%20cost) | Component selection, quantities, and estimated costs |

## Inspecting the simulation

1. Install LTspice. The checked-in log was generated with **LTspice 24.1.9 for Windows**.
2. Download the repository and open `Draft2.asc` in LTspice.
3. Check that the regulator model and diode library resolve on your installation. The generated netlist contains paths from the original machine, so regenerate it from the schematic rather than relying on those paths.
4. Review the circuit and run the configured transient analysis: `.tran 0 100ms 0 10us`.
5. Probe the rectifier output and regulated output to inspect startup and ripple. Transient waveform plots are not currently included in the repository.

## Component selection and cost

The checked-in parts list includes the transformer, bridge rectifier, adjustable regulator, capacitors, resistors, potentiometers, rotary switch, connectors, wiring, and input components.

**Listed component subtotal: $72.01.** This is the estimate recorded in the file; it does not establish the complete build cost or current supplier pricing.

## Design review and next steps

- Reconcile the **LT1085 simulation model** with the **LD1085V selected part** and document the relevant datasheet assumptions.
- Reconcile the draft's **5 kΩ adjustment resistance** with the **10 kΩ and 1 kΩ potentiometers** in the parts list, and document the intended dial/switch arrangement.
- Confirm the transformer model and its correspondence to the selected transformer's winding configuration.
- Define the intended output-voltage range and continuous output-current target.
- Evaluate dropout margin, output ripple, load regulation, and regulator power dissipation across the intended operating range.
- Add waveform plots, an annotated schematic, assembly photos, and measured results as the project progresses.

## Design calculation tool

The [Python power-supply estimator](tools/power_supply_estimator.py) calculates first-order reservoir ripple, regulator headroom, dissipation, and junction temperature from explicit assumptions. See the [equations, example, and model limitations](docs/design-calculations.md).

This tool was added to support ongoing design analysis. Its outputs are estimates, not measured results or verified hardware ratings.

```powershell
python tools/power_supply_estimator.py --secondary-rms 12 --output 9 --current 0.1
```

The command above is an illustrative calculation, not the project's specifications.

## Engineering focus

This project brings together **analog circuit modeling, AC-to-DC conversion, linear regulation, component selection, and cost documentation**. The files provide a starting point for tracing the design decisions and subsequent validation.
