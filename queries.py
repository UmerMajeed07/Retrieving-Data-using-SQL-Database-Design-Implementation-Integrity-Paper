from db_config import Database


class Queries:
    conn = ""

    def __init__(self):
        db = Database()
        self.conn = db.create_connection()

    def check_shopper(self, shopper_id) -> object:
        """
            Query the shopper details in thr shopper table.

        Args:
            shopper_id: to get shopper details against the shopper id.

        Returns:
              return object details of shopper
        """
        result = None
        try:
            query = f"""SELECT shopper_first_name, shopper_surname FROM shoppers WHERE shopper_id = {shopper_id}"""
            cursor = self.conn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
        except Exception as e:
            pass
        return result

    def get_shopper_basket(self, shopper_id) -> int:
        """
            Query the shopper current basket in the shopper_baskets table.

        Args:
            shopper_id: shopper id in the shopper table.

        Returns:
              return  current basket_id of shopper.
        """
        result = None
        try:
            query = f"""SELECT basket_id FROM shopper_baskets WHERE shopper_id = {shopper_id} AND 
                    DATE(basket_created_date_time) = DATE('now') ORDER BY basket_created_date_time DESC LIMIT 1"""
            cursor = self.conn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()[0]
        except Exception as e:
            pass
        return result

    def get_shopper_orders(self, shopper_id) -> list:
        """
            Query all the shopper orders history and product details in the
            products, seller, shopper & ordered_products table.

        Args:
           shopper_id: shopper id in the shopper table.

        Returns:
             return  current basket_id of shopper.
        """
        result = None
        try:
            query = f"""SELECT o.order_id, strftime('%d-%m-%Y' , o.order_date) AS order_date, 
                    (SELECT product_description FROM products p WHERE p.product_id = op.product_id) 
                    AS product_description,
                    (SELECT seller_name FROM sellers s WHERE s.seller_id = op.seller_id) AS seller_name,
                    op.quantity, '£ ' || ROUND(op.price, 2) AS price, op.ordered_product_status AS order_status
                    FROM shoppers s INNER JOIN  shopper_orders o ON (s.shopper_id = o.shopper_id) 
                    INNER JOIN ordered_products op ON (op.order_id = o.order_id) WHERE
                    s.shopper_id = {shopper_id} ORDER BY o.order_date DESC;"""
            cursor = self.conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
        except Exception as e:
            pass
        return result

    def get_product_categories(self) -> list:
        """
            Query all the categories in the categories table.

        Returns:
            returns list of all categories.
        """
        result = None
        try:
            query = "SELECT category_id, category_description FROM categories"
            cursor = self.conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
        except Exception as e:
            pass
        return result

    def get_products(self, category_id) -> list:
        """
            Query all the products against the provided category_id in the products table.

        Args:
            category_id: category id in the category table,

        Returns:
              returns list of all the products
        """
        result = None
        try:
            query = f"""SELECT product_id, product_description FROM products WHERE category_id = {category_id}
                    AND product_status = 'Available'"""
            cursor = self.conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
        except Exception as e:
            pass
        return result

    def get_sellers(self, product_id) -> list:
        """
            Query the product details and seller selling the product in the seller and product_sellers table.

        Args:
           product_id: product table id.

        Returns:
             returns list of all seller and product details
        """
        result = None
        try:
            query = f"""SELECT ps.seller_id, s.seller_name || '  (£' || ps.price || ')' AS product_description FROM 
                    product_sellers ps INNER JOIN sellers s ON (ps.seller_id = s.seller_id) 
                    WHERE ps.product_id = {product_id}"""
            cursor = self.conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
        except Exception as e:
            pass
        return result

    def get_product_price(self, seller_id, product_id) -> int:
        """
            Query the product price against the product and its seller in the product_sellers table.

        Args:
            product_id: table id of the product.
            seller_id: seller id of the seller.

        Returns:
            returns the price of the product.
        """
        result = None
        try:
            query = f"""SELECT price FROM product_sellers WHERE seller_id = {seller_id} AND product_id = {product_id}"""
            cursor = self.conn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()[0]
        except Exception as e:
            pass
        return result

    def add_basket(self, shopper_id) -> int:
        """
            Query to insert the shopper basket in the shopper_baskets table.

        Args:
            shopper_id: table id of the shopper.

        Returns:
            returns the created basket id.
        """
        basket_id = 0
        try:
            query = f"""INSERT INTO shopper_baskets (shopper_id, basket_created_date_time) 
                    VALUES ({shopper_id}, strftime('%Y-%m-%d %H:%M:%S', datetime('now')))"""
            cursor = self.conn.cursor()
            cursor.execute(query)
            basket_id = cursor.lastrowid
            self.conn.commit()
        except Exception as e:
            pass
        return basket_id

    def add_basket_content(self, basket_id, product_id, seller_id, quantity, price) -> bool:
        """
            Query to insert the shopper basket contents in the basket_contents table.

        Args:
            basket_id: table id of the basket.
            product_id: table id of the product.
            seller_id: table id of the seller.
            quantity: quantity of the product to add.
            price: price of the product.

        Returns:
            returns status of inserted data.
        """
        status = False
        try:
            cursor = self.conn.cursor()
            query_check = f"""SELECT EXISTS(SELECT seller_id FROM basket_contents WHERE basket_id = {basket_id} AND 
                        product_id = {product_id} AND seller_id = {seller_id})"""
            cursor.execute(query_check)
            rec = cursor.fetchone()[0]
            if rec:  # check if same product is in the basket then update the quantity.
                update_query = f"""UPDATE basket_contents SET quantity = {quantity} + quantity WHERE
                basket_id = {basket_id} AND product_id = {product_id} AND seller_id = {seller_id}"""
                cursor.execute(update_query)
                self.conn.commit()
                status = True
            else:
                query = f"""INSERT INTO basket_contents (basket_id, product_id, seller_id, quantity, price) 
                        VALUES ({basket_id}, {product_id}, {seller_id}, {quantity}, {price})"""
                cursor.execute(query)
                self.conn.commit()
                status = True
        except Exception as e:
            pass
        return status

    def get_basket_contents_details(self, basket_id) -> list:
        """
           Query to get basket content details in the products, sellers, & basket_contents tables.

        Args:
           basket_id: table id of the basket.

       Returns:
           returns list of all basket contents details.
       """
        data = list()
        try:
            query = f"""SELECT (SELECT product_description FROM products p WHERE p.product_id = bc.product_id) AS 
                    product_description, (SELECT seller_name FROM sellers s WHERE s.seller_id = bc.seller_id) AS 
                    seller_name, bc.quantity, '£ ' || ROUND(bc.price, 2) AS price,
                    ROUND((bc.quantity * bc.price), 2) 
                    as total_price FROM basket_contents bc 
                    WHERE bc.basket_id = {basket_id}"""
            cursor = self.conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            total = 0
            for key, order in enumerate(result):
                results = list()
                results.append(key + 1)
                results.append(order[0])
                results.append(order[1])
                results.append(order[2])
                results.append(order[3])
                total += order[4]
                results.append('£ ' + str(order[4]))
                data.append(results)

            data.append(list())
            results = list()
            results.append('')
            results.append('')
            results.append('Basket Total')
            results.append('')
            results.append('')
            results.append('£ ' + str("{:.2f}".format(total)))
            data.append(results)
        except Exception as e:
            pass
        return data

    def get_basket_contents(self, basket_id) -> list:
        """
            Query to get basket content details in the basket_contents table.

        Args:
            basket_id: table id of the basket.

        Returns:
            returns list of all basket contents details.
        """
        data = list()
        try:
            query = f"""SELECT product_id, seller_id FROM basket_contents WHERE basket_id = {basket_id}"""
            cursor = self.conn.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
        except Exception as e:
            pass
        return data

    def update_basket_contents(self, basket_id, product_id, seller_id, quantity):
        """
           Query to update the basket content product quantity in the basket_contents table.

       Args:
            basket_id: table id of the basket.
            product_id: table id of the product.
            seller_id: table id of the seller.
            quantity: quantity of the product to update.

       Returns:

       """
        try:
            cursor = self.conn.cursor()
            update_query = f"""UPDATE basket_contents SET quantity = {quantity} WHERE
                          basket_id = {basket_id} AND product_id = {product_id} AND seller_id = {seller_id}"""
            cursor.execute(update_query)
            self.conn.commit()
        except Exception as e:
            pass

    def delete_basket_item(self, basket_id, product_id, seller_id):
        """
          Query to delete the basket content product item in the basket_contents table.

        Args:
           basket_id: table id of the basket.
           product_id: table id of the product.
           seller_id: table id of the seller.

        Returns:

        """
        try:
            cursor = self.conn.cursor()
            update_query = f"""DELETE FROM basket_contents WHERE
                          basket_id = {basket_id} AND product_id = {product_id} AND seller_id = {seller_id}"""
            cursor.execute(update_query)
            self.conn.commit()
        except Exception as e:
            pass

    def shopper_checkout(self, shopper_id):
        """
            Query to insert the orders details of the shopper in the shopper_orders.

        Args:
           shopper_id: table id of the shopper.

        Returns:

        """
        try:
            cursor = self.conn.cursor()
            query = f"""INSERT INTO shopper_orders (shopper_id, order_date, order_status) VALUES
                            ({shopper_id}, strftime('%Y-%m-%d %H:%M:%S', datetime('now')), 'Placed')"""
            cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            pass

    def delete_basket_orders(self, basket_id) -> bool:
        """
            Query to delete the basket content details in the basket_contents & shopper_baskets tables.

        Args:
          basket_id: table id of the basket.

        Returns:
            return status of the rows delete.
        """
        status = False
        try:
            cursor = self.conn.cursor()
            delete_query_basket_c = f"""DELETE FROM basket_contents WHERE basket_id = {basket_id}"""
            delete_query_basket = f"""DELETE FROM shopper_baskets WHERE basket_id = {basket_id}"""
            cursor.execute(delete_query_basket_c)
            cursor.execute(delete_query_basket)
            self.conn.commit()
            status = True
        except Exception as e:
            pass
        return status
