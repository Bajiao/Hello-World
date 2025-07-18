# Activity: First Repository Project

## Overview
This hands-on activity guides students through creating their first complete Git repository project from scratch, incorporating all the skills learned in Unit 4. Students will create a personal portfolio project that demonstrates their understanding of Git fundamentals, GitHub integration, and collaborative workflows.

## Learning Objectives
- Apply the complete Git workflow to a real project
- Demonstrate proficiency with essential Git commands
- Create a well-organized repository structure
- Practice writing meaningful commit messages
- Showcase GitHub integration skills
- Collaborate effectively with peers on shared repositories

## Time Required
- **Setup:** 5 minutes
- **Individual Project:** 20 minutes
- **Collaboration:** 15 minutes
- **Reflection:** 5 minutes
- **Total:** 45 minutes

## Materials Needed
- Computer with Git and GitHub access
- Text editor (VS Code, Sublime Text, etc.)
- GitHub account (created in previous lesson)
- Internet connection for GitHub synchronization

---

## Project Structure

### Individual Project: Personal Developer Portfolio

Students will create a repository that serves as their personal developer portfolio, incorporating multiple files and demonstrating Git best practices.

#### Repository Requirements
- **Name:** `developer-portfolio`
- **Description:** "My personal developer portfolio showcasing projects and skills"
- **Structure:** Organized folders and files
- **Documentation:** Clear README and project descriptions
- **History:** Multiple meaningful commits

#### Expected File Structure
```
developer-portfolio/
├── README.md
├── about/
│   ├── bio.md
│   └── skills.md
├── projects/
│   ├── project1.md
│   └── project2.md
├── goals/
│   └── learning-goals.md
└── contact/
    └── contact-info.md
```

---

## Phase 1: Repository Setup (8 minutes)

### Step 1: Local Repository Creation
```bash
mkdir developer-portfolio
cd developer-portfolio
git init
```

### Step 2: Create Initial README
Create `README.md` with the following content:
```markdown
# My Developer Portfolio

Welcome to my personal developer portfolio! This repository showcases my learning journey, projects, and skills in programming and software development.

## About This Repository

This portfolio is organized into the following sections:
- **About:** Information about me and my skills
- **Projects:** Showcase of my programming projects
- **Goals:** My learning objectives and future plans
- **Contact:** How to reach me

## Current Status

🌱 I'm currently learning: Git, GitHub, and Python programming
🎯 My goal: Become a skilled software developer
📫 How to reach me: [Add your contact information]

## Repository Structure

```
developer-portfolio/
├── README.md
├── about/
├── projects/
├── goals/
└── contact/
```

---

*Last updated: [Current Date]*
*Created as part of Git and GitHub learning at [School Name]*
```

### Step 3: First Commit
```bash
git add README.md
git commit -m "Initial commit: Add README with portfolio structure"
```

### Step 4: Create GitHub Repository
1. Go to GitHub and create new repository
2. Name: `developer-portfolio`
3. Description: "My personal developer portfolio showcasing projects and skills"
4. Make it public
5. Don't initialize with README (we have one already)

### Step 5: Connect and Push
```bash
git remote add origin https://github.com/[your-username]/developer-portfolio.git
git push -u origin main
```

---

## Phase 2: Content Development (12 minutes)

### Step 6: Create About Section (4 minutes)

**Create about directory and bio:**
```bash
mkdir about
```

**Create `about/bio.md`:**
```markdown
# About Me

## Introduction
Hello! I'm [Your Name], a high school student passionate about learning programming and technology.

## Background
- **Grade:** [Your Grade]
- **School:** [Your School]
- **Interests:** Technology, programming, [other interests]
- **Hobbies:** [Your hobbies]

## My Journey
I started learning programming in [Month/Year] and have been fascinated by the power of code to solve problems and create amazing things. This portfolio represents my learning journey and the projects I've worked on.

## Fun Facts
- Favorite programming language (so far): [Language]
- Dream project: [Describe a project you'd like to build]
- Inspiration: [What motivates you to learn programming]

## Current Focus
Right now, I'm focusing on:
- Learning Git and version control
- Understanding fundamental programming concepts
- Building projects to apply what I learn
- Preparing for future computer science studies
```

**Create `about/skills.md`:**
```markdown
# My Skills

## Programming Languages
- **Learning:** Python, HTML, CSS
- **Familiar with:** Command line basics, Git
- **Want to learn:** JavaScript, Java, C++

## Tools and Technologies
- **Version Control:** Git, GitHub
- **Editors:** VS Code, [other editors you use]
- **Operating Systems:** [Windows/macOS/Linux]
- **Command Line:** Basic navigation and file operations

## Soft Skills
- Problem-solving
- Attention to detail
- Collaboration and teamwork
- Communication
- Continuous learning mindset

## Learning Style
- **Best learning methods:** [How you learn best]
- **Preferred resources:** [Videos, books, tutorials, etc.]
- **Practice approach:** [How you practice coding]

## Progress Tracking
- **Started learning:** [Date]
- **Current level:** Beginner
- **Next milestone:** [Your next goal]
```

**Commit the about section:**
```bash
git add about/
git commit -m "Add about section with bio and skills"
```

### Step 7: Create Projects Section (4 minutes)

**Create projects directory:**
```bash
mkdir projects
```

**Create `projects/project1.md`:**
```markdown
# Project 1: My First Git Repository

## Description
This is my first experience with Git and version control. I learned how to create repositories, track changes, and collaborate with others.

## What I Learned
- Git fundamentals (init, add, commit, push, pull)
- Repository structure and organization
- Commit message best practices
- Basic collaboration workflows

## Technologies Used
- Git for version control
- GitHub for remote repository hosting
- Command line for Git operations
- Markdown for documentation

## Challenges
- Understanding the staging area concept
- Writing meaningful commit messages
- Connecting local repositories to GitHub
- Learning command line Git operations

## Outcome
Successfully created and managed my first Git repository with multiple commits and proper documentation.

## Future Improvements
- Learn branching and merging
- Explore advanced Git features
- Practice collaborative workflows
- Integrate with development tools
```

**Create `projects/project2.md`:**
```markdown
# Project 2: Command Line Mastery

## Description
Learned essential command line skills for file navigation, manipulation, and system interaction.

## What I Learned
- File system navigation
- File and directory operations
- Command line text editing
- Basic system administration
- File permissions and security

## Technologies Used
- Terminal/Command Prompt
- Shell commands (ls, cd, mkdir, cp, mv, rm)
- Text editors (nano, vim)
- File permission system

## Challenges
- Overcoming fear of command line
- Memorizing essential commands
- Understanding file permissions
- Troubleshooting command errors

## Outcome
Became comfortable with command line operations and can navigate and manipulate files efficiently.

## Future Improvements
- Learn shell scripting
- Master advanced command line tools
- Explore system administration
- Integrate command line with programming workflows
```

**Commit the projects section:**
```bash
git add projects/
git commit -m "Add projects section with first two projects"
```

### Step 8: Create Goals Section (2 minutes)

**Create goals directory:**
```bash
mkdir goals
```

**Create `goals/learning-goals.md`:**
```markdown
# My Learning Goals

## Short-term Goals (Next 3 months)
- [ ] Master Git and GitHub workflows
- [ ] Learn Python programming fundamentals
- [ ] Build 3 small programming projects
- [ ] Understand object-oriented programming basics
- [ ] Create a personal website

## Medium-term Goals (Next 6-12 months)
- [ ] Learn web development (HTML, CSS, JavaScript)
- [ ] Understand database concepts
- [ ] Complete a significant programming project
- [ ] Contribute to an open-source project
- [ ] Build a portfolio website

## Long-term Goals (1-2 years)
- [ ] Pursue computer science in college
- [ ] Develop expertise in a specific programming area
- [ ] Create a mobile app or web application
- [ ] Mentor other students learning programming
- [ ] Participate in programming competitions

## Skills I Want to Develop
- **Technical Skills:**
  - Advanced Python programming
  - Web development frameworks
  - Database design and management
  - Software testing and debugging
  - System design and architecture

- **Soft Skills:**
  - Project management
  - Technical communication
  - Leadership and mentoring
  - Problem-solving methodologies
  - Continuous learning habits

## How I Plan to Achieve These Goals
- **Daily Practice:** Code for at least 30 minutes daily
- **Project-Based Learning:** Build real projects to apply concepts
- **Community Engagement:** Participate in programming communities
- **Formal Learning:** Take courses and complete certifications
- **Mentorship:** Seek guidance from experienced developers

## Progress Tracking
- **Monthly Reviews:** Assess progress and adjust goals
- **Project Milestones:** Complete specific projects by target dates
- **Skill Assessments:** Evaluate technical skills regularly
- **Portfolio Updates:** Keep portfolio current with new projects
```

**Commit the goals section:**
```bash
git add goals/
git commit -m "Add learning goals and development plans"
```

### Step 9: Create Contact Section (2 minutes)

**Create contact directory:**
```bash
mkdir contact
```

**Create `contact/contact-info.md`:**
```markdown
# Contact Information

## How to Reach Me

### GitHub
- **Profile:** https://github.com/[your-username]
- **Portfolio Repository:** https://github.com/[your-username]/developer-portfolio

### Email
- **School Email:** [your-school-email]
- **Personal Email:** [your-personal-email] (optional)

### Social Media
- **LinkedIn:** [your-linkedin-profile] (if applicable)
- **Twitter:** [your-twitter-handle] (if applicable)

## Collaboration
I'm interested in collaborating on:
- Learning projects with fellow students
- Open-source contributions (beginner-friendly)
- Study groups and programming meetups
- Peer code reviews and feedback

## Availability
- **Best contact method:** GitHub or email
- **Response time:** Usually within 24-48 hours
- **Collaboration time:** Weekends and evenings
- **Time zone:** [Your time zone]

## Professional Interests
- Software development internships
- Programming mentorship opportunities
- Technology conferences and workshops
- Computer science study groups

---

*Feel free to reach out if you'd like to collaborate, have questions about my projects, or want to connect with a fellow programming student!*
```

**Commit the contact section:**
```bash
git add contact/
git commit -m "Add contact information and collaboration interests"
```

---

## Phase 3: Collaboration (15 minutes)

### Step 10: Partner Exchange (5 minutes)

**Find a Collaboration Partner:**
1. Pair up with a classmate
2. Exchange GitHub usernames
3. Visit each other's repositories
4. Clone your partner's repository

**Clone Partner's Repository:**
```bash
cd ..
git clone https://github.com/[partner-username]/developer-portfolio.git partner-portfolio
cd partner-portfolio
```

### Step 11: Collaborative Contribution (8 minutes)

**Make a Contribution to Partner's Repository:**
1. **Create a new file:** `feedback/peer-review.md`
2. **Add feedback about their portfolio:**

```markdown
# Peer Review

**Reviewer:** [Your Name]
**Date:** [Current Date]
**Repository:** [Partner's GitHub Username]/developer-portfolio

## Overall Impression
[Write your overall thoughts about their portfolio]

## Strengths
- [List specific things you liked]
- [Mention well-organized sections]
- [Highlight clear communication]
- [Note good commit messages]

## Suggestions for Improvement
- [Offer constructive feedback]
- [Suggest additional sections]
- [Recommend formatting improvements]
- [Mention missing information]

## Favorite Section
My favorite section was [section name] because [explain why].

## Questions for the Author
1. [Ask a question about their goals]
2. [Ask about their learning process]
3. [Ask about future projects]

## Additional Comments
[Any other thoughts or encouragement]

---

*Great work on your portfolio! Keep up the excellent documentation and version control practices.*

**Reviewer's GitHub:** [Your GitHub Username]
```

**Commit and Create Pull Request:**
```bash
mkdir feedback
# Create the peer-review.md file with content above
git add feedback/
git commit -m "Add peer review feedback from [your-name]"
git push origin main
```

**Note:** In a real collaborative environment, you would create a pull request. For this exercise, we'll simulate the collaboration process.

### Step 12: Receive and Integrate Feedback (2 minutes)

**Review Your Partner's Contribution:**
1. Look at what your partner added to your repository
2. Discuss their feedback in person
3. Make any improvements suggested
4. Thank them for their contribution

**Optional: Make improvements based on feedback:**
```bash
cd ../developer-portfolio
# Make any suggested improvements
git add .
git commit -m "Improve portfolio based on peer feedback"
git push
```

---

## Phase 4: Final Polish and Reflection (5 minutes)

### Step 13: Final Repository Update

**Update README with completion status:**
```bash
# Edit README.md to add completion date and reflection
git add README.md
git commit -m "Update README with project completion and reflection"
git push
```

### Step 14: Repository Verification

**Check that your repository includes:**
- [ ] Well-organized directory structure
- [ ] Multiple meaningful commits
- [ ] Clear and informative README
- [ ] Personal information and goals
- [ ] Project descriptions
- [ ] Contact information
- [ ] Peer feedback (if applicable)

**View your complete commit history:**
```bash
git log --oneline
```

**Expected output should show multiple commits with clear messages.**

---

## Assessment Criteria

### Technical Skills (40 points)
- **Repository Setup (10 points):** Proper initialization, GitHub connection
- **Git Workflow (10 points):** Appropriate use of add, commit, push commands
- **Commit Messages (10 points):** Clear, descriptive commit messages
- **Repository Organization (10 points):** Logical file structure and organization

### Content Quality (30 points)
- **Documentation (10 points):** Clear, well-written content
- **Completeness (10 points):** All required sections included
- **Personalization (10 points):** Authentic, personal information and goals

### Collaboration (20 points)
- **Peer Interaction (10 points):** Effective collaboration with partner
- **Feedback Quality (10 points):** Constructive, helpful peer review

### Professionalism (10 points)
- **GitHub Profile (5 points):** Professional setup and presentation
- **Communication (5 points):** Clear, professional communication

### Grading Scale
- **A (90-100):** Exceptional work demonstrating mastery
- **B (80-89):** Proficient work with minor areas for improvement
- **C (70-79):** Adequate work meeting basic requirements
- **D (60-69):** Below expectations, significant improvement needed
- **F (Below 60):** Inadequate work, major revision required

---

## Extensions and Variations

### For Advanced Students
- **Advanced Git Features:** Explore branching and merging
- **GitHub Pages:** Create a live website from the repository
- **Advanced Markdown:** Use more sophisticated formatting
- **Automation:** Set up GitHub Actions for automated tasks

### For Struggling Students
- **Simplified Structure:** Focus on fewer files and sections
- **Template Approach:** Provide more detailed templates
- **Pair Programming:** Work closely with a partner throughout
- **Visual Aids:** Use diagrams and flowcharts for Git concepts

### Creative Extensions
- **Portfolio Website:** Convert to HTML/CSS website
- **Video Documentation:** Create video presentations
- **Interactive Elements:** Add interactive components
- **Multi-language Support:** Include content in multiple languages

---

## Reflection Questions

### Individual Reflection
1. **Technical Growth:** What Git skills do you feel most confident about now?
2. **Challenges:** What was the most difficult part of this project?
3. **Collaboration:** How did working with a partner enhance your learning?
4. **Professional Development:** How will this portfolio help your future goals?
5. **Next Steps:** What would you like to add or improve in your portfolio?

### Group Discussion
1. **Best Practices:** What commit message patterns worked best?
2. **Organization:** How did different people organize their repositories?
3. **Collaboration:** What made peer review most effective?
4. **GitHub Features:** What GitHub features were most useful?
5. **Future Applications:** How will you use Git and GitHub in future projects?

---

## Resources for Extension

### GitHub Learning Resources
- [GitHub Learning Lab](https://lab.github.com/)
- [GitHub Pages Guide](https://pages.github.com/)
- [Markdown Guide](https://www.markdownguide.org/)
- [Git Branching Tutorial](https://learngitbranching.js.org/)

### Portfolio Development
- [Developer Portfolio Examples](https://github.com/topics/portfolio)
- [README Template Collection](https://github.com/othneildrew/Best-README-Template)
- [Professional GitHub Profile Examples](https://github.com/abhisheknaiidu/awesome-github-profile-readme)

### Advanced Git Topics
- [Git Branching Strategies](https://nvie.com/posts/a-successful-git-branching-model/)
- [Advanced Git Commands](https://www.atlassian.com/git/tutorials/advanced-overview)
- [Git Hooks](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)

---

## Instructor Notes

### Preparation
- **Test Environment:** Ensure all students have GitHub accounts
- **Time Management:** Monitor progress and adjust pacing
- **Pair Assignment:** Strategically pair students for collaboration
- **Technical Support:** Be ready to help with authentication issues

### Common Challenges
- **Authentication:** GitHub password/token confusion
- **Merge Conflicts:** When multiple people edit same files
- **File Organization:** Helping students structure repositories logically
- **Commit Messages:** Encouraging meaningful descriptions

### Success Indicators
- **Active Git Usage:** Students using Git commands confidently
- **Quality Documentation:** Clear, well-written repository content
- **Effective Collaboration:** Constructive peer feedback and interaction
- **Professional Presentation:** Repositories that look polished and organized

### Assessment Tips
- **Process Over Product:** Focus on Git workflow mastery
- **Peer Learning:** Encourage students to learn from each other
- **Real-world Connection:** Emphasize professional portfolio development
- **Continuous Improvement:** Treat this as a living document that will grow

This activity serves as a capstone for Unit 4, allowing students to demonstrate their Git and GitHub skills while creating something valuable for their future academic and professional development.
