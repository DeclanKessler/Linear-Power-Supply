"""First-order estimates for a bridge-rectified adjustable linear supply."""

import argparse
import json
import math


def estimate_supply(
    *,
    secondary_rms_v,
    output_v,
    load_a,
    capacitance_uf=2200.0,
    line_hz=60.0,
    diode_drop_v=0.7,
    dropout_v=1.5,
    ambient_c=25.0,
    thermal_resistance_c_per_w=10.0,
):
    """Calculate nominal estimates; inputs are assumptions, not measurements.

    Uses two conducting bridge diodes and full-wave ripple at twice the
    line frequency. Thermal resistance is the total junction-to-ambient path.
    Transformer sag, ESR, wiring losses, and regulator quiescent current are
    excluded. No hardware rating or operating limit is inferred.
    """
    inputs = {
        "secondary_rms_v": secondary_rms_v,
        "output_v": output_v,
        "load_a": load_a,
        "capacitance_uf": capacitance_uf,
        "line_hz": line_hz,
        "diode_drop_v": diode_drop_v,
        "dropout_v": dropout_v,
        "ambient_c": ambient_c,
        "thermal_resistance_c_per_w": thermal_resistance_c_per_w,
    }
    for name, value in inputs.items():
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
        if name == "ambient_c":
            if value < -273.15:
                raise ValueError("ambient_c must be above absolute zero")
        elif name in {"diode_drop_v", "dropout_v"}:
            if value < 0:
                raise ValueError(f"{name} must be nonnegative")
        elif value <= 0:
            raise ValueError(f"{name} must be positive")

    ripple_hz = 2.0 * line_hz
    peak_v = secondary_rms_v * math.sqrt(2.0) - 2.0 * diode_drop_v
    ripple_v = load_a / (ripple_hz * capacitance_uf * 1e-6)
    minimum_v = peak_v - ripple_v
    average_v = peak_v - ripple_v / 2.0
    if minimum_v <= 0:
        raise ValueError("Estimated reservoir voltage reaches zero; model is unsuitable")
    average_heat_w = max(0.0, average_v - output_v) * load_a
    margin_v = minimum_v - output_v - dropout_v
    return {
        "assumptions": inputs,
        "estimates": {
            "ripple_frequency_hz": ripple_hz,
            "reservoir_peak_v": peak_v,
            "reservoir_ripple_peak_to_peak_v": ripple_v,
            "reservoir_minimum_v": minimum_v,
            "reservoir_average_v": average_v,
            "dropout_margin_v": margin_v,
            "regulator_average_dissipation_w": average_heat_w,
            "junction_temperature_c": ambient_c
            + average_heat_w * thermal_resistance_c_per_w,
        },
        "regulation_supported_by_estimate": margin_v >= 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--secondary-rms", type=float, required=True, metavar="V")
    parser.add_argument("--output", type=float, required=True, metavar="V")
    parser.add_argument("--current", type=float, required=True, metavar="A")
    parser.add_argument("--capacitance-uf", type=float, default=2200.0)
    parser.add_argument("--line-hz", type=float, default=60.0)
    parser.add_argument("--diode-drop", type=float, default=0.7, metavar="V")
    parser.add_argument("--dropout", type=float, default=1.5, metavar="V")
    parser.add_argument("--ambient", type=float, default=25.0, metavar="C")
    parser.add_argument("--thermal-resistance", type=float, default=10.0, metavar="C/W")
    parser.add_argument("--json", action="store_true", help="Print machine-readable estimates")
    args = parser.parse_args()
    try:
        report = estimate_supply(
            secondary_rms_v=args.secondary_rms,
            output_v=args.output,
            load_a=args.current,
            capacitance_uf=args.capacitance_uf,
            line_hz=args.line_hz,
            diode_drop_v=args.diode_drop,
            dropout_v=args.dropout,
            ambient_c=args.ambient,
            thermal_resistance_c_per_w=args.thermal_resistance,
        )
    except ValueError as error:
        parser.error(str(error))
    if args.json:
        print(json.dumps(report, indent=2, allow_nan=False))
        return
    print("FIRST-ORDER ESTIMATES — not measured hardware results")
    print("\nAssumptions (volts, amps, microfarads, hertz, Celsius, C/W):")
    for name, value in report["assumptions"].items():
        print(f"  {name}: {value:g}")
    print("\nEstimates:")
    for name, value in report["estimates"].items():
        print(f"  {name}: {value:.3f}")
    if not report["regulation_supported_by_estimate"]:
        print("\nNegative dropout margin: requested output is not supported by this estimate.")
        print("Dissipation and temperature assume regulation and are not valid for that condition.")
    print("\nCheck component datasheets, transformer sag, and measured performance.")


if __name__ == "__main__":
    main()
