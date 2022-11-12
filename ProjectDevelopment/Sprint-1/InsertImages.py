jpg_file="/home/sampath/Documents/projects/IBM/ProjectDevelopment/Sprint-1/static/images/jumpsuits.webp"  # path to the image file
import ibm_db

try:
    conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=b1bc1829-6f45-4cd4-bef4-10cf081900bf.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32304;SECURITY=SSL;UID=mkb48397;PWD=4joZwnJswX0BRnwT",'','')
    print(conn)
    print("connection successfull")
except:
    print("Error in connection, sqlstate = ")
    errorState = ibm_db.conn_error()
    print(errorState)

insert_sql = "INSERT INTO PROD_IMGS(prod_id,image) values(8,?)"
try:
    stmt = ibm_db.prepare(conn, insert_sql)
    print("Successfully prepared the insert statement")
except:
    print("Failed to compile the insert statement")
    print(ibm_db.stmt_errormsg(stmt))
    ibm_db.close(conn)

# link a file-name to the parameter-marker of the insert-statement (target column is BLOB)

try:
    rc = ibm_db.bind_param(stmt, 1, jpg_file, ibm_db.PARAM_FILE,ibm_db.SQL_BLOB )
    print("Bind returned: "+str(rc))
    print("Successfully bound the filename to the parmameter-marker")

except:
    # print("Bind returned: "+str(rc))
    print("Failed to bind the input parameter file")
    print(ibm_db.stmt_errormsg(stmt))
    ibm_db.close(conn)

try:
    ibm_db.execute(stmt)
    print("Successfully inserted jpg file into blob column")
except:
    print("Failed to execute the insert to blob column")
    print(ibm_db.stmt_errormsg(stmt))