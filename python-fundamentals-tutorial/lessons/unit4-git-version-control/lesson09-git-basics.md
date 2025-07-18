# Lesson 9: Git Basics

## Learning Objectives
By the end of this lesson, students will be able to:
- Install and configure Git on their computer
- Initialize a new Git repository
- Understand the Git workflow (working directory, staging area, repository)
- Use basic Git commands (add, commit, status, log)
- Write meaningful commit messages
- Navigate Git history and understand repository status
- Create and manage local repositories effectively

## Prerequisites
- Completed Lesson 8: Version Control Concepts
- Familiarity with command line interface
- Basic text editor skills
- Administrative access to install software

## Materials Needed
- Computer with internet access
- Administrative privileges for software installation
- Text editor (VS Code, Sublime Text, or similar)
- Git installation files (downloaded beforehand if possible)

## Lesson Overview (50 minutes)
1. **Git Installation and Setup** (15 minutes)
2. **Understanding Git Workflow** (10 minutes)
3. **Creating Your First Repository** (10 minutes)
4. **Basic Git Commands** (10 minutes)
5. **Practice and Troubleshooting** (5 minutes)

---

## Detailed Instructions

### 1. Git Installation and Setup (15 minutes)

#### Installing Git

**Windows Users:**
1. **Download Git:**
   - Go to [git-scm.com](https://git-scm.com/)
   - Click "Download for Windows"
   - Run the installer

2. **Installation Options:**
   - **Default editor:** Choose your preferred editor (VS Code recommended)
   - **PATH environment:** "Git from the command line and also from 3rd-party software"
   - **HTTPS transport:** Use the OpenSSL library
   - **Line ending conversions:** Checkout Windows-style, commit Unix-style
   - **Terminal emulator:** Use MinTTY
   - **Git credential manager:** Install the Git Credential Manager

3. **Verify Installation:**
   ```bash
   git --version
   ```

**macOS Users:**
1. **Option 1: Homebrew (Recommended)**
   ```bash
   # Install Homebrew if not already installed
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # Install Git
   brew install git
   ```

2. **Option 2: Download from Website**
   - Go to [git-scm.com](https://git-scm.com/)
   - Click "Download for macOS"
   - Run the installer

3. **Verify Installation:**
   ```bash
   git --version
   ```

**Linux Users:**
1. **Ubuntu/Debian:**
   ```bash
   sudo apt update
   sudo apt install git
   ```

2. **CentOS/RHEL:**
   ```bash
   sudo yum install git
   ```

3. **Verify Installation:**
   ```bash
   git --version
   ```

#### Initial Git Configuration

**Set Your Identity:**
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

**Set Default Editor:**
```bash
git config --global core.editor "code --wait"  # VS Code
# or
git config --global core.editor "nano"         # Nano
# or 
git config --global core.editor "vim"          # Vim
```

**Set Default Branch Name:**
```bash
git config --global init.defaultBranch main
```

**View Configuration:**
```bash
git config --list
git config user.name
git config user.email
```

#### Configuration Explanation

**Why Set User Name and Email?**
- Every Git commit requires author information
- Shows who made each change
- Important for collaboration and accountability

**Global vs. Local Configuration:**
- **Global:** Applies to all repositories on your computer
- **Local:** Applies only to current repository
- Local settings override global settings

**Configuration File Locations:**
- **Global:** `~/.gitconfig`
- **Local:** `.git/config` (inside repository)

### 2. Understanding Git Workflow (10 minutes)

#### The Three States

**Working Directory:**
- Files in your project folder
- Where you edit and create files
- Changes are not tracked until staged

**Staging Area (Index):**
- Files prepared for the next commit
- Allows you to choose which changes to include
- Like a "draft" of your next commit

**Repository (.git directory):**
- Contains all committed history
- Permanent record of your project
- Each commit is a snapshot of your project

#### Visual Workflow

```
Working Directory    Staging Area    Repository
    [file.txt]  -->  [file.txt]  -->  [commit]
    (modified)        (staged)        (committed)
```

#### Git Workflow Steps

1. **Edit Files:** Make changes in working directory
2. **Stage Changes:** Add files to staging area
3. **Commit Changes:** Save snapshot to repository
4. **Repeat:** Continue the cycle

#### File States in Git

**Untracked:**
- New files not yet tracked by Git
- Git doesn't know about these files
- Won't be included in commits

**Modified:**
- Tracked files that have been changed
- Changes exist in working directory
- Not yet staged for commit

**Staged:**
- Files added to staging area
- Ready for next commit
- Changes will be included in commit

**Committed:**
- Files saved in repository
- Snapshot preserved in history
- Safe and permanent

### 3. Creating Your First Repository (10 minutes)

#### Creating a New Repository

**Step 1: Create Project Directory**
```bash
mkdir my-first-repo
cd my-first-repo
```

**Step 2: Initialize Git Repository**
```bash
git init
```

**What Happens:**
- Creates hidden `.git` directory
- Contains all Git metadata and history
- Transforms folder into Git repository

**Step 3: Check Repository Status**
```bash
git status
```

**Expected Output:**
```
On branch main
No commits yet
nothing to commit (create/copy files and use "git add" to track)
```

#### Creating Your First File

**Step 4: Create a File**
```bash
echo "# My First Repository" > README.md
```

**Or use a text editor:**
```bash
code README.md  # VS Code
nano README.md  # Nano
```

**Step 5: Check Status Again**
```bash
git status
```

**Expected Output:**
```
On branch main
No commits yet
Untracked files:
  (use "git add <file>..." to include in what will be committed)
        README.md

nothing added to commit but untracked files present (use "git add" to track)
```

### 4. Basic Git Commands (10 minutes)

#### Adding Files to Staging Area

**Add Single File:**
```bash
git add README.md
```

**Add All Files:**
```bash
git add .
```

**Add Multiple Specific Files:**
```bash
git add file1.txt file2.txt
```

**Check Status After Adding:**
```bash
git status
```

**Expected Output:**
```
On branch main
No commits yet
Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
        new file:   README.md
```

#### Making Your First Commit

**Commit with Message:**
```bash
git commit -m "Initial commit: Add README file"
```

**Expected Output:**
```
[main (root-commit) a1b2c3d] Initial commit: Add README file
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

**Check Status After Commit:**
```bash
git status
```

**Expected Output:**
```
On branch main
nothing to commit, working tree clean
```

#### Viewing Git History

**View Commit History:**
```bash
git log
```

**Expected Output:**
```
commit a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0 (HEAD -> main)
Author: Your Name <your.email@example.com>
Date:   Wed Nov 15 10:30:00 2023 -0800

    Initial commit: Add README file
```

**Compact History:**
```bash
git log --oneline
```

**Expected Output:**
```
a1b2c3d Initial commit: Add README file
```

#### Making More Changes

**Edit the File:**
```bash
echo "This is my first Git repository!" >> README.md
```

**Check Status:**
```bash
git status
```

**Expected Output:**
```
On branch main
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   README.md
```

**Stage and Commit:**
```bash
git add README.md
git commit -m "Add description to README"
```

**View Updated History:**
```bash
git log --oneline
```

**Expected Output:**
```
b2c3d4e Add description to README
a1b2c3d Initial commit: Add README file
```

#### Essential Git Commands Summary

| Command | Purpose | Example |
|---------|---------|---------|
| `git init` | Initialize repository | `git init` |
| `git status` | Check repository status | `git status` |
| `git add` | Stage files for commit | `git add filename.txt` |
| `git commit` | Save changes to repository | `git commit -m "message"` |
| `git log` | View commit history | `git log --oneline` |

### 5. Practice and Troubleshooting (5 minutes)

#### Guided Practice Exercise

**Students complete this sequence:**

1. **Create a new file:**
   ```bash
   echo "Hello, Git!" > hello.txt
   ```

2. **Check status:**
   ```bash
   git status
   ```

3. **Stage the file:**
   ```bash
   git add hello.txt
   ```

4. **Check status again:**
   ```bash
   git status
   ```

5. **Commit the file:**
   ```bash
   git commit -m "Add hello.txt file"
   ```

6. **View history:**
   ```bash
   git log --oneline
   ```

#### Common Issues and Solutions

**Problem:** `git: command not found`
**Solution:** Git is not installed or not in PATH. Reinstall or add to PATH.

**Problem:** `fatal: not a git repository`
**Solution:** You're not in a Git repository. Run `git init` or navigate to repo folder.

**Problem:** `Please tell me who you are`
**Solution:** Set user name and email with `git config --global user.name` and `git config --global user.email`.

**Problem:** Commit message editor opens
**Solution:** Either write message and save, or use `git commit -m "message"` to avoid editor.

---

## Activities

### Activity 1: Repository Setup Practice (15 minutes)

**Instructions:** Students work individually to create a practice repository.

**Task Steps:**
1. Create a new directory called "practice-repo"
2. Initialize it as a Git repository
3. Create a file called "about.txt" with information about yourself
4. Add and commit the file
5. Create another file called "goals.txt" with your learning goals
6. Add and commit the second file
7. View the commit history

**Verification Commands:**
```bash
git status
git log --oneline
```

### Activity 2: Commit Message Practice (10 minutes)

**Instructions:** Review these commit messages and discuss what makes them good or bad.

**Good Commit Messages:**
- "Add user authentication system"
- "Fix bug in login validation"
- "Update README with installation instructions"
- "Remove deprecated API endpoints"

**Bad Commit Messages:**
- "stuff"
- "changes"
- "fix"
- "asdf"
- "Update"

**Discussion Questions:**
1. What makes a commit message helpful?
2. How would you improve the bad examples?
3. What information should be included in commit messages?

**Best Practices:**
- Use present tense ("Add" not "Added")
- Be specific about what changed
- Keep first line under 50 characters
- Explain why if it's not obvious

### Activity 3: Git Workflow Simulation (10 minutes)

**Instructions:** Work in pairs to simulate the Git workflow.

**Role A: Developer**
- Creates files and makes changes
- Stages and commits changes
- Explains each step to partner

**Role B: Observer**
- Watches the process
- Asks questions about each step
- Helps with troubleshooting

**Scenario:**
1. Create a simple text file about your favorite hobby
2. Add and commit the file
3. Make changes to the file
4. Stage and commit the changes
5. View the history together

**Switch roles and repeat with different content.**

---

## Assessment

### Formative Assessment

**Practical Demonstration:**
Students demonstrate competency by:
1. **Installation:** Git is properly installed and configured
2. **Repository Creation:** Can initialize a new repository
3. **File Management:** Can add files to staging area
4. **Commits:** Can create commits with meaningful messages
5. **History:** Can view and understand commit history

**Quick Check Commands:**
```bash
git --version          # Verify installation
git config --list      # Check configuration
git status            # Show repository status
git log --oneline     # Display commit history
```

### Practical Skills Assessment

**Required Skills:**
1. **Configure Git:** Set user name and email
2. **Initialize Repository:** Create new Git repository
3. **Basic Workflow:** Add, commit, and check status
4. **Commit Messages:** Write clear, descriptive messages
5. **History Navigation:** View and understand commit log

**Assessment Rubric:**
- **Proficient (3):** Can complete all tasks independently
- **Developing (2):** Can complete tasks with minimal guidance
- **Beginning (1):** Requires significant help with most tasks

### Exit Ticket

**Quick Questions:**
1. What command initializes a new Git repository?
2. What are the three states of Git workflow?
3. How do you stage a file for commit?
4. What makes a good commit message?
5. How do you view your commit history?

---

## Extensions

### For Advanced Students

**Advanced Git Commands:**
- `git diff` - See changes between versions
- `git restore` - Discard changes in working directory
- `git reset` - Unstage files or reset commits
- `git show` - View details of specific commits

**Branching Preview:**
- Learn about Git branches
- Create and switch between branches
- Understand merge concepts

**Configuration Exploration:**
- Explore Git aliases for common commands
- Learn about `.gitignore` files
- Investigate Git hooks

### For Struggling Students

**Simplified Workflow:**
- Focus on just `add`, `commit`, `status`, `log`
- Use GUI tools alongside command line
- Create visual aids for the workflow
- Practice with guided exercises

**Troubleshooting Support:**
- Provide common error solutions
- Use pair programming approach
- Create step-by-step checklists
- Offer additional practice time

### Cross-Curricular Applications

**Writing Projects:**
- Use Git for essay drafts and revisions
- Track changes in research papers
- Manage collaborative writing projects

**Creative Projects:**
- Version control for digital artwork
- Track changes in video editing projects
- Manage website development

**Science and Math:**
- Version control for data analysis scripts
- Track changes in lab procedures
- Manage collaborative research

---

## Resources

### Official Documentation
- [Git Documentation](https://git-scm.com/doc)
- [Git Tutorial](https://git-scm.com/docs/gittutorial)
- [Pro Git Book](https://git-scm.com/book) - Free online book

### Interactive Tutorials
- [Learn Git Branching](https://learngitbranching.js.org/)
- [Git-it Tutorial](https://github.com/jlord/git-it-electron)
- [Codecademy Git Course](https://www.codecademy.com/learn/learn-git)

### Video Resources
- [Git Basics Playlist](https://www.youtube.com/playlist?list=PLg7s6cbtAD15G8lNyoaYDuKZSKyJrgwB-)
- [Git Tutorial for Beginners](https://www.youtube.com/watch?v=8JJ101D3knE)
- [Git Workflow Explanation](https://www.youtube.com/watch?v=3a2x1iJFJWc)

### Cheat Sheets
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [Atlassian Git Cheat Sheet](https://www.atlassian.com/git/tutorials/atlassian-git-cheatsheet)

### Practice Platforms
- [GitHub Learning Lab](https://lab.github.com/)
- [GitKraken Learn Git](https://www.gitkraken.com/learn/git)
- [Learn Git with Bitbucket Cloud](https://www.atlassian.com/git/tutorials/learn-git-with-bitbucket-cloud)

---

## Homework

### Required Practice
1. **Personal Repository:** Create a Git repository for a personal project
2. **Daily Commits:** Make at least one commit per day for the next week
3. **Commit Messages:** Practice writing clear, descriptive commit messages
4. **Command Practice:** Use Git commands from memory without reference

### Creative Assignment
**Git Journal Project:**
- Create a repository for a daily journal
- Write a short entry each day
- Commit each entry with a descriptive message
- After one week, review your commit history

### Reflection Questions
1. What was most challenging about learning Git commands?
2. How do you think Git will help you in future projects?
3. What questions do you still have about Git?
4. How does the Git workflow compare to how you currently manage files?

### Preparation for Next Class
1. **GitHub Account:** Create a free GitHub account
2. **SSH Keys:** Research SSH key setup (optional)
3. **Project Ideas:** Think of a project to share on GitHub
4. **Collaboration:** Find a classmate to practice collaboration with

---

## Notes for Instructors

### Pre-Class Preparation
- **Software Installation:** Test Git installation on all classroom computers
- **Network Access:** Ensure internet connectivity for downloads
- **User Accounts:** Prepare temporary accounts if needed
- **Backup Plans:** Have USB drives with Git installers ready

### Common Teaching Challenges
- **Installation Issues:** Different operating systems require different approaches
- **Command Line Fear:** Some students may be intimidated by terminal
- **Abstract Concepts:** Git workflow can be difficult to visualize
- **Error Messages:** Git error messages can be confusing for beginners

### Differentiation Strategies
- **Visual Learners:** Use diagrams to show Git workflow
- **Kinesthetic Learners:** Maximize hands-on practice time
- **Auditory Learners:** Encourage verbalization of commands
- **Reading/Writing Learners:** Provide written step-by-step guides

### Assessment Modifications
- **Alternative Formats:** Allow oral demonstration instead of written assessment
- **Extended Time:** Provide additional time for students who need it
- **Peer Support:** Encourage pair programming and collaboration
- **Simplified Tasks:** Focus on core concepts for struggling students

### Success Indicators
- **Confidence:** Students using Git commands without constant reference
- **Understanding:** Can explain Git workflow in their own words
- **Problem-Solving:** Attempts to resolve Git issues independently
- **Curiosity:** Questions about advanced Git features

### Safety and Best Practices
- **Backup:** Remind students to backup important work
- **Privacy:** Discuss keeping personal information out of repositories
- **Academic Integrity:** Clarify appropriate use for school assignments
- **Professional Preparation:** Emphasize industry-standard practices

### Extension Opportunities
- **Open Source:** Explore open-source projects using Git
- **Industry Connection:** Invite professionals to discuss Git usage
- **Advanced Topics:** Introduce branching and merging concepts
- **Tool Integration:** Show Git integration with IDEs and editors
