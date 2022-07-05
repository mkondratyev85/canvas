import os
import json

import ezdxf
from ezdxf.math import Vec2


JSON_DIR = os.path.join(os.path.dirname(__file__), "patterns")


def serialize_pattern_definition(pattern):
    new_pattern = []
    for line in pattern:
        new_line = []
        for e in line:
            if isinstance(e, Vec2):
                new_line.append((e.x, e.y))
            else:
                new_line.append(e)
        new_pattern.append(new_line)
    return new_pattern


def dump_existing_patterns(json_dir):
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)

    from placer.canvas.dxf_hatch_patterns import PATTERNS

    print(PATTERNS)

    for name in PATTERNS:
        print(name)
        to_dump = PATTERNS[name]
        to_dump["name"] = name
        json_file = os.path.join(json_dir, f"{name}.txt")

        with open(json_file, "w") as f:
            json.dump(to_dump, f, indent=4)


def export_hatches_from_file(json_dir, dxf_file):
    doc = ezdxf.readfile(dxf_file)
    msp = doc.modelspace()

    if not os.path.exists(json_dir):
        os.makedirs(json_dir)

    keys = ["pattern_angle", "pattern_scale"]
    keys_for_json = ["angle", "scale"]
    for e in msp:
        if e.dxftype() == "HATCH":
            to_dump = {}
            attribs = e.dxfattribs()

            to_dump["name"] = attribs["pattern_name"]
            for key, key_for_json in zip(keys, keys_for_json):
                if key in attribs:
                    to_dump[key_for_json] = attribs[key]

            if not e.pattern:
                continue
            to_dump["definition"] = serialize_pattern_definition(e.pattern.as_list())
            json_file = os.path.join(json_dir, f"{attribs['pattern_name']}.txt")

            print(f'Found pattern for {attribs["pattern_name"]}. Write to {json_file}')

            with open(json_file, "w") as f:
                json.dump(to_dump, f, indent=4)


def load_patterns_from_dir(path):
    patterns = {}

    for filename in os.listdir(path):
        if filename.endswith(".txt"):
            filename = os.path.join(path, filename)

            with open(filename, "r") as f:
                pat = json.load(f)
            try:
                name = pat.pop("name")
                patterns[name] = pat
            except KeyError:
                pass
    return patterns


if __name__ == "__main__":
    # filename = 'placer/canvas/patterns/PATTERN_ENGINEER_GEOLOGY.dxf'
    #
    # export_hatches_from_file(JSON_DIR, filename)
    # load_patterns_from_dir(JSON_DIR)
    dump_existing_patterns(JSON_DIR)
