-- Create the departments table
CREATE TABLE departments (
    department_id INT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL
);

-- Create the employees table
CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    department_id INT,
    hire_date DATE,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

-- Create the salaries table
CREATE TABLE salaries (
    employee_id INT,
    salary DECIMAL(10, 2),
    from_date DATE,
    to_date DATE,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

-- Insert sample data into the departments table
INSERT INTO departments (department_id, department_name) VALUES
(1, 'HR'),
(2, 'Engineering'),
(3, 'Sales');

-- Insert sample data into the employees table
INSERT INTO employees (employee_id, first_name, last_name, department_id, hire_date) VALUES
(101, 'John', 'Doe', 1, '2023-06-01'),
(102, 'Jane', 'Smith', 2, '2022-01-15'),
(103, 'Bob', 'Johnson', 3, '2024-03-20'),
(104, 'Alice', 'Williams', 2, '2021-11-30'),
(105, 'Charlie', 'Brown', 1, '2022-12-01');

-- Insert sample data into the salaries table
INSERT INTO salaries (employee_id, salary, from_date, to_date) VALUES
(101, 50000, '2023-06-01', '9999-01-01'),
(102, 75000, '2022-01-15', '9999-01-01'),
(103, 60000, '2023-03-20', '9999-01-01'),
(104, 90000, '2021-11-30', '9999-01-01'),
(105, 55000, '2022-12-01', '9999-01-01');

-- Query to find all employees who have been hired in the last year
SELECT employee_id, first_name, last_name, hire_date
FROM employees
WHERE hire_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR);

-- Query to calculate the total salary expenditure for each department
SELECT d.department_name, SUM(s.salary) AS total_salary_expenditure
FROM employees e
JOIN salaries s ON e.employee_id = s.employee_id
JOIN departments d ON e.department_id = d.department_id
GROUP BY d.department_name;

-- Query to find the top 5 highest-paid employees along with their department names
SELECT e.employee_id, e.first_name, e.last_name, d.department_name, MAX(s.salary) AS max_salary
FROM employees e
JOIN salaries s ON e.employee_id = s.employee_id
JOIN departments d ON e.department_id = d.department_id
GROUP BY e.employee_id, e.first_name, e.last_name, d.department_name
ORDER BY max_salary DESC
LIMIT 5;
