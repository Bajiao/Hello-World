# Assessment: Unit 3 Skills Check

## Overview
This comprehensive assessment evaluates students' mastery of command-line interface fundamentals, essential commands, and file permissions. The assessment combines practical demonstrations, written explanations, and problem-solving scenarios.

## Assessment Components
- **Part A:** Command Line Basics (25 points)
- **Part B:** File Operations (30 points)
- **Part C:** Permissions and Security (25 points)
- **Part D:** Problem Solving (20 points)
- **Total:** 100 points

## Time Allocation
- **Setup:** 5 minutes
- **Assessment:** 60 minutes
- **Review:** 10 minutes
- **Total:** 75 minutes

## Materials Needed
- Computer with terminal access
- Assessment files (provided)
- Answer sheet
- Command reference (if permitted)

---

## Part A: Command Line Basics (25 points)

### Question A1: Multiple Choice (10 points)
**Instructions:** Select the best answer for each question.

1. **What does CLI stand for?**
   a) Computer Language Interface
   b) Command Line Interface
   c) Control Logic Interface
   d) Common Link Interface

2. **Which command shows your current directory?**
   a) `ls`
   b) `cd`
   c) `pwd`
   d) `dir`

3. **What does the `..` directory reference represent?**
   a) Current directory
   b) Parent directory
   c) Root directory
   d) Home directory

4. **Which command creates a new directory?**
   a) `touch`
   b) `mkdir`
   c) `cd`
   d) `create`

5. **What does the `*` wildcard match?**
   a) Any single character
   b) Any number of characters
   c) Only letters
   d) Only numbers

### Question A2: Command Structure (8 points)
**Instructions:** Break down the following commands into their components.

**Example:** `ls -la Documents`
- Command: `ls`
- Options: `-la`
- Arguments: `Documents`

1. `cp -r folder1 folder2`
   - Command: _______
   - Options: _______
   - Arguments: _______

2. `chmod 755 script.sh`
   - Command: _______
   - Options: _______
   - Arguments: _______

3. `find . -name "*.txt"`
   - Command: _______
   - Options: _______
   - Arguments: _______

4. `head -n 5 file.txt`
   - Command: _______
   - Options: _______
   - Arguments: _______

### Question A3: Path Understanding (7 points)
**Instructions:** Given the directory structure below, write the correct paths.

```
/home/student/
├── Documents/
│   ├── essays/
│   │   └── final.txt
│   └── notes.txt
├── Desktop/
│   └── shortcuts/
└── Downloads/
```

**Current location:** `/home/student/Documents/essays/`

1. **Absolute path to notes.txt:** _______________________
2. **Relative path to Downloads from current location:** _______________________
3. **Relative path to shortcuts from current location:** _______________________
4. **Command to go to parent directory:** _______________________

---

## Part B: File Operations (30 points)

### Question B1: Practical Commands (20 points)
**Instructions:** You will be given a practice directory. Complete the following tasks using command line only. Write the commands you used in the spaces provided.

**Setup:** Navigate to the provided `assessment_practice` directory.

**Task 1:** Create a directory called `organized` with three subdirectories: `docs`, `images`, and `scripts`.

**Commands used:**
```
________________________________
________________________________
________________________________
```

**Task 2:** Copy all `.txt` files from the current directory to the `docs` subdirectory.

**Commands used:**
```
________________________________
```

**Task 3:** Move all `.jpg` files to the `images` subdirectory.

**Commands used:**
```
________________________________
```

**Task 4:** Create an empty file called `inventory.txt` in the `organized` directory.

**Commands used:**
```
________________________________
```

**Task 5:** Remove all files that start with "temp" from the current directory.

**Commands used:**
```
________________________________
```

### Question B2: File Viewing (10 points)
**Instructions:** Answer the following questions about file viewing commands.

1. **Which command would you use to view the first 10 lines of a file?**
   _______________________

2. **How would you view a file page by page?**
   _______________________

3. **What command shows the last 5 lines of a file called `log.txt`?**
   _______________________

4. **How would you display the contents of multiple files at once?**
   _______________________

5. **What command would you use to count the number of lines in a file?**
   _______________________

---

## Part C: Permissions and Security (25 points)

### Question C1: Permission Reading (10 points)
**Instructions:** Interpret the following permission strings.

1. **`-rw-r--r--`**
   - Owner permissions: _______________________
   - Group permissions: _______________________
   - Others permissions: _______________________

2. **`drwxr-xr-x`**
   - File type: _______________________
   - Owner permissions: _______________________
   - Group permissions: _______________________
   - Others permissions: _______________________

### Question C2: Octal Conversion (8 points)
**Instructions:** Convert between symbolic and octal notation.

1. **`rwxr-xr-x` in octal:** _______
2. **`rw-rw-r--` in octal:** _______
3. **`644` in symbolic:** _______
4. **`700` in symbolic:** _______

### Question C3: Permission Modification (7 points)
**Instructions:** Write the commands to achieve the following permission changes.

1. **Make a file executable for the owner only:**
   _______________________

2. **Give everyone read and write permissions:**
   _______________________

3. **Remove write permissions from group and others:**
   _______________________

4. **Set permissions to 755 for a directory:**
   _______________________

---

## Part D: Problem Solving (20 points)

### Scenario-Based Questions
**Instructions:** Read each scenario and provide the solution using command line commands.

### Scenario 1: File Organization (10 points)
**Situation:** You have a directory with 50 mixed files (documents, images, scripts) and need to organize them by type.

**Requirements:**
- Create separate directories for each file type
- Move files to appropriate directories
- Ensure you can verify the organization worked

**Solution (write the commands):**
```
_________________________________________________
_________________________________________________
_________________________________________________
_________________________________________________
_________________________________________________
```

### Scenario 2: Security Configuration (10 points)
**Situation:** You're setting up a shared project directory where:
- The owner needs full access
- Group members need read and execute access
- Others should have no access

**Requirements:**
- Create the directory structure
- Set appropriate permissions
- Verify the permissions are correct

**Solution (write the commands):**
```
_________________________________________________
_________________________________________________
_________________________________________________
_________________________________________________
_________________________________________________
```

---

## Practical Demonstration (Optional Bonus: 10 points)

### Live Demo Task
**Instructions:** If time permits, demonstrate the following tasks live:

1. **Navigation:** Navigate to a specific directory using both absolute and relative paths
2. **File Operations:** Create, copy, and move files
3. **Permissions:** Change file permissions and explain the changes
4. **Troubleshooting:** Resolve a common error scenario

**Grading Criteria:**
- **Confidence:** Executes commands without hesitation
- **Accuracy:** Commands work as intended
- **Explanation:** Can explain what each command does
- **Problem-solving:** Can fix errors when they occur

---

## Answer Key (For Instructors)

### Part A: Command Line Basics
**A1: Multiple Choice**
1. b) Command Line Interface
2. c) `pwd`
3. b) Parent directory
4. b) `mkdir`
5. b) Any number of characters

**A2: Command Structure**
1. Command: `cp`, Options: `-r`, Arguments: `folder1 folder2`
2. Command: `chmod`, Options: none, Arguments: `755 script.sh`
3. Command: `find`, Options: `-name`, Arguments: `. "*.txt"`
4. Command: `head`, Options: `-n 5`, Arguments: `file.txt`

**A3: Path Understanding**
1. `/home/student/Documents/notes.txt`
2. `../../Downloads`
3. `../../Desktop/shortcuts`
4. `cd ..`

### Part B: File Operations
**B1: Practical Commands**
1. `mkdir organized`, `mkdir organized/docs organized/images organized/scripts`
2. `cp *.txt organized/docs/`
3. `mv *.jpg organized/images/`
4. `touch organized/inventory.txt`
5. `rm temp*`

**B2: File Viewing**
1. `head filename` or `head -n 10 filename`
2. `less filename` or `more filename`
3. `tail -n 5 log.txt`
4. `cat file1 file2 file3`
5. `wc -l filename`

### Part C: Permissions and Security
**C1: Permission Reading**
1. Owner: read, write; Group: read; Others: read
2. File type: directory; Owner: read, write, execute; Group: read, execute; Others: read, execute

**C2: Octal Conversion**
1. 755
2. 664
3. rw-r--r--
4. rwx------

**C3: Permission Modification**
1. `chmod u+x filename`
2. `chmod 666 filename`
3. `chmod go-w filename`
4. `chmod 755 directoryname`

### Part D: Problem Solving
**Scenario 1 (Sample Solution):**
```bash
mkdir documents images scripts
mv *.txt *.doc *.pdf documents/
mv *.jpg *.png *.gif images/
mv *.sh *.py *.js scripts/
ls -la documents/ images/ scripts/
```

**Scenario 2 (Sample Solution):**
```bash
mkdir shared_project
chmod 750 shared_project
ls -la shared_project
cd shared_project
mkdir docs code resources
chmod 750 docs code resources
ls -la
```

---

## Grading Rubric

### Performance Levels
**A (90-100 points): Exemplary**
- Demonstrates mastery of all CLI concepts
- Executes commands efficiently and accurately
- Shows creative problem-solving approaches
- Explains concepts clearly

**B (80-89 points): Proficient**
- Shows solid understanding of most concepts
- Executes most commands correctly
- Demonstrates good problem-solving skills
- Minor errors in advanced topics

**C (70-79 points): Developing**
- Understands basic concepts well
- Can execute simple commands
- Shows some problem-solving ability
- Needs support with advanced topics

**D (60-69 points): Beginning**
- Shows limited understanding
- Struggles with command execution
- Requires significant guidance
- Has difficulty with basic concepts

**F (Below 60 points): Inadequate**
- Demonstrates insufficient understanding
- Cannot execute basic commands
- Unable to solve simple problems
- Requires extensive remediation

### Detailed Scoring Guide

**Part A: Command Line Basics (25 points)**
- Multiple choice: 2 points each
- Command structure: 2 points each
- Path understanding: 1-2 points per question

**Part B: File Operations (30 points)**
- Practical commands: 4 points per task
- File viewing: 2 points per question

**Part C: Permissions and Security (25 points)**
- Permission reading: 2-3 points per question
- Octal conversion: 2 points each
- Permission modification: 1-2 points per question

**Part D: Problem Solving (20 points)**
- Scenario 1: 10 points (approach + accuracy)
- Scenario 2: 10 points (approach + accuracy)

---

## Accommodations and Modifications

### For Students with Disabilities
- **Extended time:** Additional 15-30 minutes if needed
- **Alternative format:** Oral assessment option
- **Assistive technology:** Screen readers, voice recognition
- **Simplified instructions:** Break down complex tasks

### For English Language Learners
- **Bilingual dictionary:** Allow use during assessment
- **Clarification:** Provide explanation of technical terms
- **Extended time:** Additional time for reading/writing
- **Visual aids:** Diagrams and flowcharts

### For Struggling Students
- **Guided practice:** Provide sample commands
- **Reference sheets:** Allow basic command reference
- **Partial credit:** Award points for correct approaches
- **Remediation:** Offer retake opportunities

### For Advanced Students
- **Bonus challenges:** Additional complex scenarios
- **Research component:** Investigate advanced topics
- **Peer teaching:** Help struggling classmates
- **Extension projects:** Apply skills to real problems

---

## Post-Assessment Activities

### Immediate Review
- **Common errors:** Discuss frequent mistakes
- **Best practices:** Share effective strategies
- **Clarifications:** Address any confusing concepts
- **Next steps:** Preview upcoming topics

### Remediation Plan
**For students scoring below 70%:**
1. **Individual consultation:** One-on-one review
2. **Practice assignments:** Additional exercises
3. **Peer tutoring:** Pairing with successful students
4. **Retake opportunity:** After remediation work

### Enrichment Activities
**For students scoring above 90%:**
1. **Advanced topics:** Explore scripting basics
2. **Research projects:** Investigate CLI applications
3. **Teaching opportunities:** Help classmates
4. **Real-world application:** Apply skills to projects

---

## Reflection and Feedback

### Student Self-Assessment
1. **Confidence level:** How comfortable are you with CLI now?
2. **Skill gaps:** What areas need more practice?
3. **Practical application:** How will you use these skills?
4. **Learning strategies:** What helped you learn best?

### Instructor Reflection
1. **Assessment quality:** Did questions measure intended skills?
2. **Difficulty level:** Was the assessment appropriately challenging?
3. **Time allocation:** Was sufficient time provided?
4. **Student performance:** What patterns emerged in responses?

### Course Improvement
1. **Lesson adjustments:** What topics need more coverage?
2. **Activity modifications:** Which exercises were most effective?
3. **Assessment changes:** How can future assessments improve?
4. **Resource needs:** What additional materials would help?
