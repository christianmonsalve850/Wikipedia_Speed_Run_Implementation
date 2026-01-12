import json
from main import run

def fetch_tests():
    """
    Load test cases from tests.json.

    @return list: Parsed list of tests or None on error.
    """
    try:
        with open('tests.json', 'r') as file:
            data = json.load(file)
            return data
    except Exception:
        print("Error loading data")

def write_test_report(test: json, time, n_links, links):
    """
    Format a single test run report.

    @param test: Test case metadata.
    @param time: Elapsed time for the run.
    @param n_links: Number of links in found path.
    @param links: Path as a list of titles.
    @return dict: Structured report for serialization.
    """
    report = {
        "test_number": test['test_number'],
        "start": test['start'],
        "end": test['end'],
        "time": time,
        "n_links": n_links,
        "links": links
    }

    return report

def run_tests():
    """
    Execute tests from tests.json and write results to test_results.json.

    @return None
    """
    tests = fetch_tests()
    test_results = []

    for test in tests:
        start = test['start']
        end = test['end']
        try:
            elapsed_time, n_links, links = run(start, end)
            report = write_test_report(test, elapsed_time, n_links, links)
        except Exception:
            report = {
                "test_number": test['test_number'],
                "start": start,
                "end": end,
                "time": -1,
                "n_links": -1,
                "links": -1
            }

        test_results.append(report)

    with open("test_results.json", "w", encoding="utf-8") as json_file:
        json.dump(test_results, json_file, indent=4, ensure_ascii=False)

# run_tests()  # Disabled by default.