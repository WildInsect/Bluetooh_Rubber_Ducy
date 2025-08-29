import json
import os
import argparse
import re

# Example mapping dictionary
alphabet_positions = {
    'a': {"xPos": 377, "yPos": 693},
    'b': {"xPos": 1120, "yPos": 847},
    'c': {"xPos": 810, "yPos": 839},
    'd': {"xPos": 714, "yPos": 694},
    'e': {"xPos": 681, "yPos": 531},
    'f': {"xPos": 875, "yPos": 692},
    'g': {"xPos": 1068, "yPos": 683},
    'h': {"xPos": 1217, "yPos": 688},
    'i': {"xPos": 1548, "yPos": 533},
    'j': {"xPos": 1413, "yPos": 686},
    'k': {"xPos": 1570, "yPos": 690},
    'l': {"xPos": 1753, "yPos": 690},
    'm': {"xPos": 1436, "yPos": 846},
    'n': {"xPos": 1286, "yPos": 845},
    'o': {"xPos": 1731, "yPos": 541},
    'p': {"xPos": 1898, "yPos": 542},
    'q': {"xPos": 336, "yPos": 535},
    'r': {"xPos": 854, "yPos": 531},
    's': {"xPos": 535, "yPos": 679},
    't': {"xPos": 1016, "yPos": 529},
    'u': {"xPos": 1384, "yPos": 542},
    'v': {"xPos": 971, "yPos": 857},
    'w': {"xPos": 497, "yPos": 538},
    'x': {"xPos": 634, "yPos": 840},
    'y': {"xPos": 1203, "yPos": 545},
    'z': {"xPos": 472, "yPos": 846},

    ' ': {"xPos": 829, "yPos": 1008},
    'ESC': {"xPos": 124, "yPos": 224},
    'SPC': {"xPos": 829, "yPos": 1008},
    'ENT': {"xPos": 2111, "yPos": 1013},
    'SFT': {"xPos": 2249, "yPos": 854},
    'WIN': {"xPos": 258, "yPos": 987},
    'ALT': {"xPos": 439, "yPos": 1000},
    'TAB': {"xPos": 175, "yPos": 540},
    'CTL': {"xPos": 124, "yPos": 1000},
    'DEL': {"xPos": 2246, "yPos": 213},
    'BSPC': {"xPos": 2180, "yPos": 387},
    'UP': {"xPos": 1594, "yPos": 844},
    'DWN': {"xPos": 1612, "yPos": 994},
    'LFT': {"xPos": 1443, "yPos": 1007},
    'RGT': {"xPos": 1782, "yPos": 997},
    'DLY': {"xPos": 1784, "yPos": 80},
    
    'FN1':  {'xPos': 256,  'yPos': 224},
    'FN2':  {'xPos': 422,  'yPos': 226},
    'FN3':  {'xPos': 583,  'yPos': 234},
    'FN4':  {'xPos': 751,  'yPos': 230},
    'FN5':  {'xPos': 917,  'yPos': 235},
    'FN6':  {'xPos': 1080, 'yPos': 226},
    'FN7':  {'xPos': 1258, 'yPos': 224},
    'FN8':  {'xPos': 1407, 'yPos': 236},
    'FN9':  {'xPos': 1581, 'yPos': 235},
    'FN10': {'xPos': 1766, 'yPos': 234},
    'FN11': {'xPos': 1922, 'yPos': 231},
    'FN12': {'xPos': 2089, 'yPos': 233},

    '.': {"xPos": 1936, "yPos": 852},
    "'": {"xPos": 2087, "yPos": 688},
    '/': {"xPos": 2088, "yPos": 844},
    '\\': {"xPos": 2257, "yPos": 706},
    ',': {"xPos": 1776, "yPos": 857},
    ';': {"xPos": 1899, "yPos": 703},
    '-': {"xPos": 1826, "yPos": 388},
    '=': {"xPos": 1989, "yPos": 397},
    '[': {"xPos": 2082, "yPos": 544},
    ']': {"xPos": 2245, "yPos": 530},

    '0': {"xPos": 1660, "yPos": 380},
    '1': {"xPos": 236, "yPos": 380},
    '2': {"xPos": 407, "yPos": 377},
    '3': {"xPos": 545, "yPos": 389},
    '4': {"xPos": 711, "yPos": 381},
    '5': {"xPos": 852, "yPos": 382},
    '6': {"xPos": 1034, "yPos": 392},
    '7': {"xPos": 1197, "yPos": 370},
    '8': {"xPos": 1336, "yPos": 380},
    '9': {"xPos": 1494, "yPos": 374}    
}

SPECIAL_KEYS = {"ESC","BSPC","SPC", "ENT", "SFT", "WIN", "ALT", "TAB", "CTL", 
                "UP", "DWN", "LFT", "RGT", "DEL", "DLY",
                "FN1", "FN2", "FN3", "FN4", "FN5", "FN6", 
                "FN7", "FN8", "FN9", "FN10", "FN11", "FN12"}

# Mapping of shifted symbols → base key
SHIFTED_SYMBOLS = {
    '!': '1',
    '@': '2',
    '#': '3',
    '$': '4',
    '%': '5',
    '^': '6',
    '&': '7',
    '*': '8',
    '(': '9',
    ')': '0',
    '_': '-',   
    '+': '=',   
    '{': '[',   
    '}': ']',   
    '|': '\\\\',
    ':': ';',
    '"': "'",
    '<': ',',
    '>': '.',
    '?': '/'
}

def tokenize_input(payload: str):
    tokens = []
    parts = payload.split()
    for part in parts:
        # Check if it's a delay token like DLY[500]
        match = re.match(r"DLY\[(\d+)\]", part)
        if match:
            tokens.append(("DLY", int(match.group(1))))  # store as tuple
        elif part in SPECIAL_KEYS:
            tokens.append(part)
        else:
            for char in part:
                if char.isupper():  # Uppercase → Shift + lowercase
                    tokens.append("SFT")
                    tokens.append(char.lower())
                elif char in SHIFTED_SYMBOLS:  # Shifted symbol
                    tokens.append("SFT")
                    tokens.append(SHIFTED_SYMBOLS[char])
                else:
                    tokens.append(char)
    return tokens

def generate_config(user_tokens, delay=100):
    targets = []
    for token in user_tokens:
        if isinstance(token, tuple) and token[0] == "DLY":
            # special case: delay instruction with custom value
            pos = alphabet_positions.get("DLY", {"xPos": -1, "yPos": -1})
            targets.append({
                "comment": "DLY",
                "delayUnit": 0,
                "delayValue": token[1],   # custom delay
                "duration": 0,
                "type": 0, 
                "xPos": pos["xPos"],
                "xPos1": -1,
                "yPos": pos["yPos"],
                "yPos1": -1
            })
        elif token in alphabet_positions:
            pos = alphabet_positions[token]
            targets.append({
                "comment": token,
                "delayUnit": 0,
                "delayValue": delay,
                "duration": 0,
                "type": 0,
                "xPos": pos["xPos"],
                "xPos1": -1,
                "yPos": pos["yPos"],
                "yPos1": -1
            })
        else:
            print(f"⚠ Skipping '{token}' (not in mapping)")
    return targets



def main():
    parser = argparse.ArgumentParser(description="Generate JSON config from payload")
    parser.add_argument("-f", "--file", help="Payload file (one payload per line)")
    parser.add_argument("-o", "--output", default="configs.txt", help="Output JSON file name")
    args = parser.parse_args()

    all_targets = []

    if args.file:
        if not os.path.exists(args.file):
            print(f"❌ File not found: {args.file}")
            return
        with open(args.file, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        for payload in lines:
            tokens = tokenize_input(payload)
            all_targets.extend(generate_config(tokens))
    else:
        payload = input("Enter your payload string: ")
        tokens = tokenize_input(payload)
        all_targets.extend(generate_config(tokens))

    final_config = [{
        "targets": all_targets,
        "antiDetection": False,
        "id": 1,
        "name": "Config_1",
        "numberOfCycles": 1,
        "stopConditionChecked": 0,
        "timeValue": 300
    }]

    with open(args.output, "w") as f_out:
        json.dump(final_config, f_out, indent=2)
    print(f"✅ Saved config into {args.output}")

if __name__ == "__main__":
    main()
