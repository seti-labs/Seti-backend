# 🔧 Installation Fix Guide

If you encountered installation errors, follow these steps:

## Step 1: Create Virtual Environment

```bash
cd /Users/mac/Works/SetLabs/backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
```

You should see `(venv)` appear in your terminal prompt.

## Step 2: Upgrade pip

```bash
pip install --upgrade pip
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This should now install without errors!

## Step 4: Verify Installation

```bash
python --version  # Should show Python 3.9.6
pip list          # Should show all installed packages
```

## Step 5: Run the Backend

```bash
# Make sure you're in the virtual environment (you should see "(venv)")
python run.py
```

## Common Issues

### "No module named 'flask'"
**Solution**: Make sure virtual environment is activated. You should see `(venv)` in your prompt.

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "command not found: python"
**Solution**: Use `python3` instead:
```bash
python3 run.py
```

### Virtual environment already exists
**Solution**: Just activate it:
```bash
source venv/bin/activate
```

### Packages installing to user directory
**Solution**: This means virtual environment is not activated. Run:
```bash
source venv/bin/activate
```

## Deactivating Virtual Environment

When you're done:
```bash
deactivate
```

## Quick Reference

```bash
# Activate venv
source venv/bin/activate

# Check if active (should see "(venv)")
echo $VIRTUAL_ENV

# Run backend
python run.py

# Deactivate when done
deactivate
```

