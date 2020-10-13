import sys
import MySQLdb


def connect_to_db(user, passw, db):
    db = MySQLdb.Connection(
        user=user,
        passwd=passw,
        db=db
    )
    return db

def get_experiment(name, cursor):
    try:
        cursor.execute("""SELECT id FROM NetExplorer_experiment 
                          WHERE name = %s""", (name, ))
        r = cursor.fetchone()
        return r[0]
    except TypeError:
        sys.stderr.write("Experiment %s does not exist in database!\n" % name)


def get_reactome(code, experiment, cursor):
    try:
        cursor.execute("""SELECT id FROM NetExplorer_reactome 
                          WHERE reactome_id = %s AND experiment_id = %s""", (code, experiment))
        r = cursor.fetchone()
        return r[0]
    except TypeError:
        sys.stderr.write("Reactome id does not exist %s!\n" % code)


def get_link(reg, tar, experiment, cursor):
    try:
        cursor.execute("""SELECT id FROM NetExplorer_regulatorylinks
                          WHERE regulator = %s AND target = %s AND experiment_id = %s""", (reg, tar, experiment))
        r = cursor.fetchone()
        return r[0]
    except TypeError as err:
        print("WITH ERROR: %s -> %s" % (reg, tar))
        print(err)

def upload_reactomes(file, cursor):
    with open(file, "r") as fh:
        for line in fh:
            line = line.strip()
            code, name, upper_name, exp_name = line.split("\t")
            experiment = get_experiment(exp_name, cursor)
            cursor.execute("""
                INSERT INTO NetExplorer_reactome (name, search_name, reactome_id, experiment_id)
                VALUES (%s, %s, %s, %s)""", (name, upper_name, code, experiment))

def upload_reactome_links(file, cursor):
    with open(file, "r") as fh:
        for line in fh:
            line = line.strip()
            code, name, upper_name, exp_name, r, t = line.split("\t")
            experiment = get_experiment(exp_name, cursor)
            link = get_link(r, t, experiment, cursor)
            reactome = get_reactome(code, experiment, cursor)
            cursor.execute("""
                INSERT INTO NetExplorer_reactomelinks (reactome_id, regulatorylink_id)
                VALUES (%s, %s)""", (reactome, link))




db = connect_to_db(sys.argv[1], sys.argv[2], sys.argv[3])
cursor = db.cursor()

#upload_reactomes(sys.argv[4], cursor)
upload_reactome_links(sys.argv[5], cursor)
db.commit()
