import yaml
import copy
import itertools
import sys
from pathlib import Path

def extend_predictions(config_file, output_file, pt_intervals, y_intervals):
    # Load YAML
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    new_predictions = []

    for pred in config.get("predictions", []):
        # Find ymin, ymax, ptmin, ptmax fields
        fields = {field["selector"]: field for field in pred["fields"] if "selector" in field}

        for (ptmin, ptmax), (ymin, ymax) in itertools.product(pt_intervals, y_intervals):
            new_pred = copy.deepcopy(pred)

            # Update name to reflect new ranges
            new_pred["name"] = f"{pred['name']}_pt{ptmin}-{ptmax}_y{ymin}-{ymax}"
            new_pred["description"] = f"{pred['description']} (pt=[{ptmin},{ptmax}], y=[{ymin},{ymax}])"

            # Update fields
            for field in new_pred["fields"]:
                if field["selector"] == "ptmin":
                    field["value"] = str(ptmin)
                elif field["selector"] == "ptmax":
                    field["value"] = str(ptmax)
                elif field["selector"] == "ymin":
                    field["value"] = str(ymin)
                elif field["selector"] == "ymax":
                    field["value"] = str(ymax)

            new_predictions.append(new_pred)

    # Extend config
    config["predictions"].extend(new_predictions)

    # Save new YAML
    with open(output_file, "w") as f:
        yaml.dump(config, f, sort_keys=False)

    print(f"✅ Extended config saved to {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extend_predictions.py input_config.yaml output_config.yaml")
        sys.exit(1)

    input_config = Path(sys.argv[1])
    output_config = Path(sys.argv[2])

    # Example intervals (can be adapted)
    pt_intervals = [(0, 0.5), (0.5, 1), (1, 1.5), (1.5, 2), (2, 2.5), (2.5, 3),
                    (3, 3.5), (3.5, 4), (4, 4.5), (4.5, 5), (5, 5.5), (5.5, 6),
                    (6, 6.5), (6.5, 7), (7, 7.5), (7.5, 8), (8, 8.5), (8.5, 9),
                    (9, 9.5), (9.5, 10), (10, 10.5), (10.5, 11.5), (11.5, 12.5),
                    (12.5, 14), (14, 16.5), (16.5, 23.5), (23.5, 40)]
    y_intervals = [(2.0, 2.5), (2.5, 3.0), (3.0, 3.5), (3.5, 4.0), (4.0, 4.5)]
    y_intervals = [(4.0, 4.5)]

    extend_predictions(input_config, output_config, pt_intervals, y_intervals)
