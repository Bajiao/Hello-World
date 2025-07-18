# Assessment: Unit 4 Portfolio Project

## Overview
This comprehensive assessment evaluates students' mastery of Git and GitHub through a complete portfolio project. Students will demonstrate their ability to use version control effectively, collaborate with peers, and present their work professionally. This assessment serves as both a learning tool and a foundation for future development work.

## Assessment Components
- **Part A:** Technical Git Skills (40 points)
- **Part B:** Repository Organization and Documentation (30 points)
- **Part C:** Collaboration and Peer Review (20 points)
- **Part D:** Professional Presentation (10 points)
- **Total:** 100 points

## Time Allocation
- **Project Development:** 45 minutes
- **Peer Collaboration:** 30 minutes
- **Portfolio Presentation:** 15 minutes
- **Total:** 90 minutes

## Materials Needed
- Computer with Git and GitHub access
- GitHub account (previously created)
- Text editor for file creation
- Internet connection for GitHub synchronization

---

## Part A: Technical Git Skills (40 points)

### A1: Repository Setup and Configuration (10 points)

**Required Tasks:**
1. Create a new repository called `unit4-portfolio`
2. Initialize local Git repository
3. Configure proper Git user information
4. Connect local repository to GitHub remote
5. Verify remote connection

**Assessment Criteria:**
- **Excellent (9-10 points):** Flawless setup with proper configuration
- **Good (7-8 points):** Setup complete with minor configuration issues
- **Adequate (5-6 points):** Basic setup working but missing some configuration
- **Needs Improvement (0-4 points):** Setup incomplete or non-functional

**Verification Commands:**
```bash
git config --list
git remote -v
git status
```

### A2: Commit History and Workflow (15 points)

**Required Demonstrations:**
1. Create initial commit with README
2. Make at least 5 meaningful commits
3. Use proper staging area workflow
4. Demonstrate understanding of working directory vs staging vs repository
5. Show ability to review commit history

**Assessment Criteria:**
- **Excellent (13-15 points):** Clean commit history with meaningful messages
- **Good (10-12 points):** Good commit history with mostly clear messages
- **Adequate (7-9 points):** Adequate commits but some unclear messages
- **Needs Improvement (0-6 points):** Poor commit history or unclear workflow

**Evaluation Elements:**
- Commit message quality and clarity
- Appropriate use of staging area
- Logical progression of commits
- Proper file organization

### A3: GitHub Integration (15 points)

**Required Tasks:**
1. Push local repository to GitHub
2. Make changes directly on GitHub
3. Pull remote changes to local repository
4. Demonstrate push/pull workflow
5. Show ability to resolve basic sync issues

**Assessment Criteria:**
- **Excellent (13-15 points):** Seamless GitHub integration and workflow
- **Good (10-12 points):** Good GitHub usage with minor issues
- **Adequate (7-9 points):** Basic GitHub functionality working
- **Needs Improvement (0-6 points):** Significant GitHub integration problems

**Verification Points:**
- Repository visible and accessible on GitHub
- Local and remote repositories synchronized
- Changes flow correctly between local and remote
- Understanding of push/pull workflow

---

## Part B: Repository Organization and Documentation (30 points)

### B1: Repository Structure (10 points)

**Required Structure:**
```
unit4-portfolio/
├── README.md
├── about/
│   ├── personal-info.md
│   └── technical-skills.md
├── projects/
│   ├── git-learning-project.md
│   └── future-projects.md
├── reflections/
│   └── git-learning-reflection.md
└── resources/
    └── git-resources.md
```

**Assessment Criteria:**
- **Excellent (9-10 points):** Well-organized, logical structure
- **Good (7-8 points):** Good organization with minor issues
- **Adequate (5-6 points):** Basic organization but could be clearer
- **Needs Improvement (0-4 points):** Poor or confusing organization

### B2: Documentation Quality (20 points)

**Required Documentation:**

#### README.md (5 points)
Must include:
- Project title and description
- Repository structure explanation
- Contact information
- Last updated date

#### Personal Information (5 points)
- `about/personal-info.md`: Background, interests, goals
- `about/technical-skills.md`: Current skills and learning objectives

#### Project Documentation (5 points)
- `projects/git-learning-project.md`: Description of Git learning journey
- `projects/future-projects.md`: Planned projects and applications

#### Reflection (5 points)
- `reflections/git-learning-reflection.md`: Thoughtful reflection on learning process

**Assessment Criteria:**
- **Excellent (18-20 points):** Clear, comprehensive, well-written documentation
- **Good (14-17 points):** Good documentation with minor clarity issues
- **Adequate (10-13 points):** Basic documentation meeting requirements
- **Needs Improvement (0-9 points):** Inadequate or unclear documentation

---

## Part C: Collaboration and Peer Review (20 points)

### C1: Peer Repository Review (10 points)

**Required Tasks:**
1. Clone a classmate's repository
2. Review their project structure and documentation
3. Create a detailed peer review document
4. Provide constructive feedback and suggestions
5. Submit peer review as part of assessment

**Peer Review Template:**
```markdown
# Peer Review

**Reviewer:** [Your Name]
**Repository Reviewed:** [Classmate's GitHub Username]/unit4-portfolio
**Review Date:** [Current Date]

## Repository Structure
- [Evaluate organization and clarity]
- [Note strengths and areas for improvement]

## Documentation Quality
- [Assess clarity and completeness]
- [Highlight well-written sections]
- [Suggest improvements]

## Technical Implementation
- [Review Git usage and commit history]
- [Evaluate GitHub integration]
- [Note best practices observed]

## Suggestions for Improvement
1. [Specific suggestion]
2. [Another suggestion]
3. [Additional recommendation]

## Overall Assessment
[Provide overall impression and encouragement]
```

**Assessment Criteria:**
- **Excellent (9-10 points):** Thorough, constructive, helpful review
- **Good (7-8 points):** Good review with useful feedback
- **Adequate (5-6 points):** Basic review meeting requirements
- **Needs Improvement (0-4 points):** Superficial or unhelpful review

### C2: Collaboration Skills (10 points)

**Demonstrated Through:**
1. Quality of peer review provided
2. Response to feedback received
3. Participation in collaborative activities
4. Communication during group work
5. Willingness to help others

**Assessment Criteria:**
- **Excellent (9-10 points):** Outstanding collaboration and communication
- **Good (7-8 points):** Good collaboration with minor issues
- **Adequate (5-6 points):** Basic collaboration skills demonstrated
- **Needs Improvement (0-4 points):** Poor collaboration or communication

---

## Part D: Professional Presentation (10 points)

### D1: GitHub Profile and Repository Presentation (5 points)

**Evaluation Criteria:**
- Professional GitHub profile setup
- Repository appears polished and well-maintained
- Appropriate use of Markdown formatting
- Clear navigation and structure

### D2: Verbal Presentation (5 points)

**Presentation Requirements:**
- 3-minute presentation of portfolio
- Explanation of Git workflow used
- Discussion of challenges and solutions
- Demonstration of key repository features

**Assessment Criteria:**
- **Excellent (5 points):** Clear, confident, engaging presentation
- **Good (4 points):** Good presentation with minor issues
- **Adequate (3 points):** Basic presentation meeting requirements
- **Needs Improvement (0-2 points):** Poor or incomplete presentation

---

## Detailed Assessment Instructions

### Phase 1: Repository Development (45 minutes)

#### Setup and Initial Commit (10 minutes)
1. **Create local repository:**
   ```bash
   mkdir unit4-portfolio
   cd unit4-portfolio
   git init
   ```

2. **Create and commit README:**
   ```bash
   # Create README.md with project description
   git add README.md
   git commit -m "Initial commit: Add README with project overview"
   ```

3. **Create GitHub repository and connect:**
   ```bash
   # Create repository on GitHub
   git remote add origin https://github.com/[username]/unit4-portfolio.git
   git push -u origin main
   ```

#### Content Development (30 minutes)
Students work through creating all required files and directories, making commits for each major addition.

#### Final Polish (5 minutes)
Review repository, make final improvements, and ensure all requirements are met.

### Phase 2: Peer Collaboration (30 minutes)

#### Partner Assignment (5 minutes)
- Students are paired for peer review
- Exchange GitHub usernames
- Plan collaboration approach

#### Repository Review (15 minutes)
- Clone partner's repository
- Thoroughly review structure and content
- Take notes for peer review document

#### Peer Review Creation (10 minutes)
- Write comprehensive peer review
- Focus on constructive feedback
- Include specific suggestions for improvement

### Phase 3: Presentations (15 minutes)

#### Individual Presentations (12 minutes)
- 3 minutes per student
- Focus on Git workflow and repository highlights
- Encourage questions and discussion

#### Wrap-up Discussion (3 minutes)
- Share key learnings
- Discuss best practices observed
- Address any remaining questions

---

## Grading Rubric

### Exemplary (A: 90-100 points)
- **Technical Mastery:** Demonstrates complete understanding of Git and GitHub
- **Documentation:** Clear, comprehensive, professional documentation
- **Collaboration:** Exceptional peer review and collaboration skills
- **Presentation:** Confident, engaging presentation with clear explanations

### Proficient (B: 80-89 points)
- **Technical Competence:** Shows solid understanding with minor gaps
- **Documentation:** Good documentation with minor areas for improvement
- **Collaboration:** Effective collaboration with constructive feedback
- **Presentation:** Clear presentation with good explanations

### Developing (C: 70-79 points)
- **Technical Understanding:** Basic understanding with some confusion
- **Documentation:** Adequate documentation meeting basic requirements
- **Collaboration:** Basic collaboration skills demonstrated
- **Presentation:** Adequate presentation with some unclear points

### Beginning (D: 60-69 points)
- **Technical Struggles:** Limited understanding with significant gaps
- **Documentation:** Minimal documentation, often unclear
- **Collaboration:** Limited collaboration effectiveness
- **Presentation:** Unclear or incomplete presentation

### Inadequate (F: Below 60 points)
- **Technical Deficiency:** Insufficient understanding of core concepts
- **Documentation:** Inadequate or missing documentation
- **Collaboration:** Poor or absent collaboration
- **Presentation:** Unable to present or explain work

---

## Assessment Templates

### Student Self-Assessment Checklist

**Before Submitting:**
- [ ] Repository properly initialized and connected to GitHub
- [ ] At least 5 meaningful commits with clear messages
- [ ] All required files and directories created
- [ ] README.md complete and informative
- [ ] All documentation sections filled out thoughtfully
- [ ] Peer review completed and submitted
- [ ] Repository appears professional and well-organized
- [ ] Prepared for 3-minute presentation

### Instructor Evaluation Form

**Student Name:** ___________________
**GitHub Username:** ___________________
**Repository URL:** ___________________

#### Technical Skills (40 points)
- **Repository Setup:** ___/10
- **Commit History:** ___/15
- **GitHub Integration:** ___/15

#### Organization and Documentation (30 points)
- **Repository Structure:** ___/10
- **Documentation Quality:** ___/20

#### Collaboration (20 points)
- **Peer Review:** ___/10
- **Collaboration Skills:** ___/10

#### Presentation (10 points)
- **GitHub Profile:** ___/5
- **Verbal Presentation:** ___/5

**Total Score:** ___/100

**Comments:**
_________________________________
_________________________________
_________________________________

---

## Accommodations and Modifications

### For Students with Disabilities
- **Extended Time:** Additional 30 minutes if needed
- **Alternative Formats:** Audio recordings instead of written documentation
- **Assistive Technology:** Screen readers, voice recognition software
- **Modified Presentation:** Written summary instead of verbal presentation

### For English Language Learners
- **Bilingual Support:** Allow native language documentation with English summaries
- **Extended Time:** Additional time for writing and presentation
- **Visual Aids:** Provide templates and examples
- **Peer Support:** Pair with fluent English speakers

### For Struggling Students
- **Simplified Requirements:** Focus on core Git concepts
- **Template Support:** Provide detailed templates for documentation
- **Step-by-Step Guides:** Break down complex tasks into smaller steps
- **Additional Support:** One-on-one assistance during assessment

### For Advanced Students
- **Extended Requirements:** Additional features like branching or GitHub Actions
- **Peer Mentoring:** Help struggling classmates while completing assessment
- **Advanced Topics:** Explore more complex Git features
- **Leadership Role:** Lead group discussions and presentations

---

## Post-Assessment Activities

### Immediate Feedback (10 minutes)
- **Quick Discussion:** What went well and what was challenging?
- **Peer Appreciation:** Students thank their collaboration partners
- **Technical Issues:** Address any problems encountered
- **Next Steps:** Preview upcoming Python programming unit

### Individual Conferences (Optional)
- **Portfolio Review:** One-on-one discussion of student work
- **Growth Planning:** Identify areas for continued development
- **Career Connections:** Discuss how Git skills apply to future goals
- **Resource Sharing:** Provide additional learning resources

### Follow-up Projects
- **Portfolio Enhancement:** Continue developing the portfolio repository
- **Open Source Exploration:** Find beginner-friendly open source projects
- **Advanced Git Learning:** Explore branching, merging, and advanced features
- **Integration Practice:** Use Git for upcoming programming projects

---

## Resources for Students

### Git and GitHub References
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [GitHub Hello World](https://guides.github.com/activities/hello-world/)
- [Markdown Guide](https://www.markdownguide.org/)

### Portfolio Development
- [README Templates](https://github.com/othneildrew/Best-README-Template)
- [GitHub Profile Examples](https://github.com/abhisheknaiidu/awesome-github-profile-readme)
- [Developer Portfolio Inspiration](https://github.com/topics/portfolio)

### Collaboration Tools
- [Code Review Guidelines](https://google.github.io/eng-practices/review/)
- [Effective Feedback Strategies](https://www.atlassian.com/blog/git/written-unwritten-guide-pull-requests)

---

## Instructor Resources

### Preparation Materials
- [Assessment Rubric Printouts](link-to-printable-rubric)
- [Student Checklist Handouts](link-to-checklist)
- [Technical Troubleshooting Guide](link-to-troubleshooting)

### Grading Efficiency
- **Batch Review:** Use GitHub's interface to quickly review multiple repositories
- **Automated Checks:** Scripts to verify repository structure and requirements
- **Peer Review Integration:** Use student peer reviews to inform grading
- **Portfolio Tracking:** Maintain spreadsheet of student repositories and progress

### Professional Development
- **Industry Connections:** Invite professionals to review student portfolios
- **Best Practices:** Share current industry version control practices
- **Tool Updates:** Stay current with Git and GitHub feature updates
- **Pedagogy Research:** Explore research on teaching version control effectively

This comprehensive assessment provides a thorough evaluation of students' Git and GitHub skills while creating a valuable portfolio that they can continue to develop throughout their programming education.
