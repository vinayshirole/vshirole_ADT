from flask import Flask, render_template, request, redirect,url_for
import mysql.connector
import pandas as pd

app = Flask(__name__)

mydb = {
  'host':"vinayinstance.c3eo642a4kqa.us-east-2.rds.amazonaws.com",
  'user':"admin",
  'password':"root1234",
  'port':'3306',
  'database' : 'vshirole_ADT_Final'
}


# Establish MySQL Connection
def get_db_connection():
    conn = mysql.connector.connect(**mydb)
    return conn

query = 'USE vshirole_ADT_Final'

conn = get_db_connection()
cur = conn.cursor()
cur.execute(query)


# Route for Landing page
@app.route('/',methods=['GET','POST'])
def home():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST' and 'search' in request.form:
        search_query = request.form['search']
        cursor.execute('SELECT * FROM walmart WHERE `Product line` LIKE %s',
                       ('%' + search_query + '%',))
    else:
        cursor.execute('SELECT * FROM walmart  order by `Invoice ID`')

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    #rows = pd.read_sql(query,conn).to_dict(orient='records')
    return render_template('index.html', rows=rows)


# Data insertion route
@app.route('/dataInsertion')
def data_insertion():
    return render_template('dataInsertion.html')


# Inserting new records
@app.route('/insert', methods=['POST'])
def insert():
    form_data = request.form
    pre_tax = float(form_data['unitPrice']) * int(form_data['quantity'])
    tax = pre_tax * 0.05
    total = tax + pre_tax
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        # SQL Insert Query
        query = f'''
            INSERT INTO walmart (`Invoice ID`, Branch, City, `Customer type`, `Product line`, `Unit price`, Quantity, `Tax 5%`, Total, Date, Payment, Rating)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        values = (
            form_data['invoiceId'], form_data['branch'], form_data['city'],
            form_data['customerType'], form_data['productLine'],
            form_data['unitPrice'], form_data['quantity'], tax,
            total, form_data['date'], form_data['payment'], form_data['rating']
        )
        
        cursor.execute(query, values)
        connection.commit()

        # Check if the insertion was successful
        if cursor.lastrowid:
            print('Successfully inserted ID', cursor.lastrowid)
        else:
            print('Insertion failed')

    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        # You might want to log this error or show it to the user

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

    return redirect(url_for('home'))


# Editing existing records
@app.route('/edit_entry/<int:invoice_id>',methods=['POST','GET'])
def edit_entry(invoice_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        form_data = request.form
        # print(form_data)
        pre_tax = float(form_data['Unit price']) * int(form_data['Quantity'])
        tax = pre_tax * 0.05
        total = tax + pre_tax
        # print(total)
        query = '''
        UPDATE walmart
        SET Branch = %s, City = %s, `Customer type` = %s, `Product line` = %s, 
            `Unit price` = %s, Quantity = %s, `Tax 5%` = %s, Total = %s, 
            Date = %s, Payment = %s, Rating = %s
        WHERE `Invoice ID` = %s'''
        # print(query)
        values = ( form_data['branch'], form_data['city'], form_data['customerType'],form_data['productLine'], form_data['Unit price'],form_data['Quantity'], tax, total, form_data['Date'],form_data['Payment'], form_data['Rating'], invoice_id )
        # print(query, values)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('home'))
    

    cursor.execute("SELECT * FROM walmart WHERE `Invoice ID` = %s", (invoice_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template ("editEntry.html", row=row)


@app.route('/delete/<int:invoice_id>', methods=['POST','GET'])
def delete_entry(invoice_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # print(invoice_id)
    # print("DELETE FROM walmart WHERE `Invoice ID` = %s", (invoice_id,))
    cursor.execute("DELETE FROM walmart WHERE `Invoice ID` = %s", (invoice_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(host='0.0.0.0',port = '8000')

