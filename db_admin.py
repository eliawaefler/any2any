from neon import *
import uuid
import os

def create_empty_rules_table():
    table_name = "rules"
    columns = {
        "guid": "UUID PRIMARY KEY",  # Unique identifier
        "rule_name": "VARCHAR(1000)",  # the rule to execute (NAME)
        "rule_info": "VARCHAR(1000)",
        "rule_family": "VARCHAR(1000)",
        "rule_param_type": "VARCHAR(1000)",
        "created_by": "VARCHAR(100)",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }
    print(create_table(CONN, table_name, columns))

def create_empty_users_table():
    table_name = "users"
    columns = {
        "guid": "UUID PRIMARY KEY",  # Unique identifier
        "username": "VARCHAR(100) NOT NULL",  # Username (required)
        "email": "VARCHAR(255) NOT NULL",  # Email (required)
        "pw_hash": "VARCHAR(255) NOT NULL",  # Password hash (required)
        "first_name": "VARCHAR(100)",  # First name (optional)
        "last_name": "VARCHAR(100)",  # Last name (optional)
        "salt": "VARCHAR(255) NOT NULL",  # Salt for password hashing (required)
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"  # Auto-timestamp
    }

    print(create_table(CONN, table_name, columns))


def any2any_db_hard_reset():
    drop_tables_with_pattern(CONN) # drops all user created tables
    drop_tables_with_pattern(CONN, "u") #drops rUles and Users

def any2any_users_reset():
    for user in read_db(CONN, "users"):
        username = user[1]
        print(username)
        drop_tables_with_pattern(CONN, f"{username}_")
        create_table(CONN, f"{username}_Mapper", {
                                        "guid": "UUID PRIMARY KEY",  # Unique identifier
                                        "name": "VARCHAR(1000)",
                                        "data": "VARCHAR(1000000)"
                                    })
        create_table(CONN, f"{username}_Quelle", {
                                    "guid": "UUID PRIMARY KEY",  # Unique identifier
                                    "API": "VARCHAR(255) NOT NULL",
                                    "file_name": "VARCHAR(255) NOT NULL",
                                    "entity_name": "VARCHAR(255) NOT NULL",
                                    "entity_attributes": "JSONB NOT NULL",
                                    "added_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"  # Auto-timestamp
                                    })
        create_table(CONN, f"{username}_Ziel", {
                                    "guid": "UUID PRIMARY KEY",  # Unique identifier
                                    "API": "VARCHAR(255) NOT NULL",
                                    "file_name": "VARCHAR(255) NOT NULL",
                                    "entity_name": "VARCHAR(255) NOT NULL",
                                    "entity_attributes": "JSONB NOT NULL",
                                    "added_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"  # Auto-timestamp
                                    })
        create_table(CONN, f"{username}_FDM", {
                                    "guid": "UUID PRIMARY KEY",  # Unique identifier
                                    "entity_name": "VARCHAR(255) NOT NULL",  #
                                    "entity_attributes": "JSONB NOT NULL",
                                    "added_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"  # Auto-timestamp
                                    })
        write_to_db(CONN, f"{username}_FDM", {
                                    "guid": str(uuid.uuid4()),  # Unique identifier
                                    "entity_name": "1",
                                    "entity_attributes": [],
                                    })

def add_user():

    new_user = {
        "guid": str(uuid.uuid4()),
        "username": "e2",
        "email": "elia.w2aefler@gmail.com",  # Email (required)
        "pw_hash": "1234",  # Password hash (required)
        "first_name": "Elia",  # First name (optional)
        "last_name": "WAE",  # Last name (optional)
        "salt": "1234",  # Salt for password hashing (required)
    }
    write_to_db(CONN, "users", new_user)


def add_rules():

    rule1 = {
        "guid": str(uuid.uuid4()),
        "rule_name": "1:1",
        "rule_family": "basic",
        "rule_info": "direkter übertrag ohne manipulation",
        "rule_param_type": "none",
        "created_by": "Elia"
    }
    rule2 = {
        "guid": str(uuid.uuid4()),
        "rule_name": "cut_left",
        "rule_family": "cut",
        "rule_info": "das QUELL attribut wird von links (vorne) beschnitten, der rechte (hintere) teil wird behalten",
        "rule_param_type": "num",
        "created_by": "Elia"
    }
    rule3 = {
        "guid": str(uuid.uuid4()),
        "rule_name": "cut_right",
        "rule_family": "cut",
        "rule_info": "das QUELL attribut wird von rechts (hinten) beschnitten, der linke (vordere) teil wird behalten",
        "rule_param_type": "num",
        "created_by": "Elia"
    }
    rule4 = {
        "guid": str(uuid.uuid4()),
        "rule_name": "multiply",
         "rule_family": "math",
        "rule_info": "wird mit dem parameter multipliziert",
        "rule_param_type": "num",
        "created_by": "Elia"
    }
    rule5 = {
        "guid": str(uuid.uuid4()),
        "rule_name": "add",
        "rule_family": "math",
        "rule_info": "die param zahl wird dazu addiert (kann auch minus sein)",
        "rule_param_type": "num",
        "created_by": "Elia"
    }
    rule6 = {
        "guid": str(uuid.uuid4()),
        "rule_name": "concat",
        "rule_family": "base",
        "rule_info": "mehrere Quellen werden in diesem Zielattribut zusammengefügt. "
                     "der parameter bestimmt die Reihenfolge (kleine zahlen zuerst)",
        "rule_param_type": "num",
        "created_by": "Elia"
    }

    rule7 = {
        "guid": str(uuid.uuid4()),
        "rule_name": "cut_sep_left",
        "rule_family": "cut",
        "rule_info": "der quell string wird beim Trennzeichen (seperator) getrennt. der LINKE Teil wird entfernt, "
                     "der RECHTE teil wird behalten.",
        "rule_param_type": "str",
        "created_by": "Elia"
    }
    rule8 = {
        "guid": str(uuid.uuid4()),
        "rule_name": "cut_sep_right",
        "rule_family": "cut",
        "rule_info": "der quell string wird beim Trennzeichen (seperator) getrennt. der RECHTE Teil wird entfernt, "
                     "der LINKE teil wird behalten.",
        "rule_param_type": "str",
        "created_by": "Elia"
    }

    for new_rule in [rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8]: #rule1, rule2, rule3
        write_to_db(CONN, "rules", new_rule)


if __name__ == "__main__":
    CONN = os.environ["NEON_URL_any"]

    # to DROP ALL users tables
    #print(f"Dropped tables: {drop_tables_with_pattern(CONN, pattern="_")}")
    any2any_users_reset()
    #users_db = read_db(CONN, "users", printout=False)
    #print(users_db)
