#!/usr/bin/python3

import argparse


def main():
    args = parse_args()

    process(args)


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Extracts documented MSRs from a text file (created with `pdftotext in.pdf`) "
            + "of Intel® 64 and IA-32 Architectures Software Developer’s Manual "
            + "Combined Volumes: 1, 2A, 2B, 2C, 2D, 3A, 3B, 3C, 3D, and 4. "
            + "Output is a list of MSR addresses/indices, one for each line "
            + "(i.e. ranges are expanded)."
        )
    )
    parser.add_argument("filename", help="Input file name (pdftotext txt file)")
    parser.add_argument(
        "start",
        help="Line number (inclusive) where to begin extracting (start).",
        type=int,
    )
    parser.add_argument(
        "end", help="Line number (inclusive) where to end extracting (end).", type=int
    )
    args = parser.parse_args()
    return args


def process(args):
    msrs = set()

    with open(args.filename, "r") as f:
        for i, line in enumerate(f):
            line = line.strip()

            # remove lines not in the range
            if i < args.start or args.end < i:
                continue

            # remove lines not matching format in tables
            if not "Register Address:" in line:
                continue

            # remove table haders
            if "Hex, Decimal" in line:
                continue

            # before e.g. Register Address: 1500H−151FH, 5376−5407
            msr = line.split(" ")[2].replace(",", "").replace("_", "").replace("H", "")
            # after: 1500−151F

            # expand ranges
            delimiter = (
                "−"  # note: not a HYPHEN-MINUS (U+002D), but a MINUS SIGN (U+2212)
            )
            if delimiter in msr:
                start, end = msr.split(delimiter)
                start = int(start, 16)
                end = int(end, 16)
                for i in range(start, end + 1):
                    msrs.add(i)
            elif "+n" in msr:
                # special case e.g. C90+n => just print it out of order
                prefix = int(msr.split("+")[0], 16)
                print(f"0x{prefix:08X} ", msr)
            else:
                msrs.add(int(msr, 16))

    msrs = sorted(list(msrs))
    for msr in msrs:
        print(f"0x{msr:08X}")


if __name__ == "__main__":
    main()
