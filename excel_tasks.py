import pandas as pd
import numpy as np
import json

def load_employee_data(filepath):
    """Load and preprocess the employee Excel file."""
    df = pd.read_excel(filepath)
    df['DOJ'] = pd.to_datetime(df['DOJ'])
    # print(f"Loaded {(df['DOJ'])} employees from {filepath}")
    return df

def identify_gratuity_eligible_employees(df):
    """Identify employees who served more than 60 months."""
    today = pd.Timestamp.today()
    df['months_served'] = ((today - df['DOJ']) / pd.Timedelta(days=30)).astype(int)
    eligible = df[df['months_served'] > 60]
    print("=== Employees Eligible for Gratuity ===")
    print(eligible[['id', 'name', 'DOJ', 'months_served']])
    return eligible

def find_employees_with_higher_salary_than_managers(df):
    """Find employees whose salary is greater than their manager's salary."""
    manager_salary_map = df.set_index('id')['salary'].to_dict()
    df['manager_salary'] = df['manager_id'].map(manager_salary_map)
    higher_paid = df[df['salary'] > df['manager_salary']]
    print("\n=== Employees Earning More Than Their Manager ===")
    print(higher_paid[['id', 'name', 'salary', 'manager_id', 'manager_salary']])
    return higher_paid

def build_employee_hierarchy(df):
    print("\n=== Building Employee Hierarchy ===")
    print(df[['id', 'name', 'manager_id']])
    """Build and save employee hierarchy to a JSON file."""
    def build_tree(df, manager_id=None):
        # Check if manager_id is None (for root level) or a specific ID
        if manager_id is None:
            # For root level, find employees with NaN manager_id
            subordinates = df[df['manager_id'].isna()]
        else:
            # For other levels, find employees with this specific manager_id
            subordinates = df[df['manager_id'] == manager_id]

        hierarchy = []
        for _, row in subordinates.iterrows():
            person = {
                "id": int(row['id']),
                "name": row['name'],
                "role": row['category'].capitalize(),
            }
            children = build_tree(df, row['id'])
            if children:
                person["reportees"] = children
            hierarchy.append(person)
        return hierarchy

    tree = build_tree(df, manager_id=None)
    print("\n=== Employee Hierarchy ===")
    print(tree)
    with open("employee_hierarchy.json", "w") as f:
        json.dump(tree, f, indent=4)
    print("\n=== Hierarchy exported to employee_hierarchy.json ===")
    return tree

def print_nth_highest_salary_sql():
    """Print SQL query to get the nth highest salary."""
    print("\n=== SQL Query for Nth Highest Salary ===")
    print("""SELECT *
FROM employees e1
WHERE (
    SELECT COUNT(DISTINCT e2.salary)
    FROM employees e2
    WHERE e2.salary > e1.salary
) = N - 1;""")

def main():
    try:
        # Try to load data from Excel file
        filepath = "employees_data.xlsx"
        df = load_employee_data(filepath)
        print(f"Data loaded from {filepath}")
    except FileNotFoundError:
        # Create sample data if Excel file doesn't exist
        print("Excel file not found. Creating sample data instead.")
        sample_data = {
            'id': [1, 2, 3, 4, 5, 6],
            'name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown', 'Charlie Davis', 'Eve Wilson'],
            'DOJ': ['2020-01-15', '2018-06-20', '2021-03-10', '2019-08-25', '2022-01-05', '2017-11-30'],
            'salary': [75000, 85000, 65000, 90000, 60000, 95000],
            'manager_id': [np.nan, 1, 1, 2, 2, 1],  # np.nan for CEO (no manager)
            'category': ['CEO', 'Manager', 'Developer', 'Manager', 'Developer', 'Manager']
        }
        df = pd.DataFrame(sample_data)
        df['DOJ'] = pd.to_datetime(df['DOJ'])

    identify_gratuity_eligible_employees(df)
    find_employees_with_higher_salary_than_managers(df)
    build_employee_hierarchy(df)
    print_nth_highest_salary_sql()

if __name__ == "__main__":
    main()
