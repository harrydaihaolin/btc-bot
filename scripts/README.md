# Scripts Directory

This directory contains utility scripts for managing and testing the tennis court booking bots.

## Available Scripts

### Setup Scripts
- **`setup_credentials.sh`** - Interactive script to set up BTC credentials in environment variables
- **`setup_ubc_credentials.py`** - Interactive script to set up UBC credentials in environment variables

### Management Scripts
- **`run_daemon.sh`** - One-command script to start daemon monitoring for BTC
- **`docker-manage.sh`** - Docker Compose management script for starting/stopping containerized bots
- **`setup-github-secrets.sh`** - Helper script to set up GitHub Actions secrets

### Testing Scripts
- **`test_modular_structure.py`** - Test script to verify the modular architecture is working correctly

## Usage

### Quick Start
```bash
# Set up credentials
./scripts/setup_credentials.sh

# Start daemon monitoring
./scripts/run_daemon.sh

# Or use Docker
./scripts/docker-manage.sh start
```

### Testing
```bash
# Test modular structure
python3 scripts/test_modular_structure.py
```

## Notes

- All scripts should be run from the project root directory
- Make sure to source your shell configuration (`source ~/.zshrc`) before running scripts that depend on environment variables
- The daemon scripts will run continuously until stopped with Ctrl+C
