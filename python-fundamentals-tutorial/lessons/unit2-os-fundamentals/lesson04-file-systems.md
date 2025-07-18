# Lesson 4: File Systems and Directory Structure

## Learning Objectives
By the end of this lesson, students will be able to:
- Explain what a file system is and why it's important
- Navigate directory structures using both GUI and path notation
- Understand the difference between absolute and relative paths
- Identify different file types and their purposes
- Explain file permissions and security concepts
- Organize files and folders effectively

## Prerequisites
- Understanding of operating systems from Lesson 3
- Basic computer file and folder operations
- Familiarity with common file types (documents, images, etc.)

## Materials Needed
- Computer with access to file system
- Examples of different file types
- File system diagram handouts
- Access to multiple operating systems (if available)

## Lesson Overview (45 minutes)
1. **Introduction** (5 minutes) - How do you find your files?
2. **File System Concepts** (10 minutes) - What is a file system?
3. **Directory Structure** (15 minutes) - The file system hierarchy
4. **File Types and Extensions** (10 minutes) - Understanding different files
5. **File Permissions** (5 minutes) - Who can access what?

---

## Detailed Instructions

### 1. Introduction: How Do You Find Your Files? (5 minutes)

**Discussion Starter:**
- "How do you organize your belongings at home?"
- "Where do you save your school assignments on your computer?"
- "What happens when you can't find a file you saved?"

**Analogy - The Filing Cabinet:**
A file system is like a giant filing cabinet:
- **Drawers** = Drives (C:, D:, etc.)
- **Folders** = Directories
- **Documents** = Files
- **Labels** = File names and extensions

### 2. File System Concepts (10 minutes)

#### What is a File System?

**Definition:**
A file system is a method and data structure that the operating system uses to organize and store files on a storage device. It's like a library's catalog system for your computer.

**Key Functions:**
- **Organization:** Arranges files in a logical structure
- **Storage:** Manages how files are stored on disk
- **Naming:** Provides a way to identify files uniquely
- **Security:** Controls who can access which files
- **Metadata:** Stores information about files (size, date, permissions)

**Video Resource:** [How File Systems Work](https://www.youtube.com/watch?v=KN8YgJnShPM) (8 minutes)

#### Why File Systems Matter

**Without File Systems:**
- Files would be scattered randomly on storage
- No way to organize or find files
- No file names, just memory addresses
- No security or access control

**With File Systems:**
- Organized, hierarchical structure
- Named files and folders
- Easy navigation and search
- Security and permission controls
- Efficient storage management

#### Common File Systems

**Windows:**
- **NTFS** (New Technology File System) - Modern Windows
- **FAT32** - Older Windows, USB drives
- **exFAT** - Large USB drives, cross-platform

**macOS:**
- **APFS** (Apple File System) - Modern macOS
- **HFS+** - Older macOS versions

**Linux:**
- **ext4** - Most common Linux file system
- **Btrfs** - Advanced features, snapshots
- **ZFS** - Enterprise-grade features

### 3. Directory Structure (15 minutes)

#### Hierarchical Organization

**Tree Structure:**
File systems use a tree-like structure, similar to a family tree:
- **Root** - The top-level directory
- **Branches** - Subdirectories
- **Leaves** - Individual files

**Visual Demonstration:**
```
Root Directory (/)
├── Users
│   ├── Alice
│   │   ├── Documents
│   │   ├── Pictures
│   │   └── Desktop
│   └── Bob
│       ├── Documents
│       └── Downloads
├── System
│   ├── Programs
│   └── Library
└── Applications
    ├── TextEditor
    └── Calculator
```

#### Directory Structure by Operating System

**Windows Directory Structure:**
```
C:\ (Root)
├── Users
│   └── [Username]
│       ├── Documents
│       ├── Pictures
│       ├── Desktop
│       └── Downloads
├── Program Files
├── Windows
└── temp
```

**macOS Directory Structure:**
```
/ (Root)
├── Users
│   └── [Username]
│       ├── Documents
│       ├── Pictures
│       ├── Desktop
│       └── Downloads
├── Applications
├── System
└── Library
```

**Linux Directory Structure:**
```
/ (Root)
├── home
│   └── [username]
│       ├── Documents
│       ├── Pictures
│       └── Desktop
├── bin (system programs)
├── etc (configuration files)
├── var (variable data)
└── usr (user programs)
```

#### Navigation Concepts

**Absolute Paths:**
- Start from the root directory
- Complete address to a file or folder
- **Windows:** `C:\Users\Alice\Documents\report.txt`
- **macOS/Linux:** `/Users/Alice/Documents/report.txt`

**Relative Paths:**
- Start from your current location
- Shorter, but depends on where you are
- **Examples:** `Documents/report.txt`, `../Pictures/photo.jpg`

**Special Directory Symbols:**
- `.` (dot) = Current directory
- `..` (dot dot) = Parent directory
- `~` (tilde) = Home directory (macOS/Linux)
- `/` = Root directory (macOS/Linux)
- `\` = Directory separator (Windows)

**Interactive Demo:** Navigate through file system showing absolute vs. relative paths

### 4. File Types and Extensions (10 minutes)

#### What Are File Extensions?

**Definition:**
File extensions are suffixes added to filenames to indicate the file type and format. They help the operating system know which program should open the file.

**Format:** `filename.extension`
**Examples:** `report.docx`, `photo.jpg`, `song.mp3`

#### Common File Types

**Documents:**
- `.txt` - Plain text files
- `.docx` - Microsoft Word documents
- `.pdf` - Portable Document Format
- `.rtf` - Rich Text Format

**Images:**
- `.jpg/.jpeg` - JPEG images (compressed)
- `.png` - PNG images (transparent backgrounds)
- `.gif` - Animated images
- `.bmp` - Bitmap images (uncompressed)

**Audio:**
- `.mp3` - Compressed audio
- `.wav` - Uncompressed audio
- `.flac` - Lossless audio compression

**Video:**
- `.mp4` - MPEG-4 video
- `.avi` - Audio Video Interleave
- `.mov` - QuickTime video

**Programming:**
- `.py` - Python code
- `.html` - Web pages
- `.css` - Style sheets
- `.js` - JavaScript

**Archives:**
- `.zip` - Compressed archive
- `.rar` - RAR archive
- `.7z` - 7-Zip archive

**Interactive Activity:** Show files with different extensions and discuss what programs open them

#### File Associations

**How Operating Systems Handle Files:**
1. User double-clicks a file
2. OS looks at the file extension
3. OS finds the associated program
4. OS opens the file with that program

**Changing File Associations:**
- Right-click file → "Open with" → Choose program
- Can set default programs for each file type
- Important for productivity and workflow

### 5. File Permissions and Security (5 minutes)

#### Understanding File Permissions

**Three Basic Permissions:**
- **Read (R):** Can view/open the file
- **Write (W):** Can modify the file
- **Execute (X):** Can run the file as a program

**Three Permission Groups:**
- **Owner:** The user who created the file
- **Group:** Users in the same group as the owner
- **Others:** All other users on the system

**Permission Examples:**
- **Read-only:** You can open a document but not save changes
- **Full access:** You can open, edit, and delete the file
- **No access:** You can't even see the file exists

#### Windows Permissions

**Common Permission Types:**
- **Full Control:** Can do everything
- **Modify:** Can change the file
- **Read & Execute:** Can open and run
- **Read:** Can only view
- **Write:** Can create new files but not modify existing ones

**Demonstration:** Show file properties and permission settings

#### macOS/Linux Permissions

**Permission Notation:**
- **rwx** for owner, group, others
- **Example:** `rwxr-xr--` 
  - Owner: read, write, execute
  - Group: read, execute
  - Others: read only

**Visual Representation:**
```
-rwxr-xr-- 1 alice staff 2048 Jan 15 10:30 myfile.txt
│││││││└─ others permissions (r--)
│││││└─ group permissions (r-x)
│││└─ owner permissions (rwx)
││└─ file type (- = regular file)
```

---

## Activities

### Activity 1: File System Scavenger Hunt (10 minutes)
Students navigate their computer's file system to find:
1. Their user folder/home directory
2. The Desktop folder
3. A file with a `.txt` extension
4. A folder that contains at least 5 files
5. The largest file in their Documents folder

### Activity 2: Path Writing Practice (8 minutes)
Given the following directory structure, write the absolute and relative paths:
```
C:\
├── Users
│   └── Student
│       ├── Documents
│       │   └── essay.docx
│       ├── Pictures
│       │   └── vacation.jpg
│       └── Music
│           └── song.mp3
```

**Questions:**
1. Absolute path to `essay.docx`
2. Relative path from `Pictures` to `song.mp3`
3. Relative path from `Music` to `vacation.jpg`

### Activity 3: File Extension Matching (5 minutes)
Match the file extension with its file type:
- `.mp3` → Audio file
- `.docx` → Word document
- `.jpg` → Image file
- `.py` → Python program
- `.pdf` → Portable document

### Activity 4: Permission Scenario (7 minutes)
Discuss what permissions are needed for each scenario:
1. A student needs to read a teacher's assignment handout
2. A student needs to submit homework to a shared folder
3. A system administrator needs to install new software
4. A user wants to protect their personal photos from others

---

## Assessment

### Formative Assessment
- **Navigation Skills:** Students can find files using both GUI and path notation
- **Concept Understanding:** Can explain file system hierarchy and organization
- **Permission Awareness:** Understands basic security concepts

### Practical Skills Check
1. **Navigate to your home directory**
2. **Create a new folder called "Unit2-Practice"**
3. **Find a file with a specific extension**
4. **Explain the difference between absolute and relative paths**
5. **Describe what file permissions control**

### Exit Ticket
1. What is the difference between a file and a directory?
2. Write the absolute path to your Desktop folder
3. Why are file extensions important?
4. What does "read-only" permission mean?

---

## Extensions

### For Advanced Students
- Explore hidden files and system directories
- Learn about file system journaling and recovery
- Investigate symbolic links and shortcuts
- Research different file system performance characteristics

### For Struggling Students
- Use file manager with tree view enabled
- Create physical file folders to demonstrate hierarchy
- Focus on practical navigation skills
- Use visual diagrams and analogies consistently

### Real-World Connections
- Organize a digital photo collection
- Set up a project folder structure for school work
- Explore cloud storage file synchronization
- Research digital asset management in creative industries

---

## Resources

### Educational Videos
- [File Systems Explained](https://www.youtube.com/watch?v=KN8YgJnShPM) (8 minutes)
- [Understanding File Paths](https://www.youtube.com/watch?v=BMi6lRKgRGU) (6 minutes)
- [File Permissions in Windows](https://www.youtube.com/watch?v=1s5XLo3Ka2c) (10 minutes)

### Interactive Tools
- [File System Simulator](https://www.filesystemsimulator.com/)
- [Command Line File Navigation Practice](https://cmdchallenge.com/)
- [Visual File System Explorer](https://www.cs.cmu.edu/~213/activities/filesys/)

### Documentation
- [Windows File System](https://docs.microsoft.com/en-us/windows/win32/fileio/file-systems)
- [macOS File System](https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/)
- [Linux File System Hierarchy](https://www.pathname.com/fhs/)

### Tools for Practice
- **Windows:** File Explorer, Command Prompt
- **macOS:** Finder, Terminal
- **Linux:** File Manager, Terminal
- **Cross-platform:** Visual Studio Code file explorer

---

## Homework

### Required
- Organize your computer's file system using best practices
- Create a folder structure for this course's materials
- Write a short explanation of your organizational system
- Practice writing absolute and relative paths

### Optional
- Explore a different operating system's file structure
- Research file recovery tools and how they work
- Create a file naming convention for your school projects
- Investigate cloud storage synchronization

---

## Notes for Instructors

### Preparation
- Test file system access on all available computers
- Prepare example files with different extensions
- Create practice directory structures for exercises
- Have backup activities for different OS environments

### Common Student Challenges
- **Path notation confusion** - Practice with both forward and backslashes
- **Understanding relative paths** - Use current location analogies
- **File extension visibility** - Show how to enable file extensions
- **Permission concepts** - Use real-world access control examples

### Differentiation Strategies
- **Visual learners:** Use file system diagrams and tree structures
- **Kinesthetic learners:** Have students physically navigate file systems
- **Auditory learners:** Verbally describe navigation steps
- **Advanced students:** Introduce command-line navigation early

### Assessment Tips
- Focus on conceptual understanding over memorization
- Test practical navigation skills regularly
- Check that students can explain concepts in their own words
- Ensure students understand security implications of file permissions

### Safety and Security Notes
- Remind students not to modify system files
- Emphasize the importance of backing up important files
- Discuss safe file sharing practices
- Address digital citizenship and respect for others' files
