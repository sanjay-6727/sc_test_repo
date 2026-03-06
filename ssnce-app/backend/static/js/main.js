// static/js/main.js
document.addEventListener('DOMContentLoaded', () => {
  const gradeSelects = document.querySelectorAll('.grade-select');
  const cgpaDisplay = document.querySelector('.text-5xl.font-bold.text-primary'); // your 8.75 element

  const gradePoints = {
    'O': 10.0,
    'A+': 9.0,
    'A': 8.0,
    'B+': 7.0,
    'B': 6.0
  };

  function calculateCGPA() {
    let totalPoints = 0;
    let totalCredits = 0;

    gradeSelects.forEach(select => {
      const grade = select.value;
      const credits = parseFloat(select.dataset.credits) || 0;

      if (grade && gradePoints[grade]) {
        totalPoints += gradePoints[grade] * credits;
        totalCredits += credits;
      }
    });

    const cgpa = totalCredits > 0 ? (totalPoints / totalCredits).toFixed(2) : '0.00';
    if (cgpaDisplay) cgpaDisplay.textContent = cgpa;
  }

  gradeSelects.forEach(select => {
    select.addEventListener('change', calculateCGPA);
  });

  // Initial calc (if any pre-selected)
  calculateCGPA();
});