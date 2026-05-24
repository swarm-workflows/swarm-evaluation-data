import csv, os, json, glob
from collections import Counter

results = []
base = '/root/SwarmAgents/runs/hier110-resilience'
TOTAL_JOBS = 2188

for scenario in ['baseline', 'distributed-10', 'distributed-20', 'site-outage']:
    scenario_dir = os.path.join(base, scenario)
    if not os.path.isdir(scenario_dir):
        continue
    for run_dir in sorted(glob.glob(os.path.join(scenario_dir, 'run-*'))):
        run_name = f'{scenario}/{os.path.basename(run_dir)}'
        
        # Use all_jobs.csv - count unique job_ids that have completed_at > 0
        jobs_csv = os.path.join(run_dir, 'all_jobs.csv')
        if not os.path.exists(jobs_csv):
            continue
        
        # Track best completion per unique job_id
        job_data = {}  # job_id -> best row (prefer completed)
        
        with open(jobs_csv) as f:
            reader = csv.DictReader(f)
            for row in reader:
                jid = row.get('job_id', '')
                submitted = float(row.get('submitted_at', '0') or '0')
                completed_at = float(row.get('completed_at', '0') or '0')
                sched_lat = float(row.get('scheduling_latency', '0') or '0')
                
                if jid not in job_data or (completed_at > 0 and job_data[jid]['completed_at'] == 0):
                    job_data[jid] = {
                        'submitted_at': submitted,
                        'completed_at': completed_at,
                        'scheduling_latency': sched_lat,
                    }

        completed = 0
        latencies = []
        sched_latencies = []
        for jid, d in job_data.items():
            if d['completed_at'] > 0 and d['submitted_at'] > 0:
                completed += 1
                lat = d['completed_at'] - d['submitted_at']
                if lat > 0:
                    latencies.append(lat)
            if d['scheduling_latency'] > 0:
                sched_latencies.append(d['scheduling_latency'])

        total_unique = len(job_data)

        # pending L1 jobs (jobs that never completed)
        pending_csv = os.path.join(run_dir, 'pending_level1_jobs.csv')
        pending = 0
        if os.path.exists(pending_csv):
            with open(pending_csv) as f:
                pending = sum(1 for _ in csv.DictReader(f))

        failed = TOTAL_JOBS - completed - pending

        # kill_event.json
        kill_event = os.path.join(run_dir, 'kill_event.json')
        killed = 0
        if os.path.exists(kill_event):
            try:
                with open(kill_event) as f:
                    ke = json.load(f)
                    killed = ke.get('num_killed', 0)
            except Exception:
                pass

        srt = sorted(latencies)
        med_lat = srt[len(srt)//2] if srt else 0
        p95_lat = srt[int(len(srt)*0.95)] if srt else 0
        max_lat = max(srt) if srt else 0

        ssrt = sorted(sched_latencies)
        med_sched = ssrt[len(ssrt)//2] if ssrt else 0
        p95_sched = ssrt[int(len(ssrt)*0.95)] if ssrt else 0
        
        completion_pct = 100 * completed / TOTAL_JOBS
        
        results.append({
            'run': run_name,
            'unique_jobs': total_unique,
            'completed': completed,
            'completion_pct': round(completion_pct, 1),
            'failed': max(0, failed),
            'pending': pending,
            'agents_killed': killed,
            'med_latency': round(med_lat, 1),
            'p95_latency': round(p95_lat, 1),
            'max_latency': round(max_lat, 1),
            'med_sched': round(med_sched, 1),
            'p95_sched': round(p95_sched, 1),
        })

# Print table
hdr = f'{"Run":<26} {"Done":>5} {"Pct":>6} {"Fail":>5} {"Pend":>5} {"Kill":>4}  {"MedE2E":>7} {"P95E2E":>8} {"MaxE2E":>8}  {"MedSch":>7} {"P95Sch":>8}'
print(hdr)
print('-' * len(hdr))
prev_scenario = None
for r in results:
    sc = r["run"].split("/")[0]
    if prev_scenario and sc != prev_scenario:
        print()
    prev_scenario = sc
    print(f'{r["run"]:<26} {r["completed"]:>5} {r["completion_pct"]:>5.1f}% {r["failed"]:>5} {r["pending"]:>5} {r["agents_killed"]:>4}  {r["med_latency"]:>6.1f}s {r["p95_latency"]:>7.1f}s {r["max_latency"]:>7.1f}s  {r["med_sched"]:>6.1f}s {r["p95_sched"]:>7.1f}s')

# Scenario averages
print()
print('=== SCENARIO AVERAGES (mean +/- std) ===')
import statistics
for scenario in ['baseline', 'distributed-10', 'distributed-20', 'site-outage']:
    runs = [r for r in results if r['run'].startswith(scenario)]
    if not runs:
        continue
    n = len(runs)
    pcts = [r['completion_pct'] for r in runs]
    fails = [r['failed'] for r in runs]
    pends = [r['pending'] for r in runs]
    meds = [r['med_latency'] for r in runs]
    p95s = [r['p95_latency'] for r in runs]
    
    avg_pct = statistics.mean(pcts)
    std_pct = statistics.stdev(pcts) if n > 1 else 0
    avg_fail = statistics.mean(fails)
    avg_pend = statistics.mean(pends)
    avg_med = statistics.mean(meds)
    avg_p95 = statistics.mean(p95s)
    
    print(f'{scenario:<20} completion={avg_pct:.1f}% +/- {std_pct:.1f}  failed={avg_fail:.0f}  pending={avg_pend:.0f}  med_e2e={avg_med:.1f}s  p95_e2e={avg_p95:.1f}s  (n={n})')
