import os
import sys

timestamp = "2021-06-16 16:45:00.000"
file_dir = sys.argv[1]
partial_file_suffix = sys.argv[2]
alignment_file_suffix = sys.argv[3]
alignment_mime_type = sys.argv[4]
index_file_suffix = sys.argv[5]
index_file_mime_type = sys.argv[6]
md5_file = sys.argv[7]

def create_md5_dict(md5_file):
    d = {}
    for line in open(md5_file, "r"):
        ls = line.strip().split()
        filename = os.path.basename(ls[1])
        checksum = ls[0]
        d[filename] = checksum
    return d

def fh_setup():
    output_file_path = "populate-drs-dataset.sql"
    output_fh = open(output_file_path, "w")
    output_fh.write("")
    output_fh.close()

    output_fh = open(output_file_path, "a")
    return output_fh

def fh_close(output_fh):
    output_fh.close()

def sql_root_bundle(fh):
    sql = """
/* Create Root Bundle */
INSERT INTO drs_object (id, description, created_time, name, updated_time, version)
VALUES ("cnest.dataset", "CNest Test Dataset", "%s", "cnest.dataset", "%s", "1.0.0");

""" % (timestamp, timestamp)
    fh.write(sql)

def sql_for_single_subject(subject, md5_dict, fh):
    sql = "/* %s */\n" % subject
    fh.write(sql)
    sql_subject_bundle(subject, fh)
    sql_subject_alignment(subject, md5_dict, fh)
    sql_subject_index(subject, md5_dict, fh)

def sql_subject_bundle(subject, fh):
    sql = ""

    # create subject bundle
    sql += """INSERT INTO drs_object (id, description, created_time, name, updated_time, version)
VALUES ("cnest.%s.bundle", "CNest subject bundle: %s", "%s", "cnest.%s.bundle", "%s", "1.0.0");
""" % (subject, subject, timestamp, subject, timestamp)

    # add subject bundle to root bundle
    sql += """INSERT INTO drs_object_bundle VALUES ("cnest.dataset", "cnest.%s.bundle");
""" % (subject)

    fh.write(sql)

def sql_single_file(subject, suffix, filetype, mime_type, md5_dict, fh):
    drs_bundle_id = "cnest.%s.bundle" % subject
    drs_object_id = "cnest.%s.%s" % (subject, filetype)
    size = "0"
    file_name = subject + partial_file_suffix + suffix
    file_path = os.path.join(file_dir, file_name)
    checksum = md5_dict[file_name]
    size = os.path.getsize(file_path)
    
    sql = ""

    # create drsobject
    sql += """INSERT INTO drs_object (id, description, created_time, mime_type, name, size, updated_time, version)
VALUES ("%s", "CNest, %s, %s file", "%s", "%s", "%s", %s, "%s", "1.0.0");
""" % (drs_object_id, subject, filetype, timestamp, mime_type, drs_object_id, size, timestamp)

    # add drsobject to subject bundle
    sql += """INSERT INTO drs_object_bundle VALUES ("%s", "%s");
""" % (drs_bundle_id, drs_object_id)

    # create alias
    sql += """INSERT INTO drs_object_alias VALUES ("%s", "CNEST-%s-%s");
""" % (drs_object_id, subject, filetype.upper())

    # create md5 checksum
    sql += """INSERT INTO drs_object_checksum (drs_object_id, checksum, type) VALUES ("%s", "%s", "md5");
""" % (drs_object_id, checksum)

    # create file access object
    sql += """INSERT INTO file_access_object (drs_object_id, path) VALUES ("%s", "%s");
""" % (drs_object_id, file_path)

    fh.write(sql)

def sql_subject_alignment(subject, md5_dict, fh):
    sql_single_file(subject, alignment_file_suffix, "alignment", alignment_mime_type, md5_dict, fh)

def sql_subject_index(subject, md5_dict, fh):
    sql_single_file(subject, index_file_suffix, "index", index_file_mime_type, md5_dict, fh)

def main():
    # initial setup
    output_fh = fh_setup()
    md5_dict = create_md5_dict(md5_file)

    # create sql for the root bundle
    sql_root_bundle(output_fh)

    # create sql for all subjects, alignment files, index files
    for item in os.popen("ls -1 %s/*.bam | rev | cut -f 1 -d '/' | rev | cut -f 1 -d '.' | uniq" % file_dir):
        subject = item.strip()
        sql_for_single_subject(subject, md5_dict, output_fh)

    # cleanup
    fh_close(output_fh)

if __name__ == "__main__":
    main()
