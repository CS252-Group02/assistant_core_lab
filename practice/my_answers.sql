-- Write ONE query under each marker. Do not delete the markers.
-- Check with:  python check.py
-- Q1  (all columns of all students)

-- Q2  (name and year of every student)

-- Q3  (names of CS students)

-- Q4  (name and year of students in year 3 or higher)

-- Q5  (student names, Z to A)

-- Q6  (title and credits of 4-credit courses, by title)

-- Q7  (how many students?)

-- Q8  (number of students per program, by program)

-- Q9  (average grade in CSC10004, rounded to 2 decimals)

-- Q10 (student_id and course_code of enrollments without a grade, by student_id)

-- Q11 (name and grade of graded students in CSC10014, by name)
SELECT s.name, e.grade
FROM students AS s
JOIN enrollments AS e ON e.student_id = s.id
WHERE e.course_code = 'CSC10014' AND e.grade IS NOT NULL
ORDER BY s.name;

-- Q12 (course title and number of enrolled students, most first, then by title)
SELECT c.title, COUNT(e.student_id) AS enrolled_students
FROM courses AS c
LEFT JOIN enrollments AS e ON e.course_code = c.code
GROUP BY c.code, c.title
ORDER BY enrolled_students DESC, c.title;

-- Q13 (names of students with a grade below 5, by name)
SELECT s.name
FROM students AS s
WHERE EXISTS (
    SELECT 1
    FROM enrollments AS e
    WHERE e.student_id = s.id AND e.grade < 5
)
ORDER BY s.name;

-- Q14 (each student's name and total credits enrolled, most first, then by name)
SELECT s.name, COALESCE(SUM(c.credits), 0) AS total_credits
FROM students AS s
LEFT JOIN enrollments AS e ON e.student_id = s.id
LEFT JOIN courses AS c ON c.code = e.course_code
GROUP BY s.id, s.name
ORDER BY total_credits DESC, s.name;

-- Q15 (names of students NOT enrolled in CSC10014, by name)
SELECT s.name
FROM students AS s
LEFT JOIN enrollments AS e ON e.student_id = s.id AND e.course_code = 'CSC10014'
WHERE e.student_id IS NULL
ORDER BY s.name;
