import os
from datetime import datetime

total_valid = 0
success_count = 0
error_count = 0
total_latency = 0
server_latency = {}
server_count = {}

try:
    with open("data/server_logs.csv", "r") as file:
        line_number = 0
        for line in file:
            line_number += 1
            if line_number == 1:
                continue

            line = line.strip()
            parts = line.split(",")
            server = parts[1]

            try:
                latency = int(parts[2])
                status = int(parts[3])
            except ValueError:
                print("bad value on line", line_number, "skipped")
                continue

            total_valid += 1
            total_latency += latency

            if status == 200:
                success_count += 1
            if status >= 400:
                error_count += 1

            if server in server_latency:
                server_latency[server] += latency
                server_count[server] += 1
            else:
                server_latency[server] = latency
                server_count[server] = 1

except FileNotFoundError:
    print("file not found")
    exit()

average = total_latency / total_valid
LATENCY_THRESHOLD = average

with open("reports/summary_report.txt", "w") as report:
    report.write("cloud log analysis\n")
    report.write(f"num valid records: {total_valid}\n")
    report.write(f"num successful requests: {success_count}\n")
    report.write(f"num error requests: {error_count}\n")
    report.write(f"average latency: {round(average, 2)}\n")

with open("reports/summary_report.txt", "a") as report:
    report.write("latency per server\n")
    for server in server_latency:
        server_avg = server_latency[server] / server_count[server]
        report.write(f"{server}: {server_count[server]} requests, average latency {round(server_avg, 2)}\n")

    report.write("slow servers\n")
    for server in server_latency:
        server_avg = server_latency[server] / server_count[server]
        if server_avg > LATENCY_THRESHOLD:
            report.write(f"{server} {round(server_avg, 2)}\n")

now = datetime.now()

if os.path.exists("logs/audit.log"):
    if os.path.getsize("logs/audit.log") > 2048:
        os.rename("logs/audit.log", "logs/audit_archive_" + now.strftime("%Y%m%d_%H%M%S") + ".log")

with open("logs/audit.log", "a") as audit:
    audit.write(f"{now} processed {total_valid} logs, average {round(average, 2)}\n")
