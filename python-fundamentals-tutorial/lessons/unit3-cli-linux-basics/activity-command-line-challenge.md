# Activity: Command Line Challenge

## Overview
This hands-on activity challenges students to complete a series of command-line tasks that progressively build their skills in file navigation, file operations, and system management. Students will work through scenarios that simulate real-world computing tasks.

## Learning Objectives
- Apply command-line navigation skills in practical scenarios
- Demonstrate file and directory management competency
- Use wildcards and patterns effectively
- Combine multiple commands to solve complex problems
- Build confidence in command-line problem-solving

## Time Required
- **Setup:** 5 minutes
- **Main Activity:** 30 minutes
- **Reflection:** 10 minutes
- **Total:** 45 minutes

## Materials Needed
- Computer with terminal access
- Starting files (provided by instructor)
- Command reference sheet
- Worksheet for tracking progress

---

## Challenge Setup

### Pre-Activity Preparation
Instructors should create the following directory structure and files:

```
challenge_start/
├── documents/
│   ├── report1.txt
│   ├── report2.txt
│   ├── notes.txt
│   └── old_notes.txt
├── projects/
│   ├── project_a/
│   │   ├── code.py
│   │   └── readme.txt
│   ├── project_b/
│   │   ├── script.sh
│   │   └── data.csv
│   └── archive/
│       ├── old_project.zip
│       └── backup.tar
├── images/
│   ├── photo1.jpg
│   ├── photo2.jpg
│   ├── logo.png
│   └── banner.gif
└── temp/
    ├── temp1.tmp
    ├── temp2.tmp
    └── cache.tmp
```

### Student Starting Position
All students should:
1. Download/receive the `challenge_start` folder
2. Place it in their home directory
3. Open terminal and navigate to the challenge_start folder
4. Confirm they're in the right place with `pwd`

---

## Challenge Tasks

### Round 1: Basic Navigation (10 minutes)

**Task 1.1: Location Verification**
- Use a command to show your current directory
- List all files and folders in the current directory
- Navigate to the `documents` folder
- Verify you're in the correct location

**Task 1.2: Exploration**
- Count how many files are in the `documents` folder
- Navigate to the `projects` folder
- List all subdirectories in `projects`
- Return to the main `challenge_start` directory

**Task 1.3: Path Practice**
- Navigate to `projects/project_a` using a single command
- From there, navigate to the `images` folder using a relative path
- Return to your home directory using the shortest possible command

### Round 2: File Operations (10 minutes)

**Task 2.1: File Organization**
- Create a new directory called `organized`
- Create three subdirectories inside `organized`: `docs`, `media`, `code`
- Copy all `.txt` files from `documents` to `organized/docs`
- Copy all image files from `images` to `organized/media`

**Task 2.2: File Management**
- Move all `.py` files from the projects directories to `organized/code`
- Create a backup copy of `organized/docs` called `docs_backup`
- Rename `old_notes.txt` to `archive_notes.txt`

**Task 2.3: Cleanup**
- Remove all files from the `temp` directory
- Delete the empty `temp` directory
- Create a new empty file called `inventory.txt` in the `organized` directory

### Round 3: Advanced Operations (10 minutes)

**Task 3.1: Pattern Matching**
- Find all files ending with `.txt` in the entire challenge directory
- Copy all files starting with "project" to a new folder called `project_files`
- List all files that contain numbers in their names

**Task 3.2: Content Exploration**
- Display the contents of any text file you find
- Show the first 5 lines of the longest text file
- Count the number of lines in all `.txt` files combined

**Task 3.3: Permission Management**
- Check the permissions of all files in `organized/code`
- Make all `.py` files executable
- Change permissions of `inventory.txt` so only you can read and write it

---

## Scoring System

### Points Distribution
- **Task Completion:** 2 points per task (18 total)
- **Efficiency:** 1 point for using optimal commands
- **Accuracy:** 1 point for correct results
- **Bonus:** 2 points for creative solutions

### Difficulty Levels
- **Beginner:** Complete Round 1 (6 points)
- **Intermediate:** Complete Rounds 1-2 (12 points)
- **Advanced:** Complete all rounds (18+ points)

### Verification Commands
Students can verify their work using:
```bash
# Check directory structure
find organized -type f | sort

# Verify file counts
ls -la organized/docs | wc -l
ls -la organized/media | wc -l
ls -la organized/code | wc -l

# Check permissions
ls -la organized/code/*.py
ls -la organized/inventory.txt
```

---

## Challenge Variations

### Team Challenge
- Students work in pairs
- One person navigates, the other operates
- Switch roles every round
- Team must agree on commands before executing

### Speed Challenge
- Set time limits for each round
- Award bonus points for early completion
- Accuracy still required for points

### Mystery Challenge
- Provide only the end goal, not step-by-step tasks
- Students must figure out the required commands
- Example: "Organize all files by type in a new directory structure"

### Collaborative Challenge
- Each student completes part of a larger task
- Must communicate file locations and status
- Final result requires everyone's contribution

---

## Troubleshooting Guide

### Common Issues
**"Command not found"**
- Check spelling and capitalization
- Verify you're using the correct command for your OS
- Try the help flag: `command --help`

**"Permission denied"**
- Check file permissions with `ls -l`
- Use `chmod` to modify permissions if needed
- Verify you're in the correct directory

**"File not found"**
- Use `pwd` to check current location
- Use `ls` to see available files
- Check for typos in filename

**"Directory not empty"**
- Use `rm -r` to remove directories with contents
- Or empty the directory first, then remove it

### Help Resources
- Use `man command` for detailed help
- Try `command --help` for quick reference
- Use tab completion to avoid typos
- Use `history` to review previous commands

---

## Extension Activities

### Advanced Challenges
**1. Automation Script**
- Create a shell script that completes some tasks automatically
- Use variables and loops if familiar with scripting
- Make the script executable and run it

**2. File System Analysis**
- Analyze the file system structure created
- Generate a report on file types and sizes
- Create a visual representation of the directory tree

**3. Backup Strategy**
- Design a backup strategy for the organized files
- Implement the backup using command line tools
- Test the backup by restoring files

### Creative Extensions
**1. Command Line Art**
- Use text files to create ASCII art
- Display the art using `cat` command
- Create a gallery of command-line creations

**2. System Monitoring**
- Monitor system resources during the challenge
- Track disk usage changes
- Document process information

**3. Cross-Platform Comparison**
- Compare commands across different operating systems
- Document differences and similarities
- Create a cross-platform command guide

---

## Assessment Rubric

### Technical Skills (60%)
- **Command Execution:** Can execute commands correctly and efficiently
- **Navigation:** Can navigate directory structures confidently
- **File Operations:** Can create, copy, move, and delete files appropriately
- **Problem Solving:** Can troubleshoot issues and find solutions

### Process Skills (40%)
- **Planning:** Thinks through tasks before executing
- **Verification:** Checks work for accuracy
- **Efficiency:** Uses optimal commands and approaches
- **Collaboration:** Works well with others (if applicable)

### Scoring Scale
- **4 - Exemplary:** Completes all tasks efficiently with creative solutions
- **3 - Proficient:** Completes most tasks with minimal guidance
- **2 - Developing:** Completes basic tasks with some assistance
- **1 - Beginning:** Requires significant help to complete tasks

---

## Reflection Questions

### Individual Reflection
1. Which tasks felt most natural to complete?
2. What commands did you find most challenging?
3. How did your confidence with command line change during the activity?
4. What strategies did you develop for troubleshooting?
5. How might these skills be useful in future work?

### Group Discussion
1. What different approaches did people take to solve the same problems?
2. Which commands were most frequently used?
3. What common mistakes did people make?
4. How can we improve our command-line efficiency?
5. What would you want to learn next about command line?

### Learning Connections
1. How does this connect to file system concepts from previous lessons?
2. What parallels do you see with GUI file management?
3. How might these skills apply to programming projects?
4. What professional contexts might require these skills?

---

## Answer Key (For Instructors)

### Round 1 Solutions
**Task 1.1:**
```bash
pwd
ls -la
cd documents
pwd
```

**Task 1.2:**
```bash
ls | wc -l
cd ../projects
ls -la
cd ..
```

**Task 1.3:**
```bash
cd projects/project_a
cd ../../images
cd ~ 
```

### Round 2 Solutions
**Task 2.1:**
```bash
mkdir organized
mkdir organized/docs organized/media organized/code
cp documents/*.txt organized/docs/
cp images/*.jpg images/*.png images/*.gif organized/media/
```

**Task 2.2:**
```bash
find projects -name "*.py" -exec cp {} organized/code/ \;
cp -r organized/docs organized/docs_backup
mv documents/old_notes.txt documents/archive_notes.txt
```

**Task 2.3:**
```bash
rm temp/*
rmdir temp
touch organized/inventory.txt
```

### Round 3 Solutions
**Task 3.1:**
```bash
find . -name "*.txt"
mkdir project_files
find . -name "project*" -exec cp {} project_files/ \;
ls -la | grep [0-9]
```

**Task 3.2:**
```bash
cat documents/report1.txt
head -n 5 documents/report1.txt
wc -l documents/*.txt
```

**Task 3.3:**
```bash
ls -la organized/code
chmod +x organized/code/*.py
chmod 600 organized/inventory.txt
```

---

## Materials for Download

### Student Worksheet
```
Command Line Challenge - Progress Tracker

Round 1: Basic Navigation
□ Task 1.1: Location Verification
□ Task 1.2: Exploration  
□ Task 1.3: Path Practice

Round 2: File Operations
□ Task 2.1: File Organization
□ Task 2.2: File Management
□ Task 2.3: Cleanup

Round 3: Advanced Operations
□ Task 3.1: Pattern Matching
□ Task 3.2: Content Exploration
□ Task 3.3: Permission Management

Commands I Used:
___________________________
___________________________
___________________________

Challenges I Faced:
___________________________
___________________________
___________________________

New Things I Learned:
___________________________
___________________________
___________________________
```

### Command Reference Card
```
Essential Commands Quick Reference

Navigation:
pwd - print working directory
ls - list files
cd - change directory
cd .. - go to parent directory
cd ~ - go to home directory

File Operations:
mkdir - create directory
touch - create empty file
cp - copy files
mv - move/rename files
rm - remove files
rm -r - remove directory

Viewing:
cat - display file contents
less - view file page by page
head - show first lines
tail - show last lines

Wildcards:
* - match any characters
? - match single character
*.txt - all .txt files
file* - files starting with 'file'

Permissions:
chmod - change permissions
ls -l - show detailed permissions
```
