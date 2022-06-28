import os
import sys
import time

from queries import Queries
from tabulate import tabulate


class Screens:
    db = user_selection = ""
    shopper_id = basket_id = 0
    main_menu_options = list()

    def __init__(self):
        self.db = Queries()
        self.main_menu_options = self.get_main_menu_options()

    def login_screen(self):
        """
            Main screen to input prompt for user to get shopper id and validates if the entered shopped is
            correct and shopper exists then proceeds to main screen menu.

        Args:

        Returns:

        """
        print("\n")
        prompt = "Please Enter Shopper id to proceed: "

        # check shopper id from input
        while True:
            try:
                id_entered = int(input(prompt))
                break
            except Exception:
                print('You have entered wrong input. Please enter valid input')

        # validate if id entered is valid and shopper exists then proceed to main menu.
        if id_entered > 0 and id_entered != '':
            self.shopper_id = id_entered
            result = self.db.check_shopper(self.shopper_id)
            if result is not None:
                print("Welcome ", result[0], result[1])
                # get shopper current basket id from database and set the basket_id
                basket_id = self.db.get_shopper_basket(self.shopper_id)
                if basket_id is not None:
                    self.basket_id = basket_id
                time.sleep(1)
                self.clear_cmd()
                self.main_menu_screen()
            else:  # wrong shopper id, exit the program
                print("\n")
                print("Wrong Shopper id: {0}".format(self.shopper_id))
                print("Exiting")
                time.sleep(2)
                sys.exit()
        else:  # if wrong input (non integer input) re-run login screen.
            self.clear_cmd()
            self.login_screen()

    def main_menu_screen(self):
        """
            Main menu screen to allow user to select from the options.

        Args:

        Returns:
        """
        selected_option = 0
        print("\n")
        print("ORINOCO–SHOPPER MAIN MENU")
        print(u'\u2500' * 100)
        print("\n")

        # print menu options
        for option_num, option in enumerate(self.main_menu_options):
            print("{0}.  {1}".format(option_num + 1, option))

        prompt = "Enter the number against the you want to choose: "
        # get valid menu selected option from the user
        while True:
            try:
                selected_option = int(input(prompt))
                break
            except Exception:
                print('Wrong Input. Please Enter Integer Value')

        # redirect user to appropriate menu screen from selected option.
        if selected_option != 0:
            if selected_option == 1:
                self.order_history_screen()
            elif selected_option == 2:
                self.products_screen()
            elif selected_option == 3:
                self.display_basket_screen(True)
            elif selected_option == 4:
                self.change_quantity_basket_screen()
            elif selected_option == 5:
                self.remove_item_basket_screen()
            elif selected_option == 6:
                self.checkout_screen()
            elif selected_option == 7:
                sys.exit()
            else:
                self.main_menu_screen()
        else:
            self.main_menu_screen()

    def order_history_screen(self):
        """
           Displays all the orders details of the users in the tabular format.

        Args:

        Returns:
        """
        self.clear_cmd()
        orders = self.db.get_shopper_orders(self.shopper_id)
        print(tabulate(orders, headers=['Order ID', 'Date', 'Product Description', 'Seller', 'Price', 'QTY', 'Status']))
        if len(orders) == 0:
            print("\nNo orders placed by this customer")
        self.main_menu_screen()

    def products_screen(self):
        """
          Displays all the categories of products for selection.

        Args:

        Returns:
        """
        categories = self.db.get_product_categories()
        self.clear_cmd()
        if categories is not None:
            # display categories screen menu
            category_id = self.display_options(categories, 'Product Category', 'product category')

            # display products screen menu
            products = self.db.get_products(category_id)
            product_id = self.display_options(products, 'Products', 'product')

            # display product seller screen menu
            sellers = self.db.get_sellers(product_id)
            seller_id = self.display_options(sellers, 'Sellers who sell this product', 'seller')

            # get quantity of product selected by user.
            prompt = "Enter the quantity of the selected product you want to buy: "
            quantity = 0
            while True:
                try:
                    input_quantity = int(input(prompt))
                except Exception as e:
                    input_quantity = 0

                if input_quantity <= 0:
                    print('The quantity must be greater than 0')
                else:
                    break

            price = self.db.get_product_price(seller_id, product_id)

            # check if user has current basket otherwise create new one.
            if self.basket_id == 0:
                basket_id = self.db.add_basket(self.shopper_id)
                self.basket_id = basket_id
            else:
                basket_id = self.basket_id

            # add selected product to the basket.
            if basket_id != 0:
                bc_status = self.db.add_basket_content(basket_id, product_id, seller_id, quantity, price)
                if basket_id != 0 and bc_status:
                    print("Item added to your basket")
        self.main_menu_screen()

    def display_basket_screen(self, redirect):
        """
         Displays all the details of the products in the shopper basket.

        Args:
            redirect: redirect user to main menu screen if True.
        Returns:
        """
        # get all the details of the product in the shopper basket.
        data = self.db.get_basket_contents_details(self.basket_id)
        print('\nBasket Contents')
        print((u'\u2500' * 15) + u'\n')
        if len(data) > 2:
            print(tabulate(data,
                           headers=['Basket Item', 'Product Description', 'Seller Name', 'QTY', 'Price', 'Total']))
        else:
            print("Your basket is empty\n")
            self.basket_id = 0

        if redirect:
            self.main_menu_screen()

    def change_quantity_basket_screen(self):
        """
            Menu selection to change the quantity of the product item in the shopper basket.

        Args:

        Returns:
        """
        # check if shopper basket is created
        if self.basket_id == 0:
            print("\nYour basket is empty\n")
            self.main_menu_screen()
        else:  # display basket contents and selection to select item to change the quantity.
            self.display_basket_screen(False)
            print("\n")
            contents = self.db.get_basket_contents(self.basket_id)
            selected_option_item = 0
            if len(contents) > 1:
                prompt = "Enter the basket item no. of the item you want to update: "
                while selected_option_item <= 0 or selected_option_item > len(contents):
                    try:
                        selected_option_item = int(input(prompt))
                    except Exception:
                        pass
                    if selected_option_item <= 0 or selected_option_item > len(contents):
                        print('The basket item no. you have entered is invalid. Please enter the value again.')
            else:  # only one item in basket
                selected_option_item = 1

            # input to get the quantity from the user.
            input_quantity = 0
            prompt = "Enter the new quantity for the item selected: "
            while True:
                try:
                    input_quantity = int(input(prompt))
                except Exception as e:
                    input_quantity = 0

                if input_quantity <= 0:
                    print('The quantity must be greater than 0')
                else:
                    break

            # get the item product_id and seller_id to update the quantity against the selected item.
            selected_option_item -= 1
            item = contents[selected_option_item]
            product_id = item[0]
            seller_id = item[1]
            self.db.update_basket_contents(self.basket_id, product_id, seller_id, input_quantity)
        self.display_basket_screen(True)

    def remove_item_basket_screen(self):
        """
           Menu to display options to remove product item from the basket.

        Args:

        Returns:
        """
        # check if shopper basket is empty.
        if self.basket_id == 0:
            print("\nYour basket is empty\n")
            self.main_menu_screen()
        else:  # display shopper basket and give selection to remove the item from the basket.
            self.display_basket_screen(False)
            print("\n")
            contents = self.db.get_basket_contents(self.basket_id)
            selected_option_item = 0

            # get the item number to be removed from the user selection.
            if len(contents) > 1:
                prompt = "Enter the basket item no. of the item you want to remove: "
                while selected_option_item <= 0 or selected_option_item > len(contents):
                    try:
                        selected_option_item = int(input(prompt))
                    except Exception as e:
                        pass
                    if selected_option_item <= 0 or selected_option_item > len(contents):
                        print('The basket item no. you have entered is invalid. Please enter the value again.')
                prompt = "Do you definitely want to delete this product from your basket Y/N: "
            else:  # only one item in the basket.
                selected_option_item = 1
                prompt = "Do you definitely want to delete this product from your basket and empty your product Y/N: "

            # confirmation prompt from user to remove product item from basket.
            input_val = self.get_y_n_prompt(prompt)
            if input_val == 'y':
                selected_option_item -= 1
                item = contents[selected_option_item]
                product_id = item[0]
                seller_id = item[1]
                self.db.delete_basket_item(self.basket_id, product_id, seller_id)
                self.display_basket_screen(True)
            else:
                self.main_menu_screen()

    def checkout_screen(self):
        """
            Confirmation prompt from user to check out the basket content.

        Args:

        Returns:
        """
        # check if shopper has a basket (empty).
        if self.basket_id == 0:
            print("\nCannot checkout your basket is empty\n")
            self.main_menu_screen()
        else:  # get user confirmation for checkout.
            self.display_basket_screen(False)
            prompt = "Do you wish to proceed with the checkout Y/N: "
            input_val = self.get_y_n_prompt(prompt)
            if input_val == 'y':
                self.db.shopper_checkout(self.shopper_id)
                status = self.db.delete_basket_orders(self.basket_id)
                if status:
                    self.basket_id = 0
                    print("Checkout complete, your order has been placed")
            self.main_menu_screen()

    @staticmethod
    def get_y_n_prompt(prompt):
        """
            Generic Prompt for user for yes/no confirmation.

        Args:

        Returns:
        """
        selected_option_y_n = ""
        while True:
            try:
                selected_option_y_n = input(prompt)
                selected_option_y_n = selected_option_y_n.lower()
                selected_option_y_n = str(selected_option_y_n.strip())
            except Exception:
                pass
            if selected_option_y_n == 'y' or selected_option_y_n == 'n':
                break
            else:
                print("You have entered wrong input. Please enter the value again Y/N.")
        return selected_option_y_n

    @staticmethod
    def display_options(all_options, title, type_option) -> int:
        """
             Display the list of items provided and title of menu.

        Args:

        Returns:
            returns the selected option from the menu list.
        """
        option_num = 1
        option_list = []
        print("\n", title, "\n")
        for option in all_options:
            code = option[0]
            desc = option[1]
            print("{0}.  {1}".format(option_num, desc))
            option_num = option_num + 1
            option_list.append(code)
        selected_option = 0
        prompt = "Enter the number against the " + type_option + " you want to choose: "
        while selected_option > len(option_list) or selected_option == 0:
            try:
                selected_option = int(input(prompt))
            except Exception:
                print("You have entered wrong input.")
            if selected_option <= len(option_list):
                return option_list[selected_option - 1]

    @staticmethod
    def clear_cmd():
        # clear command line.
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def get_main_menu_options():
        # main menu options.
        options = ['Display your order history', 'Add an item to your basket', 'View your basket',
                   'Change the quantity of an item in your basket', 'Remove an item from your basket',
                   'Checkout', 'Exit']
        return options
