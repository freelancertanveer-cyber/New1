#!/usr/bin/env python3
"""
Email Verification Web UI
Access via: http://your-vps-ip:5000
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import csv
import threading
import time
from pathlib import Path

from verify import (
    generate_permutations,
    get_mx_records,
    detect_catchall,
    verify_email,
    CONFIG
)
import logging

app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

current_job = {
    'status': 'idle',
    'progress': 0,
    'total': 0,
    'current_row': 0,
    'message': 'Ready',
    'results_file': None,
    'error': None,
}


def process_verification_job(input_file, output_file, max_records=None):
    global current_job

    try:
        current_job['status'] = 'running'
        current_job['error'] = None

        results = []
        domain_cache = {}

        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)

            total_rows = sum(1 for _ in csv.DictReader(open(input_file)))
            current_job['total'] = total_rows

            for row_idx, row in enumerate(csv.DictReader(open(input_file)), 1):
                if max_records and row_idx > max_records:
                    break

                current_job['current_row'] = row_idx
                current_job['progress'] = int((row_idx / total_rows) * 100) if total_rows > 0 else 0
                current_job['message'] = f"Processing row {row_idx}/{total_rows}"

                first_name = row.get('first_name', '').strip()
                last_name = row.get('last_name', '').strip()
                domain = row.get('domain', '').strip()
                provided_email = row.get('email', '').strip()

                if not domain:
                    logger.warning(f"Row {row_idx}: No domain provided")
                    continue

                logger.info(f"Processing row {row_idx}: {first_name} {last_name} @ {domain}")

                if domain not in domain_cache:
                    mx_hosts = get_mx_records(domain)
                    is_catchall = detect_catchall(domain, mx_hosts) if mx_hosts else False
                    domain_cache[domain] = {'mx': mx_hosts, 'catchall': is_catchall}

                mx_hosts = domain_cache[domain]['mx']
                is_catchall = domain_cache[domain]['catchall']

                permutations = generate_permutations(first_name, last_name, domain)

                verified_email = None
                best_status = "unknown"
                best_confidence = "unverified"

                if provided_email and '@' in provided_email:
                    status, confidence = verify_email(provided_email, mx_hosts)
                    if status == "valid":
                        verified_email = provided_email
                        best_status = status
                        best_confidence = confidence
                    logger.info(f"  Provided email {provided_email}: {status}")

                if not verified_email and permutations and not is_catchall:
                    for perm in permutations:
                        status, confidence = verify_email(perm, mx_hosts)
                        if status == "valid":
                            verified_email = perm
                            best_status = status
                            best_confidence = confidence
                            logger.info(f"  Found valid email: {perm}")
                            break
                        time.sleep(CONFIG['delay_between_checks'])

                result = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'domain': domain,
                    'provided_email': provided_email,
                    'verified_email': verified_email or 'not_found',
                    'status': best_status,
                    'confidence': best_confidence,
                    'is_catchall': is_catchall,
                    'mx_count': len(mx_hosts),
                }
                results.append(result)

        if results:
            with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                fieldnames = ['first_name', 'last_name', 'domain', 'provided_email',
                             'verified_email', 'status', 'confidence', 'is_catchall', 'mx_count']
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)

            valid_count = sum(1 for r in results if r['status'] == 'valid')
            catchall_count = sum(1 for r in results if r['is_catchall'])

            current_job['status'] = 'completed'
            current_job['message'] = f"Completed! Valid: {valid_count}, Catch-all: {catchall_count}"
            current_job['results_file'] = output_file
            current_job['progress'] = 100

    except Exception as e:
        logger.error(f"Error: {e}")
        current_job['status'] = 'error'
        current_job['error'] = str(e)
        current_job['message'] = f"Error: {str(e)}"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload():
    global current_job

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Please upload a CSV file'}), 400

    filename = f"upload_{int(time.time())}.csv"
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)

    output_filename = f"results_{int(time.time())}.csv"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

    current_job = {
        'status': 'running',
        'progress': 0,
        'total': 0,
        'current_row': 0,
        'message': 'Starting verification...',
        'results_file': None,
        'error': None,
    }

    max_records = request.form.get('max_records', type=int)
    thread = threading.Thread(
        target=process_verification_job,
        args=(input_path, output_path, max_records)
    )
    thread.daemon = True
    thread.start()

    return jsonify({'status': 'started'})


@app.route('/api/status')
def status():
    return jsonify(current_job)


@app.route('/api/download')
def download():
    if not current_job['results_file'] or not os.path.exists(current_job['results_file']):
        return jsonify({'error': 'No results available'}), 400

    return send_file(
        current_job['results_file'],
        mimetype='text/csv',
        as_attachment=True,
        download_name='verification_results.csv'
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
