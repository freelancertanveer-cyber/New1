#!/usr/bin/env python3
"""
Email Verification Waterfall System
Generates email permutations, detects catch-alls, and verifies addresses.
Input: CSV with first_name, last_name, domain, email
Output: CSV with verification results
"""

import csv
import sys
import time
import socket
import dns.resolver
import logging
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('verifier.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
# Set list_verification_mode=True when verifying existing email lists (no permutation testing)
CONFIG = {
    'smtp_timeout': 5,
    'dns_timeout': 3,
    'delay_between_domains': 0.05,
    'delay_between_checks': 0.01,
    'max_retries': 1,
    'backoff_multiplier': 1.5,
    'list_verification_mode': True,  # Optimized for verifying existing lists (99k/day)
}

# Email permutation patterns
PERMUTATION_PATTERNS = [
    '{first}@{domain}',
    '{last}@{domain}',
    '{first}.{last}@{domain}',
    '{first}{last}@{domain}',
    '{f}.{last}@{domain}',
    '{first}{l}@{domain}',
    '{f}{last}@{domain}',
    '{first}_{last}@{domain}',
    '{first}-{last}@{domain}',
    '{last}.{first}@{domain}',
    '{last}{first}@{domain}',
    '{l}.{last}@{domain}',
    '{first_initial}{last}@{domain}',
    '{f_initial}{last}@{domain}',
]


def generate_permutations(first_name: str, last_name: str, domain: str) -> List[str]:
    """Generate email permutations from name + domain."""
    if not first_name or not last_name or not domain:
        return []

    first = first_name.lower().strip()
    last = last_name.lower().strip()
    f = first[0] if first else ''
    l = last[0] if last else ''

    permutations = []
    for pattern in PERMUTATION_PATTERNS:
        try:
            email = pattern.format(
                first=first,
                last=last,
                f=f,
                l=l,
                first_initial=f,
                f_initial=f,
                domain=domain
            )
            if email not in permutations:
                permutations.append(email)
        except KeyError:
            continue

    return permutations


def get_mx_records(domain: str) -> List[str]:
    """Get MX records for domain."""
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        return [str(mx.exchange).rstrip('.') for mx in mx_records]
    except Exception as e:
        logger.debug(f"No MX records found for {domain}: {e}")
        return []


def check_smtp_response(host: str, email: str, timeout: int = 10) -> Tuple[bool, str]:
    """
    Check if email is deliverable via SMTP handshake.
    Returns: (is_deliverable, status_message)
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        sock.connect((host, 25))

        banner = sock.recv(1024).decode()
        if not banner.startswith('220'):
            sock.close()
            return False, "No SMTP banner"

        sock.send(b'EHLO verifier.local\r\n')
        response = sock.recv(1024).decode()

        sock.send(b'MAIL FROM:<test@verifier.local>\r\n')
        response = sock.recv(1024).decode()

        cmd = f'RCPT TO:<{email}>\r\n'.encode()
        sock.send(cmd)
        response = sock.recv(1024).decode()

        sock.send(b'QUIT\r\n')
        sock.close()

        code = response.split()[0] if response else '500'

        if code.startswith('25'):
            return True, "Accepted"
        elif code.startswith('45'):
            return False, "Try again later"
        elif code.startswith('55'):
            return False, "Rejected"
        else:
            return False, f"Response {code}"

    except socket.timeout:
        return False, "Timeout"
    except ConnectionRefusedError:
        return False, "Connection refused"
    except Exception as e:
        return False, f"Error: {str(e)[:30]}"


def detect_catchall(domain: str, mx_hosts: List[str]) -> bool:
    """
    Detect if domain is a catch-all (accepts mail for any address).
    """
    if not mx_hosts:
        return False

    test_email = f"doesnotexist{int(time.time())}@{domain}"

    for mx_host in mx_hosts[:2]:
        accepted, _ = check_smtp_response(mx_host, test_email, CONFIG['smtp_timeout'])
        if accepted:
            logger.info(f"Domain {domain} appears to be catch-all")
            return True
        time.sleep(CONFIG['delay_between_domains'])

    return False


def verify_email(email: str, mx_hosts: List[str]) -> Tuple[str, str]:
    """
    Verify a single email address.
    Returns: (status, confidence)
    """
    if not mx_hosts:
        return "unknown", "no_mx"

    for attempt in range(CONFIG['max_retries']):
        for mx_host in mx_hosts:
            accepted, reason = check_smtp_response(mx_host, email, CONFIG['smtp_timeout'])

            if accepted:
                return "valid", "accepted"

            time.sleep(CONFIG['delay_between_checks'])

        if attempt < CONFIG['max_retries'] - 1:
            wait_time = CONFIG['delay_between_domains'] * (CONFIG['backoff_multiplier'] ** attempt)
            time.sleep(wait_time)

    return "invalid", "rejected"


def process_csv(input_file: str, output_file: str, max_records: int = None):
    """Process CSV file and verify emails."""

    if not Path(input_file).exists():
        logger.error(f"Input file not found: {input_file}")
        sys.exit(1)

    results = []
    domain_cache = {}
    processed_count = 0

    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)

            if not reader.fieldnames or 'domain' not in reader.fieldnames:
                logger.error("CSV must have 'domain' column")
                sys.exit(1)

            for row_idx, row in enumerate(reader, 1):
                if max_records and row_idx > max_records:
                    break

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

                if not verified_email and permutations and not is_catchall and not CONFIG['list_verification_mode']:
                    for perm in permutations:
                        status, confidence = verify_email(perm, mx_hosts)
                        if status == "valid":
                            verified_email = perm
                            best_status = status
                            best_confidence = confidence
                            logger.info(f"  Found valid email: {perm}")
                            break
                        logger.debug(f"  {perm}: {status}")
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
                processed_count += 1

        if results:
            with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                fieldnames = [
                    'first_name', 'last_name', 'domain', 'provided_email',
                    'verified_email', 'status', 'confidence', 'is_catchall', 'mx_count'
                ]
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)

            logger.info(f"\nVerification complete!")
            logger.info(f"Processed: {processed_count} records")
            logger.info(f"Results saved to: {output_file}")

            valid_count = sum(1 for r in results if r['status'] == 'valid')
            catchall_count = sum(1 for r in results if r['is_catchall'])
            logger.info(f"Valid emails found: {valid_count}")
            logger.info(f"Catch-all domains: {catchall_count}")

    except Exception as e:
        logger.error(f"Error processing CSV: {e}")
        sys.exit(1)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Email Verification Waterfall System'
    )
    parser.add_argument('--input', required=True, help='Input CSV file (first_name, last_name, domain, email)')
    parser.add_argument('--output', default='results.csv', help='Output CSV file (default: results.csv)')
    parser.add_argument('--max-records', type=int, help='Max records to process (for testing)')

    args = parser.parse_args()

    process_csv(args.input, args.output, args.max_records)
