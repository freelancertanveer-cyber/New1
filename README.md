# Email Verification System

A web-based email verification tool that finds valid email addresses by generating permutations and verifying them via SMTP.

## Features

- **Email Permutation Generation**: Creates common business email patterns from first name, last name, and domain
- **Catch-all Detection**: Identifies domains that accept any email address
- **SMTP Verification**: Validates emails by connecting to mail servers
- **Web Dashboard**: Real-time progress tracking and results download
- **Rate Limiting**: Respects server limits with configurable delays

## Setup

### Requirements

- Python 3.7+
- pip packages: `flask`, `dnspython`

### Installation

1. Install dependencies:
```bash
pip install flask dnspython
```

2. Run the web server:
```bash
python3 app.py
```

The server will start at `http://0.0.0.0:5000` (accessible at your VPS IP)

## Usage

### Via Web Dashboard

1. Open browser: `http://your-vps-ip:5000`
2. Upload a CSV file with columns: `first_name`, `last_name`, `domain`, `email`
3. Optionally set max records to process
4. Click "Start Verification"
5. Monitor real-time progress
6. Download results CSV when complete

### Via Command Line

```bash
python3 verify.py --input data.csv --output results.csv --max-records 100
```

## CSV Format

**Input columns:**
- `first_name`: Contact's first name
- `last_name`: Contact's last name
- `domain`: Company domain (e.g., acmecorp.com)
- `email`: (Optional) Known email address to verify first

**Output columns:**
- `first_name`, `last_name`, `domain`, `provided_email`: Input data
- `verified_email`: Valid email found (or 'not_found')
- `status`: 'valid', 'invalid', or 'unknown'
- `confidence`: 'accepted', 'rejected', 'no_mx', or 'unverified'
- `is_catchall`: Whether domain accepts any address
- `mx_count`: Number of mail servers for domain

## Email Patterns Tested

1. `first@domain`
2. `last@domain`
3. `first.last@domain`
4. `firstlast@domain`
5. `f.last@domain`
6. `firstl@domain`
7. `flast@domain`
8. `first_last@domain`
9. `first-last@domain`
10. `last.first@domain`
11. `lastfirst@domain`
12. `l.last@domain`
13. `first_initial + last@domain`
14. `f + last@domain`

## Configuration

Edit `verify.py` to adjust settings:

- `smtp_timeout`: 10s (seconds to wait for SMTP response)
- `delay_between_domains`: 0.5s (pause between domain checks)
- `delay_between_checks`: 0.2s (pause between email checks)
- `max_retries`: 2 (retry attempts for SMTP verification)
- `backoff_multiplier`: 2 (exponential backoff factor)

## Rate Limiting

The system includes built-in rate limiting:
- 0.2s delay between email verification checks
- 0.5s delay between domain checks
- Exponential backoff on failures
- Configurable to stay well below 100k/day at typical domains

## Logs

- Web UI: Outputs to console
- CLI: Logs to `verifier.log` and console

## License

Legitimate business use only. This tool is designed for verifying contacts at your own organization or with explicit permission.
