

import random

# ============================================================
# ACCESS GUARD - EMPLOYEE ACCESS MANAGEMENT SYSTEM
# ============================================================

tools = [
    "GITHUB",
    "AWS",
    "SLACK",
    "JIRA",
    "HR PORTAL",
    "FIGMA",
    "PRODUCTION SERVER",
    "DOCKER"
]

valid_roles = (
    "Intern",
    "Developer",
    "Tester",
    "Manager",
    "Admin"
)

roles_permission = {
    "Intern": ["SLACK", "JIRA"],
    "Developer": ["GITHUB", "SLACK", "JIRA", "AWS"],
    "Tester": ["SLACK", "JIRA", "GITHUB", "DOCKER"],
    "Manager": ["GITHUB", "AWS", "SLACK", "JIRA", "HR PORTAL"],
    "Admin": [
        "GITHUB",
        "AWS",
        "SLACK",
        "JIRA",
        "HR PORTAL",
        "FIGMA",
        "PRODUCTION SERVER",
        "DOCKER"
    ]
}

employees = {
    "E101": {
        "name": "Aarav Sharma",
        "role": "Manager",
        "access": ["GITHUB", "AWS", "SLACK", "JIRA"],
        "email": "aaravsharma@pythongurukool.com"
    },

    "E102": {
        "name": "Sneha Patil",
        "role": "Intern",
        "access": ["SLACK", "JIRA"],
        "email": "snehapatil@pythongurukool.com"
    }
}

log = [
    ("E101", "GITHUB", "Granted", "2026-08-15"),
    ("E102", "AWS", "Denied", "2026-08-15")
]


# ============================================================
# PHASE 1 - FRONTEND
# ============================================================

print("=" * 60)
print("PYTHONGURUKOOL | HQ : PUNE | EST : 2018")
print("Security Standard : ISO 27000 Certified")
print("=" * 60)

print("Total available tools :", len(tools))
print("Valid Roles :", len(valid_roles))
print("Employees Registered :", len(employees))

print("=" * 60)

print("Available Tools :")
print(tools)

print("\nValid Roles :")
print(valid_roles)

print("\nRole Permissions:")

for role in valid_roles:
    print(role, "-->", roles_permission[role])

print("\nExisting Employees:")

for emp_id, data in employees.items():
    print(
        emp_id,
        "|",
        data["name"],
        "|",
        data["role"],
        "|",
        data["access"]
    )

print("\nAccess Log:")

for entry in log:
    print(entry)


# ============================================================
# PHASE 2 - NEW EMPLOYEE ONBOARDING
# ============================================================

print("\n")
print("=" * 60)
print("             NEW EMPLOYEE ONBOARDING")
print("=" * 60)


# ---------------- NAME VALIDATION ----------------

while True:

    full_name = input(
        "Enter your name (First name Last name) : "
    ).strip()

    name_parts = full_name.split()

    if len(name_parts) == 2:

        first_name = name_parts[0]
        last_name = name_parts[1]

        if first_name.isalpha() and last_name.isalpha():
            full_name = first_name.title() + " " + last_name.title()
            print("✅ Name accepted :", full_name)
            break

    print("🚫 Invalid name.")
    print("Please enter First name Last name.")


# ---------------- EMPLOYEE ID ----------------

while True:

    emp = input(
        "Enter Employee Number starting with E : "
    ).strip().upper()

    if (
        len(emp) == 4
        and emp.startswith("E")
        and emp[1:].isdigit()
    ):

        if emp not in employees:
            print("✅ Valid Employee ID")
            break

        else:
            print("🚫 Employee ID already exists.")

    else:
        print("🚫 Invalid Employee ID.")
        print("Example : E103")


# ---------------- ROLE VALIDATION ----------------

while True:

    role = input(
        "Enter your Role : "
    ).strip().title()

    if role in valid_roles:

        print("✅ Valid Role :", role)
        break

    print("🚫 Invalid Role.")
    print("Available Roles :", valid_roles)


# ---------------- EMAIL GENERATION ----------------

email = (
    first_name.lower()
    + last_name.lower()
    + "@pythongurukool.com"
)


# ---------------- PASSWORD GENERATION ----------------

password = (
    first_name[:3].lower()
    + emp[-3:]
    + "@TN"
)


# ---------------- EXPERIENCE ----------------

while True:

    exp = input(
        "Enter your years of experience : "
    ).strip()

    if exp.isdigit():

        exp = int(exp)

        if exp >= 0:
            break

        print("Experience cannot be negative.")

    else:
        print("🚫 Enter numbers only.")


# ---------------- EXPERIENCE LEVEL ----------------

if exp == 0:
    print("Fresher Detected - Mentor will be assigned")

elif exp <= 3:
    print("Junior Level")

elif exp <= 7:
    print("Mid Level")

else:
    print("Senior Level")


# ---------------- ASSIGN ACCESS ----------------

access = roles_permission[role].copy()

print("\nYour role-based access is :")
print(access)


# ---------------- ADD EMPLOYEE ----------------

employees[emp] = {
    "name": full_name,
    "role": role,
    "access": access,
    "email": email
}


# ---------------- ONBOARDING RECORD ----------------

permanent_onboard = (
    emp,
    full_name,
    role,
    "2026-09-02"
)


print("\n")
print("=" * 60)
print("             ONBOARDING COMPLETE")
print("=" * 60)

print("Name       :", full_name)
print("ID         :", emp)
print("Role       :", role)
print("Email      :", email)
print("Password   :", password)
print("Access     :", access)

print("-" * 60)

print("Permanent Record :", permanent_onboard)
print("Record Type      :", type(permanent_onboard))

print("=" * 60)


# ============================================================
# PHASE 3 - ACCESS REQUEST PORTAL
# ============================================================

print("\n")
print("=" * 60)
print("              ACCESS REQUEST PORTAL")
print("=" * 60)

print("Registered Employees :")

for employee_id in employees:
    print(employee_id)

# ---------------- EMPLOYEE SEARCH ----------------

while True:

    request_id = input(
        "\nEnter Employee ID : "
    ).strip().upper()

    emp1 = employees.get(request_id)

    if emp1 is not None:
        break

    print("🚫 No employee found.")
    print("Please enter a valid Employee ID.")


print("\nWelcome", emp1["name"], "!!")
print("Current Role :", emp1["role"])
print("Current Access :", emp1["access"])


# ---------------- TOOL REQUEST ----------------

while True:

    print("\nAvailable Company Tools :")
    print(tools)

    request_tool = input(
        "Enter requested tool : "
    ).strip().upper()

    if request_tool in tools:
        break

    print("🚫 Tool not found.")
    print("Please select a tool from the list.")


# ---------------- ACCESS CHECK ----------------

if request_tool in emp1["access"]:

    position = emp1["access"].index(request_tool)

    print(
        "ℹ️ You already have access to",
        request_tool
    )

    print(
        "Position in access list :",
        position + 1
    )


elif request_tool not in roles_permission[emp1["role"]]:

    print("🚫 ACCESS DENIED")

    denial_log = (
        request_id,
        request_tool,
        "Denied",
        "2026-09-02"
    )

    log.append(denial_log)

    print(
        emp1["role"],
        "is not permitted to use",
        request_tool
    )


else:

    print(
        "✅ ACCESS GRANTED to",
        emp1["name"]
    )

    emp1["access"].append(request_tool)

    print(
        "Updated Accessible Tools :",
        emp1["access"]
    )

    grant_log = (
        request_id,
        request_tool,
        "Granted",
        "2026-09-02"
    )

    log.append(grant_log)

    print("Grant Logged :", grant_log)


# ============================================================
# PHASE 4 - AUDIT REPORT
# ============================================================

print("\n")
print("=" * 60)
print("                 AUDIT REPORT")
print("=" * 60)


# Create sets dynamically from employee records

employee_ids = list(employees.keys())

if len(employee_ids) >= 2:

    emp_a = employee_ids[0]
    emp_b = employee_ids[1]

    access_a = set(employees[emp_a]["access"])
    access_b = set(employees[emp_b]["access"])

    common_tools = access_a.intersection(access_b)

    print(
        "Common tools used by",
        employees[emp_a]["name"],
        "and",
        employees[emp_b]["name"],
        ":",
        common_tools
    )

    only_a = access_a - access_b
    only_b = access_b - access_a

    print(
        employees[emp_a]["name"],
        "exclusive tools :",
        only_a
    )

    print(
        employees[emp_b]["name"],
        "exclusive tools :",
        only_b
    )

    total_tools = access_a.union(access_b)

    print(
        "Total unique tools used :",
        total_tools
    )

    exclusive_tools = access_a.symmetric_difference(access_b)

    print(
        "Tools used exclusively by one employee :",
        exclusive_tools
    )

    tools_set = set(tools)

    unused_tools = tools_set - total_tools

    print(
        "🚨 Company is paying for",
        len(unused_tools),
        "unused tools"
    )

    print("Unused tools :", unused_tools)


# ---------------- DUPLICATE REMOVAL ----------------

print("\n")
print("------------- DUPLICATION DEMO -------------")

buggy_list = [
    "GITHUB",
    "AWS",
    "SLACK",
    "JIRA",
    "GITHUB",
    "JIRA"
]

cleaned_list = list(set(buggy_list))

print("Buggy List :", buggy_list)
print("Cleaned List :", cleaned_list)


# ============================================================
# PHASE 5 - ACCESS REVOCATION
# ============================================================

print("\n")
print("=" * 60)
print("                ACCESS REVOCATION")
print("=" * 60)


while True:

    EMP = input(
        "Enter Employee ID : "
    ).strip().upper()

    EMP1 = employees.get(EMP)

    if EMP1 is not None:
        print("✅ Employee Verified")
        break

    print("🚫 Employee not found.")


while True:

    print("\nCurrent Access :", EMP1["access"])

    Tool = input(
        "Enter the tool you want to revoke : "
    ).strip().upper()

    if Tool in tools:
        break

    print("🚫 Invalid Tool.")


if Tool not in EMP1["access"]:

    print(
        "⚠️ Employee does not have access to",
        Tool
    )

else:

    position = EMP1["access"].index(Tool)

    print(
        "Found",
        Tool,
        "at position",
        position + 1
    )

    EMP1["access"].remove(Tool)

    print(
        "UPDATED ACCESS :",
        EMP1["access"]
    )

    revocation_log = (
        EMP,
        Tool,
        "Revoked",
        "2026-09-02"
    )

    log.append(revocation_log)

    print(
        "Revocation Logged :",
        revocation_log
    )


# ---------------- LOG ANALYSIS ----------------

print("\n")
print("------------- ACCESS LOG ANALYSIS -------------")

print("Total Log Entries :", len(log))

if len(log) > 0:

    print("\nFirst Entry :", log[0])
    print("Last Entry  :", log[-1])

    print("\nRecent Entries :")

    recent = log[-3:]

    for entry in recent:
        print(entry)


# ---------------- COPY / SORT / REVERSE ----------------

log1 = log.copy()

log1.sort()

print("\nSorted Log :")

for entry in log1:
    print(entry)


log1.reverse()

print("\nReversed Log :")

for entry in log1:
    print(entry)


if len(log1) > 0:

    popped_entry = log1.pop()

    print("\nPopped Entry :", popped_entry)


# ============================================================
# PHASE 6 - EMPLOYEE RECORD UPDATE
# ============================================================

print("\n")
print("=" * 60)
print("              EMPLOYEE RECORD UPDATE")
print("=" * 60)


while True:

    EMP2 = input(
        "Enter Employee ID : "
    ).strip().upper()

    EMP3 = employees.get(EMP2)

    if EMP3 is not None:
        print("✅ Employee Verified")
        break

    print("🚫 No employee found.")


print("\nCurrent Record :")

print("Fields :", EMP3.items())
print("Available Fields :", list(EMP3.keys()))


# ---------------- UPDATE ROLE ----------------

update_role = input(
    "\nEnter New Role "
    "(Press Enter to keep current role) : "
).strip().title()


if update_role == "":
    print("Role update skipped.")

elif update_role in valid_roles:

    EMP3["role"] = update_role

    EMP3["access"] = roles_permission[update_role].copy()

    print("✅ Role Updated :", update_role)

    print(
        "New Access :",
        EMP3["access"]
    )

else:

    print("🚫 Invalid Role.")


# ---------------- PHONE UPDATE ----------------

phone = input(
    "\nEnter Phone Number "
    "(Press Enter to skip) : "
).strip()


if phone == "":
    print("Phone update skipped.")

elif len(phone) == 10 and phone.isdigit():

    EMP3["phone"] = phone

    print("✅ Phone Number Updated :", phone)

else:

    print("🚫 Invalid Phone Number.")


# ---------------- REMOVE FIELD ----------------

field = input(
    "\nEnter the field you want to remove "
    "(Press Enter to skip) : "
).strip()


if field == "":
    print("Field removal skipped.")

else:

    removed = EMP3.pop(
        field,
        "Field not found"
    )

    print(
        "Removed",
        field,
        ":",
        removed
    )


print("\nUpdated Keys :", list(EMP3.keys()))
print("Updated Values :", list(EMP3.values()))


# ============================================================
# PHASE 7 - NEW JOINING
# ============================================================

print("\n")
print("=" * 60)
print("                    NEW JOINING")
print("=" * 60)


while True:

    EMP4 = input(
        "Enter New Employee ID : "
    ).strip().upper()

    if (
        len(EMP4) == 4
        and EMP4.startswith("E")
        and EMP4[1:].isdigit()
    ):

        if EMP4 not in employees:
            break

        print("🚫 Employee ID already exists.")

    else:

        print("🚫 Invalid Employee ID.")
        print("Example : E104")


while True:

    name_1 = input(
        "Enter Name : "
    ).strip()

    name_parts = name_1.split()

    if len(name_parts) == 2:

        if (
            name_parts[0].isalpha()
            and name_parts[1].isalpha()
        ):
            name_1 = (
                name_parts[0].title()
                + " "
                + name_parts[1].title()
            )
            break

    print("🚫 Enter First Name and Last Name.")


while True:

    role_1 = input(
        "Enter Role : "
    ).strip().title()

    if role_1 in valid_roles:
        break

    print("🚫 Invalid Role.")
    print("Available Roles :", valid_roles)


email_1 = (
    name_1.replace(" ", "").lower()
    + "@pythongurukool.com"
)


# Copy Aarav's access without affecting Aarav

access_1 = employees["E101"]["access"].copy()

print(
    "\nNew joinee",
    name_1,
    "has copied access from Aarav."
)

print("Copied Access :", access_1)

employees[EMP4] = {
    "name": name_1,
    "role": role_1,
    "access": access_1,
    "email": email_1
}


print("\nNew Employee Created :")
print(employees[EMP4])

print("\nAarav's Access :")
print(employees["E101"]["access"])

print("\nNew Employee Access :")
print(employees[EMP4]["access"])

print(
    "\nThis proves that Aarav's access is not affected."
)


# ============================================================
# PHASE 8 - FINAL REPORT
# ============================================================

print("\n")
print("=" * 70)
print(
    "ACCESS GUARD -- FINAL REPORT".center(70)
)
print("=" * 70)

print("PYTHONGURUKOOL".center(70))
print()

print(
    f"{'ID':<8}"
    f"{'NAME':<22}"
    f"{'ROLE':<15}"
    f"{'TOTAL':<8}"
    f"ACCESS"
)

print("-" * 70)


for employee_id, data in employees.items():

    access_text = " | ".join(data["access"])

    print(
        f"{employee_id:<8}"
        f"{data['name']:<22}"
        f"{data['role']:<15}"
        f"{len(data['access']):<8}"
        f"{access_text}"
    )


print("=" * 70)

print(
    "Total Employees :",
    len(employees),
    "| Total Tools :",
    len(tools),
    "| Log Entries :",
    len(log)
)

print("\n")
print("-" * 25, "ACCESS LOG", "-" * 25)

print(
    f"{'EMP ID':<10}"
    f"{'TOOL':<22}"
    f"{'STATUS':<12}"
    f"{'DATE'}"
)

print("-" * 60)


for entry in log:

    print(
        f"{entry[0]:<10}"
        f"{entry[1]:<22}"
        f"{entry[2]:<12}"
        f"{entry[3]}"
    )


print("-" * 60)

print("Report generated by AccessGuard v1.0")
print("Confidential -- INTERNAL USE ONLY")

print("\n")
print("=" * 70)
print("                 PROGRAM ENDED")
print("=" * 70)
