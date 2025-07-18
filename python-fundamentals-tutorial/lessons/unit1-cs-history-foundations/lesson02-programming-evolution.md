# Lesson 2: Programming Evolution

## Learning Objectives
By the end of this lesson, students will be able to:
- Understand the progression from machine code to high-level programming languages
- Explain the advantages of different programming paradigms
- Identify key programming languages and their purposes
- Understand why Python was chosen for this course

## Prerequisites
- Basic understanding of computer history (Lesson 1)
- Familiarity with the concept of giving instructions to machines

## Materials Needed
- Computer with internet access
- Simple text editor (Notepad, TextEdit)
- Access to online Python interpreter (repl.it or similar)

## Lesson Overview (45 minutes)
1. **Introduction** (5 minutes) - What is programming?
2. **Machine Code and Assembly** (10 minutes) - Speaking the computer's language
3. **High-Level Languages** (15 minutes) - Making programming accessible
4. **Modern Programming Languages** (10 minutes) - Today's tools
5. **Why Python?** (5 minutes) - Our choice for learning

---

## Detailed Instructions

### 1. Introduction: What is Programming? (5 minutes)

**Discussion Starter:**
- "How do you give instructions to a computer?"
- "What language do computers understand?"

**Key Concepts:**
- **Programming:** Writing instructions for computers to follow
- **Programming Language:** A way to communicate with computers
- **Evolution:** Languages have become more human-friendly over time

### 2. Machine Code and Assembly (10 minutes)

#### Machine Code (1940s)
- **What it is:** Binary code (0s and 1s) that computers directly understand
- **Example:** `10110000 01100001` (means "load the value 97 into register")
- **Challenge:** Very difficult for humans to read and write

**Visual Example:**
```
Machine Code:    10110000 01100001
What it means:   Load 97 into register A
```

#### Assembly Language (1950s)
- **Innovation:** Used words instead of just numbers
- **Example:** `MOV A, 97` (same instruction as above)
- **Advantage:** Easier for humans to understand
- **Limitation:** Still very low-level, one instruction per line

**Interactive Demo:** [Assembly Language Simulator](https://schweigi.github.io/assembler-simulator/)

**Video Resource:** [How Assembly Language Works](https://www.youtube.com/watch?v=wA2oMRmbrfo) (6 minutes)

### 3. High-Level Languages (15 minutes)

#### FORTRAN (1957)
- **Creator:** John Backus at IBM
- **Purpose:** Scientific and mathematical calculations
- **Innovation:** First high-level programming language
- **Impact:** Showed that computers could understand more human-like instructions

**Example:**
```fortran
PROGRAM HELLO
  PRINT *, 'Hello, World!'
END PROGRAM HELLO
```

#### COBOL (1959)
- **Creator:** Grace Hopper and team
- **Purpose:** Business and administrative systems
- **Innovation:** Used English-like syntax
- **Legacy:** Still runs many banking and government systems today

**Example:**
```cobol
DISPLAY "Hello, World!"
```

**Video Resource:** [Grace Hopper: The First Computer Bug](https://www.youtube.com/watch?v=1-vcErOPofQ) (4 minutes)

#### C Language (1972)
- **Creator:** Dennis Ritchie at Bell Labs
- **Purpose:** System programming (operating systems, compilers)
- **Impact:** 
  - Influenced almost every modern programming language
  - Used to write Unix operating system
  - Perfect balance of power and simplicity

**Example:**
```c
#include <stdio.h>
int main() {
    printf("Hello, World!\n");
    return 0;
}
```

**Key Innovation:** C introduced many concepts still used today:
- Structured programming
- Portable code (works on different computers)
- Efficient compilation

### 4. Modern Programming Languages (10 minutes)

#### Object-Oriented Languages (1980s-1990s)

**C++ (1985)**
- **Creator:** Bjarne Stroustrup
- **Innovation:** Added object-oriented features to C
- **Use:** Game development, system software, embedded systems

**Java (1995)**
- **Creator:** James Gosling at Sun Microsystems
- **Motto:** "Write once, run anywhere"
- **Impact:** Revolutionized web development and enterprise software

**Example:**
```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

#### Web Languages (1990s-2000s)

**JavaScript (1995)**
- **Creator:** Brendan Eich at Netscape
- **Purpose:** Make web pages interactive
- **Evolution:** Now used for servers, mobile apps, and desktop applications

**Example:**
```javascript
console.log("Hello, World!");
```

**Video Resource:** [JavaScript in 100 Seconds](https://www.youtube.com/watch?v=DHjqpvDnNGE) (2 minutes)

#### Language Comparison Chart

| Language | Year | Creator | Primary Use | Difficulty |
|----------|------|---------|-------------|------------|
| Machine Code | 1940s | N/A | Direct hardware control | Very Hard |
| Assembly | 1950s | Various | System programming | Hard |
| FORTRAN | 1957 | John Backus | Scientific computing | Medium |
| COBOL | 1959 | Grace Hopper | Business systems | Medium |
| C | 1972 | Dennis Ritchie | System programming | Medium-Hard |
| C++ | 1985 | Bjarne Stroustrup | Games, systems | Hard |
| Java | 1995 | James Gosling | Enterprise apps | Medium |
| JavaScript | 1995 | Brendan Eich | Web development | Easy-Medium |
| Python | 1991 | Guido van Rossum | General purpose | Easy |

### 5. Why Python? (5 minutes)

#### Python's Story (1991)
- **Creator:** Guido van Rossum in the Netherlands
- **Name:** Named after "Monty Python's Flying Circus"
- **Philosophy:** "There should be one obvious way to do it"

#### Why Python is Perfect for Learning

**1. Simple Syntax**
Compare these "Hello, World!" programs:

**C++:**
```cpp
#include <iostream>
using namespace std;
int main() {
    cout << "Hello, World!" << endl;
    return 0;
}
```

**Python:**
```python
print("Hello, World!")
```

**2. Readable Code**
Python looks like English:
```python
if temperature > 80:
    print("It's hot today!")
else:
    print("Nice weather!")
```

**3. Versatile Applications**
- Web development (Instagram, YouTube)
- Data science (Netflix recommendations)
- Artificial intelligence (Tesla's autopilot)
- Scientific computing (NASA missions)
- Game development (Civilization IV)

**4. Great for Beginners**
- Less syntax to memorize
- Immediate feedback
- Large supportive community
- Extensive libraries

**Interactive Demo:** [Python Online Interpreter](https://repl.it/languages/python3)

**Video Resource:** [Python in 100 Seconds](https://www.youtube.com/watch?v=x7X9w_GIm1s) (2 minutes)

---

## Activities

### Language Timeline Activity (10 minutes)
Create a simple timeline showing:
- 1940s: Machine Code
- 1950s: Assembly, FORTRAN
- 1960s: COBOL
- 1970s: C
- 1980s: C++
- 1990s: Java, JavaScript, Python
- 2000s: Modern frameworks and tools

### "Hello, World!" Collection
Try writing "Hello, World!" in different languages using online interpreters:
- [Python](https://repl.it/languages/python3)
- [JavaScript](https://repl.it/languages/javascript)
- [Java](https://repl.it/languages/java)

### Programming Language Research
Each student researches one programming language not covered in class:
- When was it created?
- Who created it?
- What is it used for?
- Is it still popular today?

---

## Assessment

### Formative Assessment
- **Participation:** Active engagement in discussions about language evolution
- **Demonstration:** Successfully run "Hello, World!" in Python
- **Analysis:** Compare and contrast different programming languages

### Quick Quiz (5 minutes)
1. What was the first high-level programming language?
2. Who created the C programming language?
3. Why is Python considered good for beginners?
4. What does "Write once, run anywhere" refer to?

---

## Extensions

### For Advanced Students
- Research esoteric programming languages (Brainfuck, Malbolge)
- Compare programming paradigms (procedural, object-oriented, functional)
- Investigate how programming languages are created

### For Struggling Students
- Focus on the visual timeline activity
- Use analogies (programming languages are like different ways to give directions)
- Provide additional practice with Python's simple syntax

---

## Resources

### Educational Videos
- [Programming Languages Timeline](https://www.youtube.com/watch?v=Tr9E_vzKRVo) (12 minutes)
- [History of Programming Languages](https://www.youtube.com/watch?v=qQXXI5QFUfw) (20 minutes)
- [Why Python is Great for Beginners](https://www.youtube.com/watch?v=Y8Tko2YC5hA) (15 minutes)

### Interactive Learning
- [Codecademy: Learn Python](https://www.codecademy.com/learn/learn-python-3)
- [Python.org Beginner's Guide](https://www.python.org/about/gettingstarted/)
- [Repl.it Python Classroom](https://repl.it/languages/python3)

### Documentation and References
- [Python Official Documentation](https://docs.python.org/3/)
- [Programming Languages Comparison](https://en.wikipedia.org/wiki/Comparison_of_programming_languages)
- [Computer Languages History](https://www.computerhistory.org/timeline/software-languages/)

### Books for Further Reading
- "The Pragmatic Programmer" by David Thomas and Andrew Hunt
- "Code Complete" by Steve McConnell
- "Python Crash Course" by Eric Matthes

---

## Homework
- Install Python on your computer (we'll do this together next week)
- Read about one programming language not discussed in class
- Write a one-paragraph reflection: "Why do you think programming languages keep evolving?"
- Practice running simple Python commands in an online interpreter

---

## Notes for Instructors
- Emphasize that learning programming is like learning a new language
- Use the cooking analogy: recipes (programs) written in different languages (programming languages)
- Encourage students to experiment with the online Python interpreter
- Address any concerns about programming being "too difficult"
- Connect programming evolution to other technological advances they know
