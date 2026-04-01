# GitHub Push Instructions

## Method 1: HTTPS with Personal Access Token

```bash
cd /home/din/Projects/budget-vr-tracker
git remote add origin https://github.com/Dimi90064SWuper/budget-vr-tracker.git
git push -u origin main
```

When prompted:
- Username: `Dimi90064SWuper`
- Password: [Personal Access Token](https://github.com/settings/tokens)

## Create Personal Access Token:

1. Go to https://github.com/settings/tokens
2. Click **Generate new token (classic)**
3. Select scopes: `repo`, `workflow`
4. Click **Generate token**
5. Copy the token (shown once!)
6. Use it as password when pushing

## Method 2: SSH

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to GitHub: https://github.com/settings/keys
# Then:
git remote add origin git@github.com:Dimi90064SWuper/budget-vr-tracker.git
git push -u origin main
```

## Verify

Open: https://github.com/Dimi90064SWuper/budget-vr-tracker
