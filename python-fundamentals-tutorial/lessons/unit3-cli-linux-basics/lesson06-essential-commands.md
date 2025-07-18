# Lesson 6: Essential Command Line Commands

## Learning Objectives
By the end of this lesson, students will be able to:
- Navigate the file system using command line commands
- Create, copy, move, and delete files and directories
- View file contents using various commands
- Use wildcards and patterns for file operations
- Understand absolute vs relative paths
- Combine commands to perform complex tasks

## Prerequisites
- Completed Lesson 5: CLI Introduction
- Basic understanding of file systems
- Familiarity with terminal/command prompt

## Materials Needed
- Computer with terminal access
- Practice files and directories (provided)
- Command reference sheet
- Text editor (notepad, TextEdit, etc.)

## Lesson Overview (50 minutes)
1. **Review and Warm-up** (5 minutes)
2. **Navigation Commands** (15 minutes)
3. **File Operations** (15 minutes)
4. **Viewing File Contents** (10 minutes)
5. **Wildcards and Patterns** (5 minutes)

---

## Detailed Instructions

### 1. Review and Warm-up (5 minutes)

**Quick Review Questions:**
- What does CLI stand for?
- How do you open terminal on your OS?
- What command shows your current directory?
- What's the basic structure of a command?

**Warm-up Exercise:**
1. Open terminal
2. Check current directory with `pwd`
3. List files with `ls` (or `dir` on Windows)
4. Try the help flag on one command

### 2. Navigation Commands (15 minutes)

#### Understanding Paths

**Absolute Path:**
- Complete path from root directory
- Always starts with `/` (Unix/Linux/macOS) or `C:\` (Windows)
- Examples: `/home/user/Documents`, `C:\Users\Student\Desktop`

**Relative Path:**
- Path relative to current directory
- No leading slash
- Examples: `Documents/file.txt`, `../parent_directory`

**Special Directory References:**
- `.` (dot) = current directory
- `..` (dot dot) = parent directory
- `~` (tilde) = home directory (Unix/Linux/macOS)
- `/` (forward slash) = root directory (Unix/Linux/macOS)

#### Essential Navigation Commands

**1. Print Working Directory (pwd)**
```bash
pwd
```
- Shows complete path to current directory
- Helps you understand where you are

**2. List Directory Contents (ls/dir)**
```bash
ls              # Basic listing (macOS/Linux)
dir             # Basic listing (Windows)
ls -l           # Long format with details
ls -a           # Show all files including hidden
ls -la          # Long format AND show all files
ls -h           # Human-readable file sizes
```

**3. Change Directory (cd)**
```bash
cd Documents          # Go to Documents folder
cd ..                 # Go to parent directory
cd ~                  # Go to home directory
cd /                  # Go to root directory
cd ~/Desktop          # Go to Desktop using home shortcut
cd                    # Go to home directory (no argument)
```

**4. List with Specific Directories**
```bash
ls Documents          # List contents of Documents folder
ls -l ~/Desktop       # Long listing of Desktop contents
ls /usr/bin          # List contents of /usr/bin directory
```

#### Navigation Practice Exercise (8 minutes)

**Step-by-Step Practice:**
1. **Check current location:** `pwd`
2. **See what's here:** `ls` (or `dir`)
3. **Go to Desktop:** `cd Desktop`
4. **Confirm location:** `pwd`
5. **List Desktop contents:** `ls -l`
6. **Go back to parent:** `cd ..`
7. **Check location again:** `pwd`
8. **Go to home directory:** `cd ~` (or just `cd`)

**Challenge Exercise:**
Navigate to your Documents folder and list its contents in long format showing all files.

### 3. File Operations (15 minutes)

#### Creating Directories

**Make Directory (mkdir)**
```bash
mkdir new_folder              # Create single directory
mkdir folder1 folder2         # Create multiple directories
mkdir -p path/to/new/folder   # Create nested directories
```

**Examples:**
```bash
mkdir homework
mkdir projects assignments
mkdir -p school/math/homework
```

#### Creating Files

**Touch Command (Unix/Linux/macOS)**
```bash
touch filename.txt           # Create empty file
touch file1.txt file2.txt    # Create multiple files
```

**Echo Command (All systems)**
```bash
echo "Hello World" > hello.txt        # Create file with content
echo "New line" >> hello.txt          # Append to existing file
```

**Windows Alternative:**
```cmd
echo. > filename.txt         # Create empty file
echo "Hello World" > hello.txt
```

#### Copying Files and Directories

**Copy Command (cp/copy)**
```bash
cp file1.txt file2.txt              # Copy file1 to file2
cp file1.txt Documents/             # Copy file to Documents folder
cp -r folder1 folder2               # Copy directory recursively
```

**Windows:**
```cmd
copy file1.txt file2.txt
copy file1.txt Documents\
xcopy folder1 folder2 /E            # Copy directory
```

#### Moving and Renaming

**Move Command (mv/move)**
```bash
mv oldname.txt newname.txt          # Rename file
mv file.txt Documents/              # Move file to Documents
mv folder1 folder2                  # Rename/move directory
```

**Windows:**
```cmd
move oldname.txt newname.txt
move file.txt Documents\
```

#### Removing Files and Directories

**Remove Command (rm/del)**
```bash
rm filename.txt                     # Delete file
rm -r foldername                    # Delete directory recursively
rm -i filename.txt                  # Interactive deletion (asks for confirmation)
```

**Windows:**
```cmd
del filename.txt
rmdir foldername                    # Delete empty directory
rmdir /s foldername                 # Delete directory with contents
```

**⚠️ Safety Warning:**
- Deletion is usually permanent
- Always double-check before deleting
- Use `-i` flag for interactive confirmation
- Be very careful with recursive deletion

#### File Operations Practice (8 minutes)

**Practice Sequence:**
1. **Create practice directory:** `mkdir cli_practice`
2. **Go into directory:** `cd cli_practice`
3. **Create some files:** `touch file1.txt file2.txt`
4. **Create subdirectory:** `mkdir subfolder`
5. **Copy file:** `cp file1.txt file1_copy.txt`
6. **Move file:** `mv file2.txt subfolder/`
7. **List everything:** `ls -la`
8. **List subdirectory:** `ls -la subfolder/`

### 4. Viewing File Contents (10 minutes)

#### Basic File Viewing Commands

**1. Cat Command (Display entire file)**
```bash
cat filename.txt                    # Display file contents
cat file1.txt file2.txt             # Display multiple files
```

**2. Less/More Commands (Paged viewing)**
```bash
less filename.txt                   # View file page by page
more filename.txt                   # Similar to less
```

**Navigation in less/more:**
- `Space` or `PageDown` = next page
- `b` or `PageUp` = previous page
- `q` = quit
- `/search_term` = search for text

**3. Head Command (First few lines)**
```bash
head filename.txt                   # Show first 10 lines
head -n 5 filename.txt              # Show first 5 lines
```

**4. Tail Command (Last few lines)**
```bash
tail filename.txt                   # Show last 10 lines
tail -n 5 filename.txt              # Show last 5 lines
tail -f filename.txt                # Follow file (watch for changes)
```

#### Windows Equivalents

**Windows File Viewing:**
```cmd
type filename.txt                   # Display file contents
more filename.txt                   # Paged viewing
```

#### Creating Sample Files for Practice

**Create a sample file:**
```bash
echo -e "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6\nLine 7\nLine 8\nLine 9\nLine 10" > sample.txt
```

**Or create manually:**
1. Use text editor to create a file with 10 lines
2. Save as `sample.txt`
3. Practice viewing commands on this file

#### File Viewing Practice (5 minutes)

**Practice Commands:**
1. **View entire file:** `cat sample.txt`
2. **View first 3 lines:** `head -n 3 sample.txt`
3. **View last 3 lines:** `tail -n 3 sample.txt`
4. **View file page by page:** `less sample.txt` (press `q` to quit)

### 5. Wildcards and Patterns (5 minutes)

#### Common Wildcards

**Asterisk (*) - Matches any number of characters**
```bash
ls *.txt                           # All .txt files
ls file*                           # All files starting with "file"
ls *data*                          # All files containing "data"
```

**Question Mark (?) - Matches single character**
```bash
ls file?.txt                       # file1.txt, file2.txt, etc.
ls test?                           # test1, test2, testa, etc.
```

**Square Brackets ([]) - Matches character ranges**
```bash
ls file[1-3].txt                   # file1.txt, file2.txt, file3.txt
ls [A-Z]*.txt                      # Files starting with uppercase letter
```

#### Practical Wildcard Examples

**File Operations with Wildcards:**
```bash
cp *.txt Documents/                # Copy all .txt files
mv file*.txt archive/              # Move all files starting with "file"
rm temp*                           # Delete all files starting with "temp"
```

**Safety with Wildcards:**
- Always test with `ls` before using destructive commands
- Use `ls *.txt` to see what files match before `rm *.txt`
- Be careful with spaces in filenames

#### Wildcard Practice (3 minutes)

**Setup:**
```bash
touch file1.txt file2.txt file3.doc test1.txt test2.txt
```

**Practice:**
1. **List all .txt files:** `ls *.txt`
2. **List files starting with "file":** `ls file*`
3. **List files ending with numbers:** `ls *[0-9].*`

---

## Activities

### Activity 1: Navigation Challenge (10 minutes)
Students complete a navigation sequence:
1. Start at home directory
2. Navigate to Desktop
3. Create a folder called "cli_test"
4. Navigate into cli_test
5. Create three subfolders: "docs", "images", "projects"
6. Navigate to each subfolder and back
7. End at home directory

### Activity 2: File Management Practice (15 minutes)
Working in pairs, students complete file operations:
1. Create practice directory structure
2. Create several text files with content
3. Copy files between directories
4. Rename files using move command
5. View file contents using different commands
6. Use wildcards to operate on multiple files

### Activity 3: Command Combination Challenge (10 minutes)
Students combine commands to complete tasks:
1. Create a directory and navigate into it in one line
2. Create multiple files and list them
3. Copy all .txt files to a new directory
4. View the contents of multiple files at once

---

## Assessment

### Formative Assessment
**Command Demonstration:**
Students demonstrate competency by:
1. Navigating to specific directories
2. Creating and organizing files
3. Using wildcards effectively
4. Viewing file contents appropriately

### Practical Skills Check
**Required Skills:**
1. **Navigation:** Can move between directories using absolute and relative paths
2. **File Creation:** Can create files and directories
3. **File Operations:** Can copy, move, and rename files
4. **Content Viewing:** Can view file contents using appropriate commands
5. **Wildcards:** Can use basic wildcards for file operations

### Quick Assessment Quiz
1. What command creates a new directory?
2. How do you copy a file to a different directory?
3. What's the difference between `cat` and `less`?
4. What does `*.txt` match?
5. How do you go to the parent directory?

**Answer Key:**
1. `mkdir`
2. `cp filename.txt destination_directory/`
3. `cat` shows entire file, `less` shows page by page
4. All files ending with .txt
5. `cd ..`

---

## Extensions

### For Advanced Students
- Learn about command chaining with `&&` and `||`
- Explore advanced wildcards and regular expressions
- Practice with symbolic links (`ln -s`)
- Learn about file permissions preview

### For Struggling Students
- Focus on just navigation and basic file operations
- Provide printed command reference cards
- Use visual file tree diagrams
- Practice with guided step-by-step exercises

### Cross-Curricular Connections
- **Math:** Use command line for file organization in math projects
- **Science:** Practice with data file management
- **English:** Use command line for managing writing projects
- **Art:** Organize digital artwork using command line

---

## Resources

### Command Reference Sheets
- [Unix/Linux Command Reference](https://files.fosswire.com/2007/08/fwunixref.pdf)
- [Windows Command Reference](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/windows-commands)
- [macOS Terminal Commands](https://ss64.com/osx/)

### Interactive Practice
- [Command Line Mystery](https://github.com/veltman/clmystery)
- [Terminus Game](https://web.mit.edu/mprat/Public/web/Terminus/Web/main.html)
- [Command Line Bootcamp](http://rik.smith-unna.com/command_line_bootcamp/)

### Video Tutorials
- [Linux Command Line Tutorial](https://www.youtube.com/watch?v=cBokz0LTizk) (20 minutes)
- [File Management Commands](https://www.youtube.com/watch?v=UdKFqvJGEFc) (15 minutes)
- [Wildcards and Patterns](https://www.youtube.com/watch?v=7BRsNkOzBps) (10 minutes)

### Online Tools
- [ExplainShell](https://explainshell.com/) - Command breakdown
- [JSLinux](https://bellard.org/jslinux/) - Linux emulator in browser
- [Command Line Simulator](https://copy.sh/v86/) - Practice environment

---

## Homework

### Required Practice
1. **Navigation Practice:** Navigate through your computer's directory structure using only command line
2. **File Organization:** Create a homework folder structure for your classes
3. **File Operations:** Practice copying, moving, and renaming files
4. **Content Viewing:** Use different commands to view text files

### Creative Project
Create a personal file organization system using command line:
1. Design a folder structure for your school work
2. Create folders for each subject
3. Add subfolders for different types of assignments
4. Practice moving files into appropriate folders

### Reflection Journal
Write a short reflection (3-4 sentences) about:
1. Which commands felt most natural to use?
2. What was most challenging about using command line?
3. How might command line be useful in your daily computer use?

---

## Notes for Instructors

### Preparation
- Create practice files and directories for students
- Test all commands on available systems
- Prepare safety guidelines for file operations
- Have backup files in case of student errors

### Common Student Mistakes
- **Path confusion:** Mix up absolute and relative paths
- **Case sensitivity:** Forget about case-sensitive file systems
- **Spacing:** Add spaces in filenames without quotes
- **Deletion accidents:** Use rm without thinking

### Safety Protocols
- Start with test directories only
- Teach `ls` before any destructive commands
- Always demonstrate commands before student practice
- Have students practice in designated folders

### Differentiation Strategies
- **Visual learners:** Use tree diagrams of directory structures
- **Kinesthetic learners:** Maximize hands-on practice
- **Advanced students:** Introduce command combinations early
- **Struggling students:** Focus on fewer commands initially

### Assessment Rubric
**Proficient (3):** Can navigate and perform all file operations independently
**Developing (2):** Can perform basic operations with minimal guidance
**Beginning (1):** Requires significant help with most commands
**Not Yet (0):** Cannot perform basic navigation or file operations

### Extension Activities
- Research command line tools for specific subjects
- Create scripts for repetitive tasks
- Explore advanced file manipulation
- Learn about command history and shortcuts
