# National Rail Data Project

This project downloads and processes timetable data from the National Rail DTD feed using Python.

## Structure

- `src/`: source code
- `config/config_template.json`: example config file for authentication credentials
- `requirements.txt`: Python dependencies

## Getting Started

1. Copy `config/config_template.json` to `config/config.json`
2. Fill in your NRDP `username` and `password`
3. Run the script:

```bash
python src/auth.py
