# 🎓 Getting Started with Meshachvetz

**Welcome to Meshachvetz - Your Student Class Assignment Scoring Tool!**

## What is Meshachvetz?

Meshachvetz helps educators evaluate how well students are assigned to classes by scoring three key areas:
- **Student Happiness**: Friend placement and conflict avoidance
- **Class Balance**: Gender distribution within classes
- **School Balance**: Even distribution of abilities across classes

## 🚀 Quick Start (5 minutes)

### Step 1: Install
Choose your operating system:

**🪟 Windows Users:**
- Double-click `install.bat`
- Wait for installation to complete

**🍎 Mac Users:**
- Double-click `install.sh`
- Wait for installation to complete

**🐧 Linux Users:**
- Run `./install.sh` in terminal
- Wait for installation to complete

### Step 2: Test with Sample Data
After installation, try it out:

**Windows:**
```
run_meshachvetz.bat score examples/test_data/perfect_score_test.csv
```

**Mac/Linux:**
```
./run_meshachvetz.sh score examples/test_data/perfect_score_test.csv
```

You should see a score around 99/100 - that's a great assignment!

### Step 3: Use Your Own Data
1. Create a CSV file with your student data (see `examples/test_data/` for format)
2. Run: `run_meshachvetz score your_students.csv --reports`
3. Review the generated reports to understand your class assignments

## 📁 Important Files

- `install.bat` / `install.sh` - Installation scripts
- `run_meshachvetz.bat` / `run_meshachvetz.sh` - Run the program
- `docs/CLI_USER_GUIDE.md` - Complete user guide
- `examples/test_data/` - Sample CSV files to see the format

## 🆘 Need Help?

### Common Issues
- **"Python not found"** - Install Python 3.8+ from python.org
- **"Permission denied"** - Right-click and "Run as administrator" (Windows)
- **Data format errors** - Check your CSV matches the format in `examples/test_data/`

### Documentation
- **📖 [CLI User Guide](docs/CLI_USER_GUIDE.md)** - Complete instructions
- **📋 [Data Format Guide](docs/02_data_format_specification.md)** - CSV format requirements
- **📊 [Technical Docs](docs/)** - Advanced features and design

## 🎯 What You Get

- **Scores (0-100)** for your class assignments
- **Detailed reports** showing what works and what doesn't
- **Student satisfaction** analysis
- **Class balance** metrics
- **Recommendations** for improvements

## 💡 Quick Tips

1. **Start simple**: Use the sample data first to understand the tool
2. **Fill in social preferences**: The more friend/dislike data, the better the analysis
3. **Try different scenarios**: Use the tool to compare different class arrangements
4. **Read the scores**: 85+ is excellent, 70-84 is good, below 70 needs work

---

**Ready to improve your class assignments? Start with Step 1 above! 🚀** 