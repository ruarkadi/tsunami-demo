from flask import Flask, request
import subprocess
import ipaddress
import json

app = Flask(__name__)

@app.route('/scan', methods=['POST'])
def run_scan():

    # Optional URL paramater raw_log, if true will send the raw scan log
    raw = request.args.get('raw_log', default=False, type=lambda v: v.lower() == 'true')

    # Map the targets list from the request json
    targets = request.json['targets']

    # Prepare the results dict
    results = {}

    # Execute the scan command for each target
    for target in targets:

        command = ['java', '-cp', 'tsunami.jar:plugins/*', 
                    "-Dtsunami-config.location=tsunami.yaml", 
                    'com.google.tsunami.main.cli.TsunamiCli', 
                    '--scan-results-local-output-format=JSON']

        # Append the target query
        command.append(get_query_string_by_type(target))

        # Append the log path to the command
        command.append(f"--scan-results-local-output-filename=logs/{target}.json")

        # Execute the command and capture output
        # TODO: Add parallelability to these commands and check why in some instances 
        #       the command takes a long time to exit after completion
        command_result = subprocess.run(command, capture_output=True)

        # Write the command log output to a file
        with open(f"logs/{target}_command_log.json", 'w') as f:
            f.write(command_result.stdout.decode())
            f.write(command_result.stderr.decode())

        # Prepare the result and append to results which will be returned
        with open(f"logs/{target}.json") as log_file:

            data = json.load(log_file)
          
            if raw:
                results[target] = data
            else:
                results[target] = {
                    "scan_status": data['scanStatus'],
                    "scan_duration": data['scanDuration'],
                    "scan_findings": [finding['vulnerability'] for finding in data['scanFindings']] if 'scanFindings' in data else "No vulnerabilities detected"
                }

    return results

# Will return the proper query string after checking the type of target IPv4/IPv6/hostname
def get_query_string_by_type(target):
    try:
        return f"--ip-v4-target={target}" if type(ipaddress.ip_address(target)) is ipaddress.IPv4Address else f"--ip-v6-target={target}"
    except ValueError:
        return f"--hostname-target={target}"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')