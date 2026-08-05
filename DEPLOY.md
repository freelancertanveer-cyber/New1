# Deployment Guide

## Quick Setup on VPS

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Upload Directory

```bash
mkdir -p uploads
```

### 3. Start the Server

```bash
python3 app.py
```

You should see:
```
* Running on http://0.0.0.0:5000
```

### 4. Access the Web UI

Open your browser and go to:
```
http://your-vps-ip:5000
```

## Usage Steps

1. **Prepare CSV File**
   - Columns needed: `first_name`, `last_name`, `domain`, `email`
   - The `email` column is optional - leave blank if unknown
   - Save as `.csv` (comma-separated values)

2. **Upload**
   - Click "Click to upload or drag & drop" on the page
   - Select your CSV file
   - Optionally set "Max Records to Process" for testing (leave empty for all)
   - Click "Start Verification"

3. **Monitor Progress**
   - Watch the progress bar update in real-time
   - Stats show total rows and current row being processed
   - Status message updates every 1-2 seconds

4. **Download Results**
   - When complete, click "Download Results"
   - CSV file downloads with verification results

## Testing

### Test with Sample File

```bash
python3 verify.py --input sample_data.csv --output test_results.csv --max-records 2
```

### Test Web UI

1. Create a small test CSV (e.g., 5 rows)
2. Upload via web UI
3. Check results for validity

## Troubleshooting

### Port Already in Use

If you get "Address already in use":

```bash
# Find what's using port 5000
lsof -i :5000

# Kill the process (if it's old)
kill -9 <PID>

# Or use a different port in app.py:
# Change: app.run(host='0.0.0.0', port=5000, debug=False)
# To:     app.run(host='0.0.0.0', port=5001, debug=False)
```

### DNS/MX Record Lookup Fails

This is normal for some domains or if DNS is blocked. The tool will mark them as "unknown".

### SMTP Timeouts

If too many timeouts occur:
- Check your network/firewall allows port 25
- Increase `smtp_timeout` in `verify.py`
- Reduce `max_records` for testing

### Module Not Found

Make sure you ran:
```bash
pip install -r requirements.txt
```

## Production Considerations

For production deployment:

1. **Use a Process Manager** (systemd, supervisord, gunicorn)
2. **Set debug=False** (already done in app.py)
3. **Add Authentication** if needed
4. **Use HTTPS** with reverse proxy (nginx)
5. **Monitor Logs** in `verifier.log`
6. **Set Max Requests** to limit memory growth

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Performance Tuning

Adjust delays in `verify.py` CONFIG:
- Shorter delays = faster but more likely rate-limited
- Longer delays = slower but more reliable
- Default settings target ~100k/day on typical domains

For a single domain, you could safely do 5,000-10,000 checks/day.
For 100k/day across many domains, keep current delays.

## Notes

- The system handles 1 email verification request at a time
- Large files (1000+ rows) will take 5-30 minutes depending on configuration
- Progress is calculated based on row count, not time
- Results are stored in `uploads/results_*.csv` (timestamped)
- Web server runs on all interfaces (0.0.0.0) - accessible from anywhere on the network
