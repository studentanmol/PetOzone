from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from  flask_mysqldb  import  MySQL
import  MySQLdb.cursors
import os
from functools import wraps
from trie import Trie

app = Flask(__name__)

sql_password = os.getenv('sql_password')

app.secret_key  =  'supersecretkey'

mysql  =  MySQL(app) 
app.config['MYSQL_HOST']  =  'localhost' 
app.config['MYSQL_USER']  =  'root' 
app.config['MYSQL_PASSWORD']  =  sql_password
app.config['MYSQL_DB']  =  'dbms_project'


app.config["TEMPLATES_AUTO_RELOAD"] = True

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.template_filter()
def rupees(value):
    """Format value as Rupees"""
    #rupee =  u"\u20B9"
    return (u"\u20B9"f"{value:,.2f}")


# User will login 
@app.route("/login", methods=["GET","POST"])
def login():

    # Clear sessions 
    session.clear()

    #If user submitted login form
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")


        # If username was not submitted
        if not username:
            return render_template("apology.html",top=400,bottom="must provide username")
        
        # If password was not submitted
        elif not password:
            return render_template("apology.html",top=400,bottom="must provide password")
        
        # Establish connection with server
        cursor  =  mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Query database
        cursor.execute("SELECT * FROM customer WHERE username = %s AND password = %s;",([username],[password]))

        # Fetch query
        records = cursor.fetchall()

        # Check if user exists
        if len(records) != 1:
            return render_template("apology.html",top=400,bottom="invalid username/password")
        
        # Remember user
        session["user_id"] = records[0]["cust_id"]

        # User should get home page
        return redirect("/")

    # If user visits by GET method
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register",methods=["GET","POST"])
def register():
    """ To register user """

    if request.method == "POST":

        # Get value iserted in input field
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        username = request.form.get("username")
        email = request.form.get("email")
        contact_no = request.form.get("contact_no")
        password = request.form.get("password")

        # Test cases
        if not firstname:
            return render_template("apology.html",top=400,bottom="must provide firstname")
        elif not lastname:
            return render_template("apology.html",top=400,bottom="must provide lastname")
        elif not username:
            return render_template("apology.html",top=400,bottom="must provide username")
        elif not email:
            return render_template("apology.html",top=400,bottom="must provide email")
        elif not contact_no or len(contact_no) != 10:
            return render_template("apology.html",top=400,bottom="must provide conact no.")
        elif not password:
            return render_template("apology.html",top=400,bottom="must provide password")
        elif password != request.form.get("confirm_password"):
            return render_template("apology.html",top=400,bottom="password must be same")
        
        # Establish connection with server
        cursor  =  mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Get list of usernames
        cursor.execute("SELECT * FROM customer WHERE username = %s",[username])
        usernames = cursor.fetchall()

        # Check is username is unique
        if len(usernames) > 0:
            return render_template("apology.html",top=400,bottom="username already exists")
        
        # Add new user to customer taable
        cursor.execute('INSERT INTO customer(firstname,lastname,contact_no,email,username,password) VALUES(%s,%s,%s,%s,%s,%s);',([firstname],[lastname],[contact_no],[email],[username],[password]))

        # Commit changes to customer table
        mysql.connection.commit()
        
        # Send user to log in page
        return redirect("/login")
    
    # If user visist by GET method
    else:
        return render_template("register.html")
        
@app.route("/")
def index():
    """Show dog and cat choice with description"""
    return render_template("index.html")



@app.route("/dogs",methods=["GET","POST"])
@login_required
def dogs():
    """Show Products of Dogs"""
    if request.method == "POST":
        cursor  =  mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute("SELECT prod_sub_id FROM prod_sub;")
        ids = cursor.fetchall()
        for row in ids:
            count = 0
            if int(request.form['submit_button']) == (row['prod_sub_id']):
                cursor.execute("SELECT prod_id FROM product WHERE prod_sub_id=%s",[row['prod_sub_id']])
                prod_id = cursor.fetchone()
                cursor.execute("SELECT * FROM cart WHERE cust_id=%s AND prod_id=%s",([session['user_id']],[prod_id['prod_id']]))
                duplicate = cursor.fetchall()
                if len(duplicate) == 1:
                    cursor.execute("UPDATE cart SET quantity=quantity+1 WHERE cust_id=%s AND prod_id=%s",([session['user_id']],[prod_id['prod_id']]))
                else:
                    cursor.execute("INSERT INTO cart(prod_id,cust_id,quantity) VALUES(%s,%s,%s);",([prod_id['prod_id']],[session["user_id"]],[1]))
                mysql.connection.commit()
                break
            
        return redirect("/cart")

    else:
        cursor  =  mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute("select distinct uses.pet_id,pets.pet_type,product.prod_sub_id,prod_sub.name,product.price,product.expiry_date from product,prod_sub,uses,pets where product.prod_sub_id= prod_sub.prod_sub_id AND pets.pet_id=uses.pet_id AND uses.prod_id=product.prod_id AND uses.pet_id=10;")
        prods = cursor.fetchall()
        return render_template("dog.html",prods=prods,name="dogs")


@app.route("/cats",methods=["GET","POST"])
@login_required
def cats():
    """Show Products of Cats"""
    if request.method == "POST":
        cursor  =  mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute("SELECT prod_sub_id FROM prod_sub;")
        ids = cursor.fetchall()
        for row in ids:
            if int(request.form['submit_button']) == (row['prod_sub_id']):
                cursor.execute("SELECT prod_id FROM product WHERE prod_sub_id=%s",[row['prod_sub_id']])
                prod_id = cursor.fetchone()
                cursor.execute("SELECT * FROM cart WHERE cust_id=%s AND prod_id=%s",([session['user_id']],[prod_id['prod_id']]))
                duplicate = cursor.fetchall()
                if len(duplicate) == 1:
                    cursor.execute("UPDATE cart SET quantity=quantity+1 WHERE cust_id=%s AND prod_id=%s",([session['user_id']],[prod_id['prod_id']]))
                else:
                    cursor.execute("INSERT INTO cart(prod_id,cust_id,quantity) VALUES(%s,%s,%s);",([prod_id['prod_id']],[session["user_id"]],[1]))
                mysql.connection.commit()
                break
            
        return redirect("/cart")

    else:
        cursor  =  mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute("select distinct uses.pet_id,pets.pet_type,product.prod_sub_id,prod_sub.name,product.price,product.expiry_date from product,prod_sub,uses,pets where product.prod_sub_id= prod_sub.prod_sub_id AND pets.pet_id=uses.pet_id AND uses.prod_id=product.prod_id AND uses.pet_id=20;")
        prods = cursor.fetchall()
        return render_template("cat.html",prods=prods)



@app.route("/cart",methods=["GET","POST"])
@login_required
def cart():
    """Show users their cart"""
    if request.method == "POST":
        if request.form["address"] == "address":
            return redirect("/address")
        cursor  =  mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT cart_id FROM cart WHERE cust_id=%s;",[session["user_id"]])
        cart_id = cursor.fetchall()
        count=0
        for row in cart_id:
            if int(request.form["remove_button"]) == row['cart_id']:
                cursor.execute("DELETE FROM cart WHERE cart_id=%s;",[row['cart_id']])
                mysql.connection.commit()
                count = 1
                break
        
        if count == 1:
            return redirect("/cart")
        
    else:
        cursor  =  mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute('SELECT cart_id, name,price,quantity,expiry_date,product.prod_id FROM product JOIN prod_sub ON product.prod_sub_id = prod_sub.prod_sub_id JOIN cart ON cart.prod_id = product.prod_id WHERE cart.cust_id = %s;',[session["user_id"]]) 
        records = cursor.fetchall()
        if len(records) == 0:
            return render_template("example.html",record="Your cart is empty")
        cursor.execute('SELECT SUM(price*quantity) AS total FROM product JOIN prod_sub ON product.prod_sub_id = prod_sub.prod_sub_id JOIN cart ON cart.prod_id = product.prod_id WHERE cart.cust_id = %s;',[session["user_id"]])
        total = cursor.fetchone()
        cursor.execute('SELECT firstname FROM customer WHERE cust_id=%s',[session["user_id"]])
        name = cursor.fetchone()
        return render_template("cart.html",records=records,name=name,total=total)


@app.route("/address",methods = ["GET","POST"])
@login_required
def address():
    """Take address from user and confirm order"""
    if request.method == "POST":
        flat = request.form.get("flat")
        building = request.form.get("building")
        street = request.form.get("street")
        city = request.form.get("city")
        pincode = request.form.get("pincode")
        lname = request.form.get("lname")
        method = request.form.get("payment_mode")

        if not building:
            return render_template("apology.html",top=400,bottom="must enter building")
        elif not street:
            return render_template("apology.html",top=400,bottom="must enter street")
        elif not city:
            return render_template("apology.html",top=400,bottom="must enter city")
        elif not pincode or len(pincode) !=6:
            return render_template("apology.html",top=400,bottom="must enter correct pincode")
        elif not lname:
            return render_template("apology.html",top=400,bottom="must enter location name")
        elif not flat:
            return render_template("apology.html",top=400,bottom="must enter flat number")
        
        cursor  =  mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute("INSERT INTO delivery_location(location_name,building_name,area_name,city,pincode,address_name,cust_id) VALUES(%s,%s,%s,%s,%s,%s,%s)",([flat],[building],[street],[city],[pincode],[lname],[session["user_id"]]))
        mysql.connection.commit()
        cursor.execute('SELECT delivery_location_id AS id FROM delivery_location WHERE address_name=%s AND cust_id=%s;',([lname],[session["user_id"]]))
        id = cursor.fetchone()
        cursor.execute('SELECT name,price,quantity,expiry_date,product.prod_id AS product_id FROM product JOIN prod_sub ON product.prod_sub_id = prod_sub.prod_sub_id JOIN cart ON cart.prod_id = product.prod_id WHERE cart.cust_id = %s;',[session["user_id"]]) 
        records = cursor.fetchall()
        for row in records:
            cursor.execute('INSERT INTO orders(order_date,payment_mode,invoice_amt,quantity,delivery_location_id,cust_id,prod_id) VALUES(CURDATE(),%s,%s,%s,%s,%s,%s);',([method],[row['price']*row['quantity']],[row['quantity']],[id['id']],[session["user_id"]],[row['product_id']]))
            mysql.connection.commit()
        cursor.execute('DELETE FROM cart WHERE cust_id=%s',[session['user_id']])
        mysql.connection.commit()
        
        return render_template("confirm.html")
    else:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT SUM(price*quantity) AS total FROM product JOIN prod_sub ON product.prod_sub_id = prod_sub.prod_sub_id JOIN cart ON cart.prod_id = product.prod_id WHERE cart.cust_id = %s;',[session["user_id"]])
        total = cursor.fetchone()
        return render_template("address.html",total=total)


@app.route("/orders")
@login_required
def orders():
    cursor  =  mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT DISTINCT O.quantity,O.invoice_amt,O.order_id,P.name AS product_name,O.order_date,S.shipment_status, date_add(O.order_date, INTERVAL 5 DAY) AS delivery_date from orders O,delivery_location D,prod_sub P,shipment S,product WHERE S.order_id=O.order_id AND O.delivery_location_id=D.delivery_location_id AND O.prod_id=product.prod_id AND product.prod_sub_id=P.prod_sub_id AND O.cust_id=%s;',[session["user_id"]]) 
    order = cursor.fetchall()
    if len(order) == 0:
        return render_template("example.html",record="You don't have any orders")
    for row in order:
        if row["shipment_status"] == None:
            shipment = 'Delivered'
        else:
            shipment = row["shipment_status"]
    
    return render_template("orders.html",order=order,shipment=shipment)

@app.route("/example")
def example():
    cursor  =  mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute('SELECT name FROM prod_category;')
    key = "ppl"
    cursor.execute("SELECT DISTINCT uses.pet_id,pets.pet_type,product.prod_sub_id,prod_sub.name,product.price,product.expiry_date FROM product,prod_sub,uses,pets where product.prod_sub_id= prod_sub.prod_sub_id AND pets.pet_id=uses.pet_id AND uses.prod_id=product.prod_id AND prod_sub.name LIKE %s;",['%' + key + '%'])
    records = cursor.fetchall()
    #usernames = cursor.execute("SELECT * FROM customer WHERE username = %s",["pranati01"])
    #records = cursor.fetchall()
    return render_template("example.html",records=records)

@app.route("/search",methods=["GET","POST"])
def search():
    if request.method=="POST":
        """If user submits a search"""
        prods=()
        cursor  =  mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT DISTINCT prod_sub.name FROM product,prod_sub,uses,pets WHERE product.prod_sub_id= prod_sub.prod_sub_id AND pets.pet_id=uses.pet_id AND uses.prod_id=product.prod_id;")
        prods = cursor.fetchall()
        keys = set()
        for i in range(len(prods)):
            keys.add(prods[i]['name'])
        
        key = request.form.get("search")
        key = key.capitalize()

        if key == "Dog" or key == "Dogs":
            return redirect("/dogs")
        
        elif key == "Cat" or key=="Cats":
            return redirect("/cats")
        
        cursor.execute('SELECT name FROM prod_category;')
        category = cursor.fetchall()
        records = -1
        for i in range(4):
            if category[i]['name'] == key:
                cursor.execute("SELECT DISTINCT uses.pet_id,pets.pet_type,product.prod_sub_id,prod_sub.name,product.price,product.expiry_date FROM product,prod_sub,uses,pets,prod_category WHERE product.prod_sub_id= prod_sub.prod_sub_id AND pets.pet_id=uses.pet_id AND uses.prod_id=product.prod_id AND prod_sub.prod_category_id = (SELECT prod_category_id FROM prod_category WHERE name=%s)",[category[i]['name']])
                records=cursor.fetchall()
                break
        
        if records != -1:
            return render_template("dog.html",prods=records,name="pets",key=key)
        
        # creating trie object
        t = Trie()
        
        # creating the trie structure with the
        # given set of strings.
        t.formTrie(keys)
        
        # autocompleting the given key using
        # our trie structure.
        comp = t.printAutoSuggestions(key)
        
        if comp == -1:
            return render_template("apology.html",top=400,bottom="No other products found with this word")
        elif comp == 0:
            cursor.execute("SELECT DISTINCT uses.pet_id,pets.pet_type,product.prod_sub_id,prod_sub.name,product.price,product.expiry_date FROM product,prod_sub,uses,pets where product.prod_sub_id= prod_sub.prod_sub_id AND pets.pet_id=uses.pet_id AND uses.prod_id=product.prod_id AND prod_sub.name LIKE %s;",['%' + key + '%'])
            records = cursor.fetchall()
            if len(records) == 0:
                return render_template("apology.html",top=400,bottom="No product found with this word")
            return render_template("dog.html",prods=records,name="pets",key=key)
        prods=[]
        for name in comp:
            cursor.execute("SELECT DISTINCT uses.pet_id,pets.pet_type,product.prod_sub_id,prod_sub.name,product.price,product.expiry_date FROM product,prod_sub,uses,pets where product.prod_sub_id= prod_sub.prod_sub_id AND pets.pet_id=uses.pet_id AND uses.prod_id=product.prod_id AND prod_sub.name LIKE %s;",[name])
            prods.append(cursor.fetchone())
        prods=tuple(prods)
        return render_template("dog.html",prods=prods,name="pets",key=key)
    else:
        return redirect("/")

