from analytics import compute_funnel, compute_student_stats, segment_funnel
from sample_events import generate_sample_events


def main() -> None:
    events = generate_sample_events()
    print("Funnel:", compute_funnel(events))
    print("Raphael stats:", compute_student_stats(events, "Raphael"))
    print("Segment by device:", segment_funnel(events, "device"))


if __name__ == "__main__":
    main()
