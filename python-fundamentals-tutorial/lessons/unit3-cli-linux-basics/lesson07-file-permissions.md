# Lesson 7: File Permissions and System Information

## Learning Objectives
By the end of this lesson, students will be able to:
- Understand file permissions and ownership concepts
- Read and interpret permission notation (symbolic and octal)
- Modify file permissions using chmod command
- View and understand system information commands
- Use commands to monitor system resources
- Understand the importance of file security

## Prerequisites
- Completed Lessons 5 and 6
- Understanding of file system basics
- Familiarity with essential CLI commands

## Materials Needed
- Computer with terminal access (preferably Unix/Linux/macOS)
- Practice files for permission exercises
- System monitoring tools
- Permission reference charts

## Lesson Overview (50 minutes)
1. **Introduction to File Permissions** (15 minutes)
2. **Understanding Permission Notation** (15 minutes)
3. **Changing Permissions** (10 minutes)
4. **System Information Commands** (10 minutes)

---

## Detailed Instructions

### 1. Introduction to File Permissions (15 minutes)

#### Why File Permissions Matter

**Security Concepts:**
- **Access Control:** Who can access what files
- **Data Protection:** Preventing unauthorized changes
- **System Security:** Protecting system files
- **Privacy:** Controlling personal file access

**Real-World Examples:**
- **Personal Documents:** Only you can read/edit
- **System Files:** Only administrators can modify
- **Shared Projects:** Group members can collaborate
- **Public Files:** Everyone can read, few can edit

#### Permission Categories

**Three Types of Users:**
1. **Owner (User):** The person who created the file
2. **Group:** Users who belong to the same group
3. **Others (World):** Everyone else on the system

**Three Types of Permissions:**
1. **Read (r):** View file contents or list directory contents
2. **Write (w):** Modify file contents or create/delete files in directory
3. **Execute (x):** Run file as program or access directory

#### Viewing File Permissions

**Using ls -l Command:**
```bash
ls -l filename.txt
```

**Example Output:**
```
-rw-r--r--  1 student  staff  1024 Nov 15 10:30 homework.txt
drwxr-xr-x  2 student  staff    68 Nov 15 10:25 projects
```

**Understanding the Output:**
- First character: File type (`-` = file, `d` = directory)
- Next 9 characters: Permissions (3 groups of 3)
- Number: Links count
- First name: Owner
- Second name: Group
- Size: File size in bytes
- Date/Time: Last modification
- Name: File/directory name

#### Breaking Down Permission Strings

**Permission String Format:**
```
drwxr-xr-x
│└┬┘└┬┘└┬┘
│ │  │  └─ Others permissions (r-x)
│ │  └──── Group permissions (r-x)
│ └─────── Owner permissions (rwx)
└───────── File type (d = directory)
```

**Examples:**
- `rw-r--r--`: Owner can read/write, others can only read
- `rwxr-xr-x`: Owner can do everything, others can read/execute
- `rw-------`: Only owner can read/write, no access for others

### 2. Understanding Permission Notation (15 minutes)

#### Symbolic Notation

**Permission Symbols:**
- `r` = Read (4)
- `w` = Write (2)
- `x` = Execute (1)
- `-` = No permission (0)

**Common Permission Combinations:**
- `rwx` (7) = Read, Write, Execute
- `rw-` (6) = Read, Write
- `r-x` (5) = Read, Execute
- `r--` (4) = Read only
- `-wx` (3) = Write, Execute
- `-w-` (2) = Write only
- `--x` (1) = Execute only
- `---` (0) = No permissions

#### Octal (Numeric) Notation

**How Octal Works:**
- Each permission has a numeric value
- Add values together for each user category
- Results in a 3-digit number

**Calculating Octal Values:**
```
Read (r) = 4
Write (w) = 2
Execute (x) = 1

rwx = 4 + 2 + 1 = 7
rw- = 4 + 2 + 0 = 6
r-x = 4 + 0 + 1 = 5
r-- = 4 + 0 + 0 = 4
```

**Common Octal Permissions:**
- `755` = rwxr-xr-x (owner: all, group/others: read/execute)
- `644` = rw-r--r-- (owner: read/write, group/others: read)
- `777` = rwxrwxrwx (everyone: all permissions)
- `700` = rwx------ (owner: all, group/others: none)
- `666` = rw-rw-rw- (everyone: read/write)

#### Permission Examples Analysis

**Practice Reading Permissions:**
```bash
ls -l
```

**Sample Output Analysis:**
```
-rw-r--r--  1 student  staff   256 Nov 15 10:30 essay.txt
-rwxr-xr-x  1 student  staff   512 Nov 15 10:25 script.sh
drwxr-xr-x  2 student  staff    68 Nov 15 10:20 homework
-rw-------  1 student  staff   128 Nov 15 10:35 diary.txt
```

**Analysis:**
1. `essay.txt` (644): Owner can read/write, others can only read
2. `script.sh` (755): Owner can do everything, others can read/execute
3. `homework` (755): Directory, same permissions as above
4. `diary.txt` (600): Only owner can read/write, private file

### 3. Changing Permissions (10 minutes)

#### Using chmod Command

**Basic Syntax:**
```bash
chmod permissions filename
```

**Symbolic Mode:**
```bash
chmod u+rwx filename          # Add all permissions for user
chmod g+r filename            # Add read permission for group
chmod o-w filename            # Remove write permission for others
chmod a+x filename            # Add execute permission for all
```

**Octal Mode:**
```bash
chmod 755 filename            # Set specific permissions
chmod 644 filename            # Set read/write for owner, read for others
chmod 700 filename            # Set all permissions for owner only
```

#### Symbolic Mode Details

**Permission Modification Symbols:**
- `u` = User (owner)
- `g` = Group
- `o` = Others
- `a` = All (user + group + others)

**Operation Symbols:**
- `+` = Add permission
- `-` = Remove permission
- `=` = Set exact permission

**Examples:**
```bash
chmod u+x script.sh           # Make script executable for owner
chmod g-w document.txt        # Remove write permission from group
chmod o=r public.txt          # Set others to read-only
chmod a+r readme.txt          # Make file readable by everyone
```

#### Practical Permission Changes

**Common Scenarios:**
1. **Make script executable:**
   ```bash
   chmod +x script.sh
   ```

2. **Make file private:**
   ```bash
   chmod 600 private.txt
   ```

3. **Share with group:**
   ```bash
   chmod 664 shared.txt
   ```

4. **Public read-only:**
   ```bash
   chmod 644 public.txt
   ```

#### Directory Permissions

**Directory-Specific Meanings:**
- **Read (r):** List directory contents
- **Write (w):** Create/delete files in directory
- **Execute (x):** Access directory (cd into it)

**Common Directory Permissions:**
- `755` = rwxr-xr-x (standard directory)
- `700` = rwx------ (private directory)
- `755` = rwxr-xr-x (shared directory)

### 4. System Information Commands (10 minutes)

#### System Status Commands

**1. Who and What Commands**
```bash
whoami                        # Show current username
who                          # Show logged-in users
id                           # Show user and group IDs
```

**2. System Information**
```bash
uname -a                     # System information
date                         # Current date and time
uptime                       # System uptime and load
hostname                     # Computer name
```

**3. Disk Usage**
```bash
df -h                        # Disk space usage (human readable)
du -sh foldername            # Directory size
du -h --max-depth=1          # Size of subdirectories
```

**4. Memory and Process Information**
```bash
free -h                      # Memory usage (Linux)
top                          # Running processes (press q to quit)
ps aux                       # Process list
```

#### File System Information

**File and Directory Information:**
```bash
ls -la                       # Detailed file listing
stat filename.txt            # Detailed file information
file filename.txt            # File type information
wc filename.txt              # Word count, lines, characters
```

**Finding Files:**
```bash
find . -name "*.txt"         # Find all .txt files
locate filename              # Find file by name (if available)
which command                # Find location of command
```

#### System Monitoring

**Resource Monitoring:**
```bash
top                          # Real-time process viewer
htop                         # Enhanced process viewer (if available)
ps aux | grep process_name   # Find specific process
```

**Network Information:**
```bash
ping google.com              # Test network connectivity
curl ifconfig.me             # Show public IP address
```

---

## Activities

### Activity 1: Permission Detective (15 minutes)
Students analyze file permissions:
1. Create several files with different permissions
2. Use `ls -l` to view permissions
3. Identify who can do what with each file
4. Predict what will happen with different operations

### Activity 2: Permission Modification Practice (15 minutes)
Students practice changing permissions:
1. Create test files and directories
2. Practice with symbolic mode (`chmod u+x`, etc.)
3. Practice with octal mode (`chmod 755`, etc.)
4. Verify changes with `ls -l`
5. Test actual permission effects

### Activity 3: System Exploration (10 minutes)
Students explore system information:
1. Check their username and ID
2. View system information
3. Check disk usage
4. Explore process information
5. Share interesting findings with class

---

## Assessment

### Formative Assessment
**Permission Understanding:**
- Can read and interpret permission strings
- Understands the difference between owner, group, and others
- Can explain what each permission type allows

**Practical Skills:**
- Can change permissions using both symbolic and octal notation
- Can verify permission changes
- Can use system information commands

### Quick Check Questions
1. What does `rw-r--r--` mean?
2. How do you make a file executable for everyone?
3. What octal number represents `rwx------`?
4. Which command shows disk usage?
5. How do you find out your username?

**Answer Key:**
1. Owner can read/write, group/others can only read
2. `chmod a+x filename` or `chmod 755 filename`
3. 700
4. `df -h`
5. `whoami`

### Practical Assessment
Students demonstrate:
1. **Reading permissions:** Correctly interpret `ls -l` output
2. **Modifying permissions:** Change permissions using both methods
3. **System information:** Use commands to gather system info
4. **Security awareness:** Explain why permissions matter

---

## Extensions

### For Advanced Students
- Learn about special permissions (setuid, setgid, sticky bit)
- Explore user and group management commands
- Research file system security best practices
- Learn about access control lists (ACLs)

### For Struggling Students
- Focus on basic permission concepts first
- Use visual permission charts
- Practice with guided exercises
- Emphasize practical security examples

### Real-World Applications
- **Web Development:** Understanding web server permissions
- **System Administration:** Managing user access
- **Data Security:** Protecting sensitive information
- **Collaborative Projects:** Sharing files safely

---

## Resources

### Reference Materials
- [Linux File Permissions Guide](https://www.guru99.com/file-permissions.html)
- [chmod Command Reference](https://ss64.com/bash/chmod.html)
- [Unix Permissions Calculator](https://chmod-calculator.com/)

### Interactive Tools
- [Permission Calculator](https://www.rapidtables.com/code/linux/chmod.html)
- [Linux Permissions Simulator](https://training.github.com/downloads/subversion-cheat-sheet/)

### Video Resources
- [Linux File Permissions Explained](https://www.youtube.com/watch?v=BmVmJi5dR9c) (15 minutes)
- [chmod Command Tutorial](https://www.youtube.com/watch?v=ngJG6Ix5FR4) (10 minutes)

---

## Homework

### Required Practice
1. **Permission Analysis:** Use `ls -l` to analyze files in your home directory
2. **Permission Modification:** Practice changing permissions on practice files
3. **System Information:** Explore your system using information commands
4. **Security Reflection:** Write about why file permissions are important

### Creative Project
Design a file organization system with appropriate permissions:
1. Create different types of files (private, shared, public)
2. Set appropriate permissions for each type
3. Test permissions by switching user contexts (if possible)
4. Document your permission strategy

### Research Assignment
Research file permission best practices:
1. Find examples of good permission practices
2. Research common permission mistakes
3. Learn about one advanced permission topic
4. Share findings with the class

---

## Notes for Instructors

### Platform Considerations
- **Unix/Linux/macOS:** Full permission system available
- **Windows:** Limited permission system, focus on concepts
- **Mixed Environment:** Provide alternatives for different systems

### Safety Considerations
- Start with test files only
- Avoid system files and directories
- Teach checking permissions before changing them
- Emphasize the importance of backups

### Common Student Challenges
- **Octal confusion:** Use visual aids and calculators
- **Permission logic:** Practice with real-world examples
- **Command syntax:** Provide reference cards
- **Security concepts:** Use relatable analogies

### Assessment Rubric
**Mastery (4):** Can read, interpret, and modify permissions confidently
**Proficient (3):** Can perform basic permission operations with minimal guidance
**Developing (2):** Understands concepts but needs help with commands
**Beginning (1):** Limited understanding of permission concepts

### Extension Activities
- Set up group projects with shared permissions
- Create permission-based puzzles and challenges
- Research historical computer security incidents
- Explore modern security practices and tools

### Cross-Platform Notes
- Windows uses different permission model
- macOS and Linux are very similar
- Adapt exercises for available platforms
- Use virtual machines if needed for consistency
