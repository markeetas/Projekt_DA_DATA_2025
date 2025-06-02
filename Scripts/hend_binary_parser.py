import os
import struct
import csv

# Set the root directory
root_dir = r"C:\Users\marke\DA_Projekt\Data_nezpracovana\Mars_Odyssey2001\GRS_HEND_AHD\Year12"
fmt_path = os.path.join(root_dir, "AVG_HEND_DATA_COLS.FMT")

# Function to parse the .FMT file
def parse_fmt(fmt_file):
    fields = []
    with open(fmt_file, "r") as f:
        current = {}
        for line in f:
            line = line.strip()
            if line.startswith("NAME"):
                current["name"] = line.split("=")[1].strip()
            elif line.startswith("BYTES"):
                current["bytes"] = int(line.split("=")[1].strip())
            elif line.startswith("DATA_TYPE"):
                current["type"] = line.split("=")[1].strip()
            elif line.startswith("END_OBJECT = COLUMN"):
                dtype = current["type"]
                if dtype == "REAL":
                    fmt = "f"
                else:
                    raise ValueError(f"Unknown data type: {dtype}")
                fields.append((current["name"], fmt))
                current = {}
    return fields


# Load the format structure
fields = parse_fmt(fmt_path)
struct_fmt = ">" + "".join(fmt for _, fmt in fields)
row_size = struct.calcsize(struct_fmt)

# Find all .DAT files in the folder
dat_files = [f for f in os.listdir(root_dir) if f.lower().endswith(".dat")]

# Process each .DAT file
for dat_file in dat_files:
    dat_path = os.path.join(root_dir, dat_file)
    csv_path = os.path.join(root_dir, dat_file.replace(".dat", ".csv"))

    with open(dat_path, "rb") as f:
        data = f.read()

    # Unpack binary records
    records = [struct.unpack(struct_fmt, data[i:i + row_size])
               for i in range(0, len(data), row_size)]

    # Save to csv
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([name for name, _ in fields])
        writer.writerows(records)

    print(f"Saved: {csv_path}")
