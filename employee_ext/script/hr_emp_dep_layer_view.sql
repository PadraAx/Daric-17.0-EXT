CREATE OR REPLACE VIEW hr_emp_dep_layer_view AS
WITH RECURSIVE department_hierarchy AS (
    SELECT 
        d.id AS department_id, 
        d.parent_id, 
        (SELECT value FROM jsonb_each_text(d.name) LIMIT 1) AS department_name, 
        d.layer_id,
        (SELECT name FROM hr_department_layer WHERE id = d.layer_id) AS layer_name,
        e.id AS employee_id
    FROM hr_department d
    INNER JOIN hr_employee e ON d.id = e.department_id
    UNION ALL
    SELECT 
        d.id AS department_id, 
        d.parent_id, 
        (SELECT value FROM jsonb_each_text(d.name) LIMIT 1) AS department_name, 
        d.layer_id,
        (SELECT name FROM hr_department_layer WHERE id = d.layer_id) AS layer_name,
        dh.employee_id
    FROM hr_department d
    INNER JOIN department_hierarchy dh ON dh.parent_id = d.id
)

-- Pivot the results to show each layer_name as a separate column
SELECT 
    employee_id,
    MAX(CASE WHEN layer_id = 1 THEN department_name END) AS "division", 
    MAX(CASE WHEN layer_id = 2 THEN department_name END) AS "dep",
    MAX(CASE WHEN layer_id = 3 THEN department_name END) AS "unit",
    MAX(CASE WHEN layer_id = 4 THEN department_name END) AS "sub_unit",
    MAX(CASE WHEN layer_id = 5 THEN department_name END) AS "desk",
    MAX(CASE WHEN layer_id = 1 THEN department_id END) AS "division_id", 
    MAX(CASE WHEN layer_id = 2 THEN department_id END) AS "dep_id",
    MAX(CASE WHEN layer_id = 3 THEN department_id END) AS "unit_id",
    MAX(CASE WHEN layer_id = 4 THEN department_id END) AS "sub_unit_id",
    MAX(CASE WHEN layer_id = 5 THEN department_id END) AS "desk_id"
FROM department_hierarchy
GROUP BY employee_id;


