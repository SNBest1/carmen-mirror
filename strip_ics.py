"""Shrink a Canvas ICS feed so it survives a single WebFetch.

Drops the bulky free-text fields (a single ART 2555 description was enough to
push every later event past the fetch limit) and refuses to publish anything
that looks truncated.
"""

import sys

DROP = ("DESCRIPTION", "X-ALT-DESC", "ATTENDEE", "ORGANIZER")
MAX_LINE = 300

src, dst = sys.argv[1], sys.argv[2]

with open(src, encoding="utf-8", errors="replace") as fh:
    raw = fh.read()

if "END:VCALENDAR" not in raw:
    sys.exit("Feed is truncated, no END:VCALENDAR found. Refusing to publish.")

# Unfold RFC 5545 continuation lines before filtering, otherwise the tail of a
# dropped DESCRIPTION survives as orphaned continuation lines.
text = raw.replace("\r\n", "\n").replace("\n ", "").replace("\n\t", "")

out = []
for line in text.split("\n"):
    if not line.strip():
        continue
    prop = line.split(";")[0].split(":")[0].upper()
    if prop in DROP:
        continue
    out.append(line[:MAX_LINE])

events = sum(1 for line in out if line.startswith("BEGIN:VEVENT"))
if events == 0:
    sys.exit("No VEVENT blocks survived. Refusing to publish.")

body = "\n".join(out) + "\n"
with open(dst, "w", encoding="utf-8") as fh:
    fh.write(body)

print(f"Wrote {dst}: {events} events, {len(body)} bytes (was {len(raw)}).")
