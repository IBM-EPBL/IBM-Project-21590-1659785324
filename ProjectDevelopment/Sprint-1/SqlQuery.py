import ibm_db
import base64
try:
    conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=b1bc1829-6f45-4cd4-bef4-10cf081900bf.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32304;SECURITY=SSL;UID=mkb48397;PWD=4joZwnJswX0BRnwT",'','')
    print(conn)
    print("connection successfull")
except:
    print("Error in connection, sqlstate = ")
    errorState = ibm_db.conn_error()
    print(errorState)

sql = "SELECT PRODUCTS.ID, PRODUCTS.NAME, PRODUCTS.PRICE, PROD_IMGS.IMAGE FROM PRODUCTS INNER JOIN PROD_IMGS ON PRODUCTS.ID = PROD_IMGS.PROD_ID"
stmt = ibm_db.exec_immediate(conn,sql)
result = ibm_db.fetch_assoc(stmt)
prods = []
while result != False:
    # print("The ID is : ", result["ID"])
    # print("The name is : ", result["NAME"])
    image=base64.b64encode(result["IMAGE"]).decode("utf-8")
    # print("The encoded image is : ",image )
    result.update({"IMAGE":image})
    prods.append(result)
    result = ibm_db.fetch_assoc(stmt)
print(prods)