import csv, os, re, argparse
from datetime import datetime, date, time, timedelta
from icalendar import Calendar, Event, Alarm
try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None  # fallback if py<3.9

# ---------- helpers ----------
def slug(s: str) -> str:
    return re.sub(r'[^A-Za-z0-9._-]+', '_', s).strip('_')

TIME_PATTERNS = ["%I:%M %p", "%I %p", "%H:%M", "%H%M"]  # e.g., 11:30 AM, 11 AM, 23:30, 2330

def parse_date(s: str) -> date:
    return datetime.strptime(s.strip(), "%Y-%m-%d").date()

def parse_time(s: str) -> time | None:
    s = s.strip()
    if not s:
        return None
    for pat in TIME_PATTERNS:
        try:
            return datetime.strptime(s, pat).time()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized time format: {s!r}")

def make_dt(d: date, t: time | None, tzname: str | None):
    if t is None:
        return d  # date-only (all-day)
    if tzname and ZoneInfo:
        return datetime.combine(d, t, tzinfo=ZoneInfo(tzname))
    return datetime.combine(d, t)  # naive if tz not available

# ---------- main ----------
parser = argparse.ArgumentParser(description="Generate .ics calendar files from a CSV file.")
parser.add_argument("csv_file", type=str, help="Path to the input CSV file")
parser.add_argument("--out", default="calendar_files", help="Output folder (default: calendar_files)")
parser.add_argument("--default-tz", default="America/Chicago", help="Fallback timezone if column missing")
parser.add_argument("--alarm-mins", type=int, default=15, help="Minutes before start for reminder (default: 15)")
args = parser.parse_args()

os.makedirs(args.out, exist_ok=True)

with open(args.csv_file, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        summary = row["Summary"].strip()
        start_date = parse_date(row["Start Date"])
        end_date = parse_date(row["End Date"])

        # Optional columns
        start_time = parse_time(row.get("Start Time", "").strip()) if "Start Time" in row else None
        end_time   = parse_time(row.get("End Time", "").strip())   if "End Time" in row else None
        tzname     = (row.get("Timezone") or args.default_tz).strip()
        description = row.get("Description", "").strip()

        # Build event
        cal = Calendar()
        event = Event()
        event.add("summary", summary)
        event.add("description", description)

        dtstart = make_dt(start_date, start_time, tzname)
        dtend   = make_dt(end_date,   end_time,   tzname)

        event.add("dtstart", dtstart)
        event.add("dtend", dtend)
        event.add("dtstamp", datetime.utcnow())

        # Alarm (relative)
        if start_time is not None and args.alarm_mins:
            alarm = Alarm()
            alarm.add("action", "DISPLAY")
            alarm.add("description", f"Reminder: {summary}")
            alarm.add("trigger", timedelta(minutes=-abs(args.alarm_mins)))
            event.add_component(alarm)

        cal.add_component(event)

        # Unique filename (summary + start date/time)
        stamp = start_date.strftime("%Y%m%d")
        if start_time:
            stamp += datetime.combine(date.min, start_time).strftime("_%H%M")
        filename = f"{slug(summary)}_{stamp}.ics"
        path = os.path.join(args.out, filename)
        with open(path, "wb") as out:
            out.write(cal.to_ical())
        print(f"Created {path}")

print(f"All calendar events created in '{args.out}'.")

