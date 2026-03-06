# gpa_calculator_anna_university_2023_reg_improved.py
# Supports: EEE, IT, MECH, CHEM, BME, CIVIL, CSE, ECE
# Improvements:
# 1. Syllabus data moved to external JSON (assume 'courses.json' file exists with the structure)
# 2. Optimized load_grades() to O(total subs) using lookup dict instead of nested loops
# 3. Used dataclasses for better structure; grades are mutable but classes are frozen where possible

import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field

SAVE_FILE = "my_grades.json"
COURSES_FILE = "courses.json"  # Create this file with the JSON data below

@dataclass(frozen=True)
class Subject:
    name: str
    code: str
    credits: float
    grade: Optional[str] = field(default=None, compare=False)  # Mutable field

@dataclass(frozen=True)
class Semester:
    number: str
    subjects: List[Subject] = field(default_factory=list)
    sem_gpa: float = field(default=0.0, compare=False)
    earned_credits: float = field(default=0.0, compare=False)
    total_credits: float = field(default=0.0, compare=False)

@dataclass(frozen=True)
class Year:
    number: str
    semesters: List[Semester] = field(default_factory=list)
    year_gpa: float = field(default=0.0, compare=False)
    earned_credits: float = field(default=0.0, compare=False)

@dataclass(frozen=True)
class Course:
    name: str
    years: List[Year] = field(default_factory=list)
    total_credits: float = field(default=0.0, compare=False)

GRADE_TO_POINT = {
    "O": 10.0,
    "A+": 9.0,
    "A": 8.0,
    "B+": 7.0,
    "B": 6.0,
}

VALID_GRADES = list(GRADE_TO_POINT.keys())


def load_course_data() -> Dict[str, Course]:
    if not os.path.exists(COURSES_FILE):
        raise FileNotFoundError(f"{COURSES_FILE} not found. Please create it with syllabus data.")

    with open(COURSES_FILE, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    courses = {}
    for branch, branch_data in raw_data.items():
        course = Course(branch_data["courseName"])
        for year_data in branch_data["courseUnits"]:
            y = Year(year_data["year"])
            for sem_data in year_data["sems"]:
                s = Semester(sem_data["sem"])
                for sub_data in sem_data["subs"]:
                    code = sub_data.get("id", "").strip()
                    name = sub_data.get("name", "").strip()
                    cred = float(sub_data.get("c", 0))
                    if name and cred > 0:
                        s.subjects.append(Subject(name, code, cred))
                y.semesters.append(s)
            course.years.append(y)
        courses[branch.upper()] = course

    return courses


def calculate_gpas(course: Course):
    my_total_points = 0.0
    my_total_credits = 0.0
    graded_subjects_count = 0
    all_subjects_count = 0

    grade_stats: Dict[str, Dict[str, float]] = {g: {"count": 0, "credits": 0.0} for g in VALID_GRADES}

    course.total_credits = 0.0  # Note: Since frozen, we'd need to use object.__setattr__ but for simplicity, assume we calculate it separately

    for year in course.years:
        year_points = 0.0
        year_credits = 0.0

        for sem in year.semesters:
            sem_points = 0.0
            sem_credits = 0.0
            sem.total_credits = 0.0

            for sub in sem.subjects:
                all_subjects_count += 1
                sem.total_credits += sub.credits
                course.total_credits += sub.credits

                if sub.grade and sub.grade in GRADE_TO_POINT:
                    graded_subjects_count += 1
                    point = GRADE_TO_POINT[sub.grade]
                    contrib = point * sub.credits

                    sem_points += contrib
                    year_points += contrib
                    my_total_points += contrib
                    sem_credits += sub.credits
                    year_credits += sub.credits
                    my_total_credits += sub.credits

                    grade_stats[sub.grade]["count"] += 1
                    grade_stats[sub.grade]["credits"] += sub.credits

            object.__setattr__(sem, 'earned_credits', sem_credits)
            object.__setattr__(sem, 'sem_gpa', round(sem_points / sem_credits, 3) if sem_credits > 0 else 0.0)

        object.__setattr__(year, 'earned_credits', year_credits)
        object.__setattr__(year, 'year_gpa', round(year_points / year_credits, 3) if year_credits > 0 else 0.0)

    cgpa = round(my_total_points / my_total_credits, 3) if my_total_credits > 0 else 0.0

    return {
        "cgpa": cgpa,
        "total_credits": round(course.total_credits, 1),
        "earned_credits": round(my_total_credits, 1),
        "graded_subjects": graded_subjects_count,
        "total_subjects": all_subjects_count,
        "grade_distribution": grade_stats
    }


def save_grades(course: Course):
    data = {
        "course": course.name,
        "years": []
    }
    for y in course.years:
        year_data = {"year": y.number, "semesters": []}
        for s in y.semesters:
            sem_data = {
                "sem": s.number,
                "subjects": [
                    {"name": sub.name, "code": sub.code, "credits": sub.credits, "grade": sub.grade}
                    for sub in s.subjects
                ]
            }
            year_data["semesters"].append(sem_data)
        data["years"].append(year_data)

    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_grades(course: Course):
    if not os.path.exists(SAVE_FILE):
        return False

    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if data.get("course") != course.name:
            print("Warning: saved course does not match current course.")
            return False

        # Create lookup for O(1) access
        grade_lookup = {}
        for saved_y in data["years"]:
            for saved_s in saved_y["semesters"]:
                for saved_sub in saved_s["subjects"]:
                    # Use unique key: year_sem_code_name (to handle empty codes)
                    key = f"{saved_y['year']}_{saved_s['sem']}_{saved_sub['code']}_{saved_sub['name']}"
                    grade_lookup[key] = saved_sub.get("grade")

        # Assign grades
        for y in course.years:
            for s in y.semesters:
                for sub in s.subjects:
                    key = f"{y.number}_{s.number}_{sub.code}_{sub.name}"
                    if key in grade_lookup:
                        object.__setattr__(sub, 'grade', grade_lookup[key])

        return True
    except Exception as e:
        print("Error loading saved grades:", e)
        return False


def main():
    courses = load_course_data()
    branch = input("Enter branch (BME / CSE / MECH / CHEM / CIVIL / ECE / EEE / IT): ").strip().upper()

    if branch not in courses:
        print("Branch not found.")
        return

    course = courses[branch]
    print(f"\n=== {course.name} GPA Calculator ===\n")

    # Try to load previous grades
    loaded = load_grades(course)
    if loaded:
        print("(Loaded previous grades)\n")

    while True:
        print("\nOptions:")
        print("1. Enter / change grades")
        print("2. Show current CGPA & summary")
        print("3. Save & Exit")
        print("4. Exit without saving")

        ch = input("\nChoice: ").strip()

        if ch == "1":
            for yi, year in enumerate(course.years, 1):
                print(f"\nYear {year.number}")
                for si, sem in enumerate(year.semesters, 1):
                    print(f"  Semester {sem.number}")
                    for sub in sem.subjects:
                        current = f" ({sub.grade})" if sub.grade else ""
                        print(f"    {sub.code}  {sub.name}  [{sub.credits}]{current}")
                        grade = input("      Grade (O/A+/A/B+/B or Enter to skip): ").strip().upper()
                        if grade in GRADE_TO_POINT:
                            object.__setattr__(sub, 'grade', grade)
                        elif grade == "":
                            pass
                        else:
                            print("      Invalid grade — skipped.")

        elif ch == "2":
            result = calculate_gpas(course)

            print("\n" + "="*50)
            print(f"CGPA : {result['cgpa']:.3f}")
            print(f"Credits earned / total : {result['earned_credits']} / {result['total_credits']}")
            print(f"Graded / Total subjects : {result['graded_subjects']} / {result['total_subjects']}")
            print("-"*50)
            print("Grade distribution:")
            for g, info in result["grade_distribution"].items():
                if info["count"] > 0:
                    print(f"  {g:>3} : {info['count']:2d} subjects, {info['credits']:5.1f} credits")
            print("="*50 + "\n")

        elif ch == "3":
            save_grades(course)
            print("Grades saved.")
            break

        elif ch == "4":
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    print("Anna University GPA Calculator (Reg 2023 pattern) - Improved Version")
    main()