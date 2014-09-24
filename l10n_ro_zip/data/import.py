import csv
import psycopg2

conn_string = "dbname='db2' user='openpg' password='openpgpwd'"

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

reader = csv.reader(open('products_import.csv','rb'))

for row in reader:
    print row[1]

    statement = "INSERT INTO product_template (name,standard_price,list_price,mes_type,uom_id,uom_po_id," \
    "type,procure_method,cost_method,categ_id,supply_method,sale_ok) VALUES ('" + row[1] + "'," \
    + str(row[2]) + "," + str(row[2]) + ",'fixed',1,1,'product','make_to_stock','standard',1,'buy',True) RETURNING id"

    cursor.execute(statement)
    conn.commit()
    templateid = cursor.fetchone()[0]

    statement = "INSERT INTO product_product (product_tmpl_id,default_code,active,valuation) VALUES \
    (" + str(templateid) + ",'" + row[0] + "',True,'manual_periodic')"

    cursor.execute(statement)
    conn.commit()
