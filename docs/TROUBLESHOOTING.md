# Meshachvetz Troubleshooting Guide

## 🔧 Common Issues and Solutions

### RuntimeWarning: 'meshachvetz.cli.main' found in sys.modules

**Problem:** You see this warning when running the CLI:
```
<frozen runpy>:128: RuntimeWarning: 'meshachvetz.cli.main' found in sys.modules after import of package 'meshachvetz.cli', but prior to execution of 'meshachvetz.cli.main'; this may result in unpredictable behaviour
```

**Solution:** This warning has been fixed in the latest version. To resolve:

1. **For new installations:** The issue is automatically resolved
2. **For existing installations:** 
   - Delete old run scripts: `rm run_meshachvetz.sh run_meshachvetz.bat`
   - Regenerate scripts: `python -c "import install; install.create_run_script()"`
   - The new scripts use the direct `meshachvetz` command instead of `python -m`

**Technical Details:** The warning occurred because we were using `python -m meshachvetz.cli.main`, which can cause module import conflicts. The fix uses the proper console script entry point defined in `setup.py`.

### Installation Issues

#### "Python not found" Error

**Problem:** Installation fails with "Python not found" or "Python is not installed"

**Solutions:**
1. **Install Python 3.8+** from [python.org](https://python.org)
2. **Windows:** Make sure to check "Add Python to PATH" during installation
3. **Mac:** Install via Homebrew: `brew install python3`
4. **Linux:** Install via package manager: `sudo apt install python3` or `sudo yum install python3`

#### "Permission denied" Error

**Problem:** Cannot run installation scripts

**Solutions:**
- **Windows:** Right-click `install.bat` and select "Run as administrator"
- **Mac/Linux:** Make script executable: `chmod +x install.sh`

#### Virtual Environment Creation Fails

**Problem:** Installation fails when creating virtual environment

**Solutions:**
1. **Clear existing environment:** `rm -rf meshachvetz_env`
2. **Install venv module:** `python -m pip install --upgrade pip`
3. **Check Python installation:** `python --version` should show 3.8+

### CLI Issues

#### "Command not found" Error

**Problem:** Running `./run_meshachvetz.sh` or `run_meshachvetz.bat` fails

**Solutions:**
1. **Make sure you're in the right directory:** The project root folder
2. **Run installation first:** Double-click `install.bat` or `install.sh`
3. **Check script exists:** `ls run_meshachvetz.*`
4. **Make executable (Unix):** `chmod +x run_meshachvetz.sh`

#### Data Validation Errors

**Problem:** CSV file validation fails

**Common Issues:**
- **Student ID format:** Must be exactly 9 digits (e.g., `123456789`)
- **Gender values:** Must be `M` or `F` (uppercase)
- **Behavior ranks:** Must be `A`, `B`, `C`, `D`, or `E`
- **Academic scores:** Must be numbers between 0 and 100
- **Missing columns:** Check all required columns are present

**Solution:** Use `./run_meshachvetz.sh validate your_file.csv` to get detailed error messages

### Performance Issues

#### Slow Processing

**Problem:** Scoring takes a long time

**Solutions:**
1. **Large datasets:** Expected for 1000+ students
2. **Use quiet mode:** Add `--quiet` flag
3. **Disable detailed reports:** Remove `--detailed` flag
4. **Check system resources:** Close other applications

#### Memory Issues

**Problem:** Out of memory errors

**Solutions:**
1. **Split large files:** Process smaller chunks
2. **Remove unnecessary columns:** Only include required data
3. **Close other applications:** Free up system memory

### Output Issues

#### No Reports Generated

**Problem:** Expected CSV reports are missing

**Solutions:**
1. **Use --reports flag:** `./run_meshachvetz.sh score file.csv --reports`
2. **Check output directory:** Look for `results_YYYY-MM-DD_HH-MM-SS/` folder
3. **Use custom output:** `--output my_results`

#### Scoring Results Seem Wrong

**Problem:** Scores don't match expectations

**Diagnostic Steps:**
1. **Check data quality:** Validate your CSV file first
2. **Review weights:** Use `./run_meshachvetz.sh config show`
3. **Use detailed mode:** Add `--detailed --verbose` flags
4. **Compare with sample data:** Test with provided examples

### Platform-Specific Issues

#### Windows PowerShell Execution Policy

**Problem:** Cannot run .bat files in PowerShell

**Solution:** 
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### macOS Catalina+ Security

**Problem:** "Cannot open because developer cannot be verified"

**Solution:**
1. **System Preferences** → **Security & Privacy**
2. Click **"Allow Anyway"** next to the blocked application

#### Linux Dependencies

**Problem:** Missing system dependencies

**Solution:**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip python3-venv

# CentOS/RHEL
sudo yum install python3 python3-pip python3-venv
```

## 📞 Getting Help

### Before Reporting Issues

1. **Try the sample data first:** Test with `examples/test_data/perfect_score_test.csv`
2. **Check the documentation:** Review `docs/CLI_USER_GUIDE.md`
3. **Validate your data:** Use the validate command first
4. **Check installation:** Reinstall if necessary

### Diagnostic Commands

```bash
# Check installation
./run_meshachvetz.sh --help

# Test with sample data
./run_meshachvetz.sh score examples/test_data/perfect_score_test.csv

# Validate your data
./run_meshachvetz.sh validate your_students.csv

# Check configuration
./run_meshachvetz.sh config show

# Verbose output for debugging
./run_meshachvetz.sh score your_students.csv --verbose --detailed
```

### Information to Include When Reporting Issues

1. **Operating system and version**
2. **Python version:** `python --version`
3. **Complete error message**
4. **Command you were trying to run**
5. **Sample of your CSV data (anonymized)**

## 🔄 Clean Reinstallation

If all else fails, try a clean reinstallation:

1. **Remove virtual environment:** `rm -rf meshachvetz_env`
2. **Remove run scripts:** `rm run_meshachvetz.*`
3. **Run installation again:** Double-click `install.bat` or `install.sh`

This will create a fresh installation and should resolve most issues. 