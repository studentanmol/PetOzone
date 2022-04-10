# PetOzone
PetOzone is a website of shops that allows users to select and buy pet accessories and food from the comfort of their homes. The websitr is made using Flask and SQL.
Website Flow: 
- When a user first visits the website they will be asked to register and provide their details.
- They can then log in to view the homepage of the website. 
- On that home page they can view and add to their cart various accessories and food products for their pets. 
- They can visit their cart to see the products they want to buy and can also remove them.
- Check Out and see the final price to pay along with the items bought.

### MySQL
MySQL server is used as databse to store the data required in making this website. The various tables used are:
* Customer: In this table, we will be storing users data such as cust_id, username, contact_no, password, email. 
We will be storing this information when a user registers on the website & we will be using
this information when a user wants to log in . 

  **Constraints**:  cust_id is primary Key, Contact_no should be 10 digits, Email is UNIQUE. 

* Product : The details and stock of products available on our website will be stored in this table.
Following are the attributes:
, prod_id
, pet_id
, price 
, stock_quantity 
, product_sub_category.

  **Constraints**: prod_id is Primary key, price is Not Null, stock_quantity is Not Null, product_sub_category_id is a Foreign key from table *product*,                sub category, pet_id is Foreign key referencing table *pets*.

* Prod_category: Categories of  products available like food,medicine,clothes and accessories in product table are stored here. Following are the attributes:
, prod_category_id
, prod_name.

  **Constraints**: prod_category_id is primary key, 
prod_name is Not Null.

* Prod_sub_category : Names of categories of products in product_categories are stored here. For example, pedigree in the food category.
Following are the attributes:
, prod_sub_category_id
, name
, prod_category_id.

  **Constraints**: prod_sub_category_id is primary key, 
name is Not Null, product_category_id is the foriegn key referencing table *product_category*.

* Cart :Products chosen by customers to buy are added to carts. Following are the attributes:
, prod_id
, cust_id
, quantity .

  **Constraints**: prod_id is foriegn key referencing table *product*,
cust_id is foreign key referencing table *customer*,
quantity is Not Null.  

* Order : All the details of customers’ final order are stored here.
Following are the attributes:
, order_id
, order_date
, payment_mode
, payment_date
, invoice_amt
, quantity
, delivery_location_id
, cust_id.

  **Constraints**:  order_id is Primary key, payment_mode is Not Null, delivery_location_id is foreign key referencing table *delivery location*, cust_id is foreign
    key referencing table *customers*.

* Shipment: Order shipment details will be stored in this table. Following are the attributes:
, shipment_id
, shipment_date
, shipment_status
, delivery_date
, order_id
, cust_id.

  **Constraints**:  shipment_id is primary key, order_id is Foreign Key referencing *order* table, cust_id is foreign key referencing the *customer* table.

* Delivery Location : Delivery locations entered by users are stored here. Following are the attributes:
, delivery_location_id
, location_name
, address 
, cust_id.

  **Constraints**: delivery_location_id is Primary key, address is Not Null, cust_id is foreign key referencing table *customers*.

* Pets : Pets with their id are stored here
, pet_id
, pet_type.

  **Constraints**: pet_id is primary key, pet_type is not NULL.
  
  ### app.py
  This is where Flask is used to create the website. Its various functions are:
  * login_required() is a decorator that ensures that only logged in users can access a part of the website.
  * rupees() is a Flask filter that will convert the value passed to it to a float with 2 decimal places and add a ruppee sign in front of it.
  * login() function depicts the login route where a form will be displayed to the user via login.html template. On submitting the form if the user is present in the databse then they will be successfully logged in and redirected to the index page otherwise an appropiate error message will be displayed to them.
  * The logout() functions depicting the logout route will log the user out.
  * the register() route will display a form to the user via the register.html template which if correctly submitted will register the user to the website and add their details to the databse. They will then be redirected to the login page.
  * The index() depicts the homepage of the website via index.html which will show dogs and cats as 2 options and on clicking either of them the suers will be redirected to the respective pages.
  * dogs() function depicts the dogs route which will display the products for dogs with title, image, price on each product. Users have an option to add the product to their carts. The appropiate changes are done in the database.
  * cats() function depicts the cats route which will display the products for cats with title, image, price on each product. Users have an option to add the product to their carts. The appropiate changes are done in the database.
  * The cart() function depicting cart route shows the user the products in their cart. Users can remove a product or confirm their order. They will then be redirected to a confirmation page.
  * address() route displays a form for the user to input their address where the order will be delivered. The address is stored in the databse the first time and displayed to the user on multiple uses.
  * order() function depicting order route shows the users the status of their orders, i.e. the orders that have delivered already, are being processed, are on the way,etc.

##### layout.html
This html file contains the layout of the page from which all other html files extend. The page has a navbar at the top. The name of the page is in the top left with the links for register and login in the left. Only a user who has logged in can view the links for products, cart, orders,etc. the rest of the page is according to each html page.
