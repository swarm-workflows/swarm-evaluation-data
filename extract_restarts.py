import os, glob, re, json, ast
from collections import defaultdict

base = '/Users/kthare10/swarm/agents/swarmplus-evaluation-data/runs/hier110-resilience'
results = []

for scenario in ['baseline', 'distributed-10', 'distributed-20', 'site-outage']:
    scenario_dir = os.path.join(base, scenario)
    if not os.path.isdir(scenario_dir):
        continue
    for run_dir in sorted(glob.glob(os.path.join(scenario_dir, 'run-*'))):
        run_name = f'{scenario}/{os.path.basename(run_dir)}'
        
        # Parse "stopped with restarts: {...}" from all agent logs
        total_restarts = 0      # sum of all restart counts
        unique_restarted_jobs = set()
        agent_restart_counts = {}  # agent_id -> total restarts
        max_per_job = 0
        
        # Look in agent-N/ subdirs (each host has agent-*.log)
        for host_dir in glob.glob(os.path.join(run_dir, 'agent-*')):
            if not os.path.isdir(host_dir):
                continue
            for logfile in glob.glob(os.path.join(host_dir, 'agent-*.log')):
                agent_id = None
                m = re.search(r'agent-(\d+)\.log$', logfile)
                if m:
                    agent_id = int(m.group(1))
                
                with open(logfile, 'r', errors='replace') as f:
                    for line in f:
                        if 'stopped with restarts:' in line:
                            # Extract the dict
                            idx = line.index('stopped with restarts:') + len('stopped with restarts: ')
                            rest = line[idx:].strip().rstrip('!')
                            try:
                                restarts_dict = ast.literal_eval(rest)
                                agent_total = 0
                                for job_id, cnt in restarts_dict.items():
                                    cnt = int(cnt)
                                    if cnt > 0:
                                        unique_restarted_jobs.add(job_id)
                                        total_restarts += cnt
                                        agent_total += cnt
                                        if cnt > max_per_job:
                                            max_per_job = cnt
                                if agent_id is not None:
                                    agent_restart_counts[agent_id] = agent_total
                            except Exception:
                                pass
        
        # Count RESTART lines (alternative method)
        restart_lines = 0
        for host_dir in glob.glob(os.path.join(run_dir, 'agent-*')):
            if not os.path.isdir(host_dir):
                continue
            for logfile in glob.glob(os.path.join(host_dir, 'agent-*.log')):
                with open(logfile, 'r', errors='replace') as f:
                    for line in f:
                        if '- INFO - RESTART: Job:' in line:
                            restart_lines += 1

        # kill count
        kill_event = os.path.join(run_dir, 'kill_event.json')
        killed = 0
        if os.path.exists(kill_event):
            try:
                with open(kill_event) as f:
                    killed = json.load(f).get('num_killed', 0)
            except:
                pass

        results.append({
            'run': run_name,
            'killed': killed,
            'unique_restarted_jobs': len(unique_restarted_jobs),
            'total_restart_events': restart_lines,
            'total_restart_count': total_restarts,
            'max_restarts_per_job': max_per_job,
            'agents_with_restarts': len(agent_restart_counts),
        })

# Print
hdr = f'{"Run":<26} {"Kill":>4} {"ReselJobs":>9} {"Events":>7} {"TotCnt":>7} {"MaxPerJob":>9} {"AgentsW/":>8}'
print(hdr)
print('-' * len(hdr))
prev = None
for r in results:
    sc = r['run'].split('/')[0]
    if prev and sc != prev:
        print()
    prev = sc
    print(f'{r["run"]:<26} {r["killed"]:>4} {r["unique_restarted_jobs"]:>9} {r["total_restart_events"]:>7} {r["total_restart_count"]:>7} {r["max_restarts_per_job"]:>9} {r["agents_with_restarts"]:>8}')

# Averages
print()
print('=== SCENARIO AVERAGES ===')
for scenario in ['baseline', 'distributed-10', 'distributed-20', 'site-outage']:
    runs = [r for r in results if r['run'].startswith(scenario) and r['total_restart_count'] > 0]
    if not runs:
        runs_all = [r for r in results if r['run'].startswith(scenario)]
        if runs_all:
            print(f'{scenario:<20} No restart data available (n={len(runs_all)})')
        continue
    n = len(runs)
    avg_jobs = sum(r['unique_restarted_jobs'] for r in runs) / n
    avg_events = sum(r['total_restart_events'] for r in runs) / n
    avg_total = sum(r['total_restart_count'] for r in runs) / n
    avg_max = sum(r['max_restarts_per_job'] for r in runs) / n
    print(f'{scenario:<20} resel_jobs={avg_jobs:.0f}  events={avg_events:.0f}  total_cnt={avg_total:.0f}  max_per_job={avg_max:.0f}  (n={n})')
