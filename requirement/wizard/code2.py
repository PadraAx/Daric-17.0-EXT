import xmlrpc.client
from graphviz import Digraph

# Configuration
odoo_url = "http://your-odoo-instance.com"
db_name = "your_db_name"
username = "your_username"
password = "your_password"

# Connect to Odoo
common = xmlrpc.client.ServerProxy(f"{odoo_url}/xmlrpc/2/common")
uid = common.authenticate(db_name, username, password, {})
models = xmlrpc.client.ServerProxy(f"{odoo_url}/xmlrpc/2/object")

if not uid:
    print("Authentication failed.")
    exit()

# Fetch data
print("Fetching data from Odoo...")
users = models.execute_kw(db_name, uid, password, 'res.users', 'search_read', [[], ['name', 'groups_id', 'partner_id']])
partners = models.execute_kw(db_name, uid, password, 'res.partner', 'search_read', [[], ['id', 'name', 'category_id']])
groups = models.execute_kw(db_name, uid, password, 'res.groups', 'search_read', [[], ['name', 'implied_ids']])
access_rights = models.execute_kw(db_name, uid, password, 'ir.model.access', 'search_read', [[], ['group_id', 'model_id', 'perm_read', 'perm_write', 'perm_create', 'perm_unlink']])
record_rules = models.execute_kw(db_name, uid, password, 'ir.rule', 'search_read', [[], ['name', 'model_id', 'domain_force', 'groups']])
models_list = models.execute_kw(db_name, uid, password, 'ir.model', 'search_read', [[], ['name', 'model']])
partner_categories = models.execute_kw(db_name, uid, password, 'res.partner.category', 'search_read', [[], ['id', 'name']])

# Prepare data mappings
group_names = {group['id']: group['name'] for group in groups}
model_names = {model['id']: model['model'] for model in models_list}
partner_names = {partner['id']: partner['name'] for partner in partners}
partner_categories_map = {cat['id']: cat['name'] for cat in partner_categories}

user_groups = {user['name']: [group_names[gid] for gid in user['groups_id']] for user in users}
user_partner_categories = {
    user['name']: [partner_categories_map[cat_id] for cat_id in partners if cat_id in user['partner_id']] if user['partner_id'] else []
    for user in users
}

# Create a graph
graph = Digraph(comment="Odoo Access Rights and Record Rules Visualization")

# Add users and their groups and partner tags
for user, groups in user_groups.items():
    partner_tags = ", ".join(user_partner_categories.get(user, []))
    user_label = f"{user}\nTags: {partner_tags}" if partner_tags else user
    graph.node(user, shape='ellipse', color='blue', label=user_label)
    for group in groups:
        graph.node(group, shape='box', color='green')
        graph.edge(user, group)

# Add groups and their models with permissions
for access in access_rights:
    group_name = group_names.get(access['group_id'][0], "Unknown Group")
    model_name = model_names.get(access['model_id'][0], "Unknown Model")

    if group_name and model_name:
        permission_label = "".join([
            "R" if access['perm_read'] else "",
            "W" if access['perm_write'] else "",
            "C" if access['perm_create'] else "",
            "D" if access['perm_unlink'] else ""
        ])
        graph.node(model_name, shape='folder', color='orange')
        graph.edge(group_name, model_name, label=permission_label)

# Add record rules
for rule in record_rules:
    rule_name = rule['name']
    model_name = model_names.get(rule['model_id'][0], "Unknown Model")
    domain = rule['domain_force']
    group_ids = rule['groups']
    group_names_for_rule = [group_names[gid] for gid in group_ids if gid in group_names]

    rule_label = f"{rule_name}\nDomain: {domain}"
    graph.node(rule_name, shape='note', color='red', label=rule_label)
    if model_name:
        graph.edge(rule_name, model_name, label="Applies to")
    for group_name in group_names_for_rule:
        graph.edge(group_name, rule_name, label="Has Rule")

# Save and render the graph
output_file = "odoo_access_rights_record_rules"
print(f"Generating visualization at {output_file}.png...")
graph.render(output_file, format='png', cleanup=True)

print("Visualization generated successfully.")
