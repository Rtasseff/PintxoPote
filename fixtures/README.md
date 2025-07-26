# Railway Deployment Instructions

This directory contains JSON fixtures for deploying to Railway. **No media files are stored here** - they remain in the untracked `data/` directory.

## Deployment Process:

### 1. Deploy Code to Railway
```bash
git add bars/management/commands/export_data.py fixtures/
git commit -m "feat: add Railway deployment fixtures"
git push origin main
```

### 2. Load Database Fixtures on Railway
```bash
railway run python manage.py loaddata fixtures/bars.json fixtures/photos.json fixtures/comments.json fixtures/users.json
```

### 3. Sync data/ Directory to Railway
The `data/` directory (database + media files) needs to be synced to `/app/data` on Railway:

```bash
# Option A: Use Railway CLI to copy files
railway connect
# Then use rsync or scp to copy data/ contents to /app/data

# Option B: Compress and upload
tar czf data-backup.tar.gz data/
# Upload via Railway dashboard and extract to /app/data
```

## Important Notes:
- The `data/` directory is NOT tracked by git (as intended)
- Django settings automatically detect Railway and use `/app/data` for storage
- Only JSON metadata is committed to git, actual files are synced separately