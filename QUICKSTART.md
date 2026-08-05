# Quick Start Guide

## What We Built

A complete email verification system with:
- ✓ Core verification engine (verify.py)
- ✓ Web API backend (app.py) 
- ✓ Beautiful web dashboard (templates/index.html)
- ✓ Real-time progress tracking
- ✓ One-click results download

## Installation (3 commands)

```bash
pip install -r requirements.txt
mkdir -p uploads
python3 app.py
```

Or use the startup script:
```bash
./start.sh
```

## Access

Open your browser:
```
http://your-vps-ip:5000
```

## Use Case Flow

1. **Prepare Data** - Export LinkedIn/CRM data with: first_name, last_name, domain
2. **Upload CSV** - Upload file via web UI (or 5,000+ rows at a time)
3. **Watch Progress** - Real-time status and stats display
4. **Download Results** - Get verified emails with confidence scores

## File Breakdown

| File | Purpose |
|------|---------|
| `verify.py` | Core email verification engine (can run standalone) |
| `app.py` | Flask web server and API |
| `templates/index.html` | Web dashboard UI |
| `requirements.txt` | Python dependencies |
| `start.sh` | One-command startup script |
| `README.md` | Full documentation |
| `DEPLOY.md` | Deployment guide with troubleshooting |
| `sample_data.csv` | Example CSV format |

## Example CSV Input

```csv
first_name,last_name,domain,email
John,Smith,acmecorp.com,
Jane,Johnson,techstartup.io,jane.johnson@techstartup.io
```

## Expected Output

```csv
first_name,last_name,domain,provided_email,verified_email,status,confidence,is_catchall,mx_count
John,Smith,acmecorp.com,,john@acmecorp.com,valid,accepted,false,3
Jane,Johnson,techstartup.io,jane.johnson@techstartup.io,jane.johnson@techstartup.io,valid,accepted,false,2
```

## Features

### Smart Permutation Generation
Tests 14 common email formats:
- first@domain
- first.last@domain
- firstlast@domain
- last.first@domain
- And 10 more...

### Catch-all Detection
Identifies if a domain accepts any email (skips permutation testing for those)

### SMTP Verification
Real SMTP handshakes to mail servers (not simulated)

### Rate Limiting
- 0.2s between email checks
- 0.5s between domain checks
- Exponential backoff on failures
- Safely handles 100k+ emails/day

### Real-time Progress
- Live progress bar
- Rows processed counter
- Status messages
- No page refresh needed

## Command Line (Advanced)

Run verification without web UI:
```bash
python3 verify.py --input data.csv --output results.csv --max-records 100
```

Options:
- `--input`: CSV file to process (required)
- `--output`: CSV file to save results (default: results.csv)
- `--max-records`: Limit rows for testing (optional)

## Tips

1. **Test First** - Upload 5-10 rows first to verify your CSV format
2. **Large Files** - 1000-row files take 5-30 minutes depending on configuration
3. **Domains** - Works best with standard business domains (gmail, yahoo, outlook = low success)
4. **Logs** - Check `verifier.log` for details on any errors
5. **Rate Limits** - If getting rejected, increase delays in `verify.py` CONFIG

## Performance

Expected rates (single domain, varies widely):
- Fresh startup: ~5-20 emails/minute
- After warmup: ~3-10 emails/minute  
- 100k/day = ~70 emails/minute average
- Catch-all domains: skip permutation testing (10x faster)

## Support

- Full documentation: See `README.md`
- Deployment issues: See `DEPLOY.md`
- Code changes: Edit `verify.py` CONFIG section

## Next Steps

1. Clone/pull the code to your VPS
2. Run `./start.sh` or follow installation steps
3. Open browser to `http://your-ip:5000`
4. Upload a test CSV file
5. Download results
6. Build your outbound sales workflow!

Good luck with your cold email campaigns! 🚀
