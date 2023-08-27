# ------------------------- LIBRARY IMPORTS ---------------------------
import gspread
import pyfiglet as pyf
import os
import re
import bcrypt
import sys
from google.oauth2.service_account import Credentials
from pokemon_ascii_art import print_pokemon
from termcolor import colored
from tabulate import tabulate

# ---------------------------- API SETUP ------------------------------
# Specify what parts of the google account the user has access to
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]

try:
    # Create a Credentials instance from a service account json file
    CREDS = Credentials.from_service_account_file("creds.json")

    # Create a copy of the credentials with specified scope
    SCOPED_CREDS = CREDS.with_scopes(SCOPE)

    # Create gspread client using gspread authorize method
    GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)

    # Access sheet for project
    SHEET = GSPREAD_CLIENT.open("pokemon_portfolio")

except Exception as e:
    print(f"\nAn error occured when initialising: {e}, "
          "please press the Run Program above to try again\n")
    print()
    sys.exit(1)  # exit due to err


# --------------------------- CLASSES -----------------------------
class User:
    """
    A class representing a human user.

    Attributes:
        user_col_number (int):
            Value representing column that stores uses card collection
        col_letter (string):
            Letter to represent user column
    """

    def __init__(self, col_number, col_letter):
        """
        Initialise an instance of the User class.

        Parameters:
            col_number (string):
                Represents the column number that store users cards
        """
        self.col_number = col_number
        self.col_letter = col_letter

    def add_card(self):
        """
        Adds a card to users collection based on the card number

        Parameters:
            self (object): An instance of the User class
        Returns:
            None
        """

        clear_terminal()
        print_art_font("               Add  a  card")
        print_pokemon("19")
        print("\n")

        # Get card number from user and validate
        while True:
            card_num_selection = input(
                "\nEnter the card number (1-102) that you "
                "would like to add: \n"
            )

            validated_card_num = validate_selection(
                card_num_selection, list(range(1, 103))
            )

            if validated_card_num:
                break

        bss_worksheet = SHEET.worksheet("base_set_shadowless")
        # Set card row adding 1 to account for headings
        card_row = str(validated_card_num + 1)

        # Check if card is not in collection (== "No") and ad it
        if bss_worksheet.cell(card_row, self.col_number).value == "No":
            bss_worksheet.update_cell(card_row, self.col_number, "Yes")

            cardname = bss_worksheet.cell(card_row, 2).value
            clear_terminal()
            print_center_string(
                colored(
                    f"You have successfully added {cardname}, "
                    f"card No.{validated_card_num}.\n",
                    "green",
                    attrs=["bold", "underline"],
                )
            )
            print_pokemon(str(validated_card_num))

            select_avail_user_option(self.add_card, "Add another card")

        else:
            print_center_string(
                colored(
                    "This card is already in your collection\n",
                    "red",
                    attrs=["bold", "underline"],
                )
            )
            select_avail_user_option(self.add_card, "Add another card")

    def remove_card(self):
        """
        Allows a user to remove a card from their collection
        based on the card number

        Parameters:
            self (object): An instance of the User class
        Returns:
            None
        """

        clear_terminal()
        print_art_font("       Remove  a  Card")
        print_pokemon("28")
        print("\n")

        while True:
            card_num_selection = input(
                "\nEnter the card number (1-102) that "
                "you would like to remove: \n"
            )

            validated_card_num = validate_selection(
                card_num_selection, list(range(1, 103))
            )
            if validated_card_num:
                break

        bss_worksheet = SHEET.worksheet("base_set_shadowless")
        # set card row adding 1 to account for headings
        card_row = str(validated_card_num + 1)

        # Check if card is card is in collection (== "Yes") and remove it
        if bss_worksheet.cell(card_row, self.col_number).value == "Yes":
            bss_worksheet.update_cell(card_row, self.col_number, "No")

            cardname = bss_worksheet.cell(card_row, 2).value
            clear_terminal()
            print_center_string(
                colored(
                    f"You have successfully removed {cardname}, "
                    f"card No.{validated_card_num}.\n",
                    "green",
                    attrs=["bold", "underline"],
                )
            )
            print_pokemon(str(validated_card_num))

            select_avail_user_option(self.remove_card, "Remove another card")

        else:
            print_center_string(
                colored(
                    "You do not have this card in your collection\n",
                    "red",
                    attrs=["bold", "underline"],
                )
            )
            select_avail_user_option(self.remove_card, "Remove another card")

    def view_portfolio(self):
        """
        Allows a user to view their portfolio

        Parameters:
            self (object): An instance of the User class
        Returns:
            None
        """

        clear_terminal()
        print_art_font("       Your  Portfolio")
        print("")

        bss_worksheet = SHEET.worksheet("base_set_shadowless")

        # Get pokemon card names, numbers and user cards -
        # (Yes/No's to indicate which cards are in their collection)
        card_names = bss_worksheet.col_values(2)[1:]
        user_cards = bss_worksheet.col_values(self.col_number)[1:]
        card_nums = bss_worksheet.col_values(4)[1:]

        # Generate a list of pokemon cards in the users collection
        user_collection = []
        for card, card_num, name in zip(user_cards, card_nums, card_names):
            if card == "Yes":
                card_string = f"BS{card_num}: {name}"
                user_collection.append(card_string)

        # Check if we have cards to display
        num_cards_collected = len(user_collection)
        if num_cards_collected > 0:
            # Structure list of cards for display in 3 columns
            user_coll_columns = []
            num_cols = 3
            for i in range(0, len(user_collection), num_cols):
                column = user_collection[i:i + num_cols]
                user_coll_columns.append(column)

            print(tabulate(user_coll_columns, tablefmt="fancy_grid"))

            # check how many cards we show and display % complete
            percentage = round((num_cards_collected / len(card_nums) * 100))
            if percentage == 100:
                print_center_string(
                    colored(
                        f"Congratulation your set is {percentage}% complete\n",
                        "green",
                        attrs=["bold", "underline"],
                    )
                )
            else:
                print_center_string(
                    colored(
                        f"You have collected {percentage}%, "
                        "of available cards in this set\n",
                        "green",
                        attrs=["bold", "underline"],
                    )
                )

        else:
            print("")
            print_center_string(
                colored("You do not have any cards in you collection\n", "red")
            )

        input("Press enter to return to main menu\n")

    def view_cards_needed(self):
        """
        Allows a user to view the cards missing from their collection

        Parameters:
            self (object): An instance of the User class
        Returns:
            None
        """

        clear_terminal()
        print_art_font("         Cards  Needed")
        print("")

        bss_worksheet = SHEET.worksheet("base_set_shadowless")

        # Get pokemon card names, numbers and user cards -
        # (Yes/No's to indicate which cards are in their collection)
        card_names = bss_worksheet.col_values(2)[1:]
        user_cards = bss_worksheet.col_values(self.col_number)[1:]
        card_nums = bss_worksheet.col_values(4)[1:]

        # Generate a list of pokemon cards in the users collection
        user_missing_cards = []
        for card, card_num, name in zip(user_cards, card_nums, card_names):
            if card == "No":
                card_string = f"BS{card_num}: {name}"
                user_missing_cards.append(card_string)

        # Check if we have cards to display
        num_cards_missing = len(user_missing_cards)
        if num_cards_missing > 0:
            # Structure list of cards for display in 3 columns
            user_coll_columns = []
            num_cols = 3
            for i in range(0, len(user_missing_cards), num_cols):
                column = user_missing_cards[i:i + num_cols]
                user_coll_columns.append(column)

            print(tabulate(user_coll_columns, tablefmt="fancy_grid"))

            # check how many cards we show and display % complete
            percentage = round((num_cards_missing / len(card_nums) * 100))
            print_center_string(
                colored(
                    f"You are missing {percentage}%, "
                    "of available cards in this set\n",
                    "red",
                    attrs=["bold", "underline"],
                )
            )

        else:
            print("")
            print_center_string(
                colored("Your collection is 100% complete, "
                        "CONGRATULATIONS\n", "green")
            )

        input("Press enter to return to main menu\n")

    def appraise_portfolio(self):
        """
        Allows a user to view their portfolio value

        Parameters:
            self (object): An instance of the User class
        Returns:
            None
        """

        clear_terminal()
        print_art_font("      Portfolio  Value")
        print("")

        bss_worksheet = SHEET.worksheet("base_set_shadowless")

        # Get pokemon card values and user cards -
        # (Yes/No's to indicate which cards are in their collection)
        card_values = bss_worksheet.col_values(5)[1:]
        user_cards = bss_worksheet.col_values(self.col_number)[1:]

        # Sum the values of the cards the user
        # using a generator expression and sum function
        portfolio_value = round(
            sum(
                float(card_value)
                for card, card_value in zip(user_cards, card_values)
                if card == "Yes"
            ),
            2,
        )

        print_pokemon("46")
        print_center_string(
            colored(
                f"Your pokemon portfolio value is, ${portfolio_value}\n",
                "green",
                attrs=["bold", "underline"],
            )
        )

        if portfolio_value > 0:
            print_art_font(f"                       $  {portfolio_value}")
        else:
            print_center_string(
                colored(
                    "You do not have any pokemon cards in your portfolio \n",
                    "red",
                    attrs=["bold", "underline"],
                )
            )

        input("Press enter to return to main menu\n")

    def delete_portfolio(self):
        """
        Allows a user to delete their portfolio

        Parameters:
            self (object): An instance of the User class
        Returns:
            None
        """

        clear_terminal()
        print_art_font("     Portfolio Deleted")
        print_pokemon("50")
        print_center_string(
            colored(
                "Your Portfolio has been successfully deleted\n",
                "green",
                attrs=["bold", "underline"],
            )
        )

        # Add No to all cells in user column
        bss_worksheet = SHEET.worksheet("base_set_shadowless")
        update_values = [["No"] for i in range(102)]
        range_to_update = f"{self.col_letter}2:{self.col_letter}103"
        bss_worksheet.update(range_to_update, update_values)

        input("Press enter to return to main menu\n")


def select_avail_user_option(function_to_call, function_text):
    """
    Used to display a list of options to the user and
    allow them to make a selection

    Parameters:
        function_to_call (func): Function to be called if option 1 is selected
    Returns:
        function_text (string): Text to be shown for option 1

    """
    while True:
        print_center_string(
            colored(
                "Please select option (1 or 2) from the list shown "
                "and enter it below\n",
                attrs=["bold", "underline"],
            )
        )

        print("1. " + function_text)
        print("2. Return to main menu\n")

        selection = input("Enter your selection: \n")

        validated_selection = validate_selection(selection, list(range(1, 3)))

        if validated_selection == 1:
            function_to_call()
            break
        elif validated_selection == 2:
            # just break, as this will return the user to main menu
            break


# --------------------- APP LOGIC FUNCTIONS -----------------------


def display_welcome_banner():
    """
    Displays welcome banner and image

    Parameters:
        None
    Returns:
        None
    """
    clear_terminal()

    print_art_font("Pokemon Portfolio")

    print_pokemon("pikachu_banner")

    login_options()


def login_options():
    """
    Displays the login opitions to user.
    Takes user selection, validates and calls appropiate function.

    Parameters:
        None
    Returns:
        None
    """
    while True:
        print_center_string(
            colored(
                "Please select an option (1-3) from the list shown "
                "and enter it below\n",
                attrs=["bold", "underline"],
            )
        )

        print("1. Log into your account")
        print("2. Create an account")
        print("3. Password reset\n")

        login_selection = input("Enter your selection: \n")

        validated_selection = validate_selection(
            login_selection, list(range(1, 4)))

        if validated_selection == 1:
            account_login()
            break
        elif validated_selection == 2:
            create_account()
            break
        elif validated_selection == 3:
            reset_password()
            break


def account_login():
    """
    Allows user to login to app using their username and password
    Retrieves stored password for username and compares to entered pass

    Parameters:
        None
    Returns:
        None
    """

    clear_terminal()
    print_art_font("       Account  Login")
    print_pokemon("10")

    print("\n\n")
    print_center_string(
        colored(
            "Please enter your username and password below to login "
            "(both are case sensitive)\n",
            attrs=["bold", "underline"],
        )
    )

    username = get_valid_username(False)

    if check_username_in_use(username):
        password_attempt = get_valid_password(False)

        print_center_string("Logging in ....\n")

        # Find the row their username is on and
        # return the corrisponding password
        login_worksheet = SHEET.worksheet("login")
        username_found = login_worksheet.find(username, in_column=1)
        row_num = username_found.row
        stored_hashed_pass = login_worksheet.cell(row_num, 2).value

        # Slice the b'' from the stored pass and
        # change type from string to bytes for comparison
        stored_hashed_pass = stored_hashed_pass[2:-1].encode("utf-8")
        password_attempt_bytes = password_attempt.encode()

        # check if password entered matches
        if bcrypt.checkpw(password_attempt_bytes, stored_hashed_pass):
            print_center_string(colored("Login Successful\n", "green"))

            # get the users col number/letter and
            # create a user using this value
            bss_worksheet = SHEET.worksheet("base_set_shadowless")
            username_found_bss = bss_worksheet.find(username, in_row=1)
            user_col_num = username_found_bss.col
            user_col_letter = bss_worksheet.cell(104, user_col_num).value
            print(user_col_letter)
            human_user = User(user_col_num, user_col_letter)
            main_menu(human_user)
        else:
            print_center_string(
                colored("Login failed, password incorrect\n", "red"))
            select_from_avail_options(account_login, "Try again")

    else:
        print_center_string(
            colored("The username entered is not associated "
                    "with an account\n", "red")
        )

        select_from_avail_options(account_login, "Try again")


def create_account():
    """
    Used to create a new user account
    Takes username, password and phone num from user and validates
    Stores new user details in google sheet
    Assigns the user a column in the base_set_shadowless sheet
    Preps workbook for next user

    Parameters:
        None
    Returns:
        None
    """
    clear_terminal()
    print_art_font(" Account Creation")
    print_pokemon("44")

    print("\n\n")
    print_center_string(
        colored(
            "Please follow the steps below to create an account\n",
            attrs=["bold", "underline"],
        )
    )

    # get new user details
    username = get_valid_username()
    print_center_string(colored("Username available\n", "green"))
    password = get_valid_password()
    phone_num = get_valid_phone_num()

    print_center_string("Creating Account ....\n")

    # Store user account details
    account_details = [username, password, phone_num]
    login_worksheet = SHEET.worksheet("login")
    login_worksheet.append_row(account_details)

    # Assign the user the next available column in
    # base_set_shadowless sheet and add his username
    bss_worksheet = SHEET.worksheet("base_set_shadowless")
    next_avail_column = bss_worksheet.acell("A2").value
    bss_worksheet.update_acell(next_avail_column + "1", username)

    # add empty collection ("No's")
    update_values = [["No"] for i in range(102)]
    range_to_update = f"{next_avail_column}2:{next_avail_column}103"

    bss_worksheet.update(range_to_update, update_values)

    # Save the column letter assigned to that account as a letter
    # for use when creating a user object
    bss_worksheet.update_acell(next_avail_column + "104", next_avail_column)

    # Increment the next_avail_column stored in gsheets, and add a new column
    # to ensure were always ready and hava a column for next account creation
    bss_worksheet.update_acell(
        "A2", increment_gsheet_column_value(next_avail_column))
    add_column_to_sheet("base_set_shadowless")

    clear_terminal()
    print_center_string(
        colored("Account created successfully\n", "green",
                attrs=["bold", "underline"])
    )
    print_pokemon("5")

    select_from_avail_options(create_account, "Create another account")


def reset_password():
    """
    Allows user to reset password

    Parameters:
        None
    Returns:
        None
    """
    clear_terminal()

    print_art_font("      Password  Reset")
    print_pokemon("63")

    print("\n\n")
    print_center_string(
        colored(
            "Please follow the steps below to reset your password\n",
            attrs=["bold", "underline"],
        )
    )

    phone_num = get_valid_phone_num(False)

    print_center_string("Checking for account ....\n")

    if check_phone_num_in_use(phone_num):
        # Find the row their phone number is on and
        # return the corrisponding username
        login_worksheet = SHEET.worksheet("login")
        phone_num_found = login_worksheet.find(phone_num, in_column=3)
        row_num = phone_num_found.row
        username = login_worksheet.cell(row_num, 1).value

        print_center_string(
            colored(f"Account found, username is {username}\n", "green")
        )

        # Get and store new password
        hashed_password = get_valid_password()

        # Write users new hashed pass
        login_worksheet.update_acell("B" + str(row_num), hashed_password)

        print("")
        print_center_string(colored("Password has been reset\n", "green"))

    else:
        print_center_string(
            colored(
                "The phone number entered is not associated "
                "with an acconut\n", "red"
            )
        )

    # Return to login menu or try again
    select_from_avail_options(reset_password, "Reset password again")


def main_menu(human_user):
    """
    Displays a main menu to a user allowing them to select options

    Parameters:
        human_user (object of User class):
            The current user that is using the app
    Returns:
        None
    """
    while True:
        clear_terminal()
        print_art_font("                Main  Menu")
        print_pokemon("4")

        print_center_string(
            colored(
                "Please select an option (1-6) from the list shown"
                "and enter it below\n",
                attrs=["bold", "underline"],
            )
        )
        while True:
            print("1. Add a card to your portfolio")
            print("2. Remove a card from your portfolio")
            print("3. View portfolio")
            print("4. View cards needed to complete collection")
            print("5. Appraise portfolio")
            print("6. Delete portfolio\n")

            menu_selection = input("Enter your selection: \n")

            validated_selection = validate_selection(
                menu_selection, list(range(1, 7)))

            if validated_selection:
                break

        if validated_selection == 1:
            human_user.add_card()

        elif validated_selection == 2:
            human_user.remove_card()

        elif validated_selection == 3:
            human_user.view_portfolio()

        elif validated_selection == 4:
            human_user.view_cards_needed()

        elif validated_selection == 5:
            human_user.appraise_portfolio()

        elif validated_selection == 6:
            clear_terminal()
            print_art_font("      Delete  Portfolio")
            print_pokemon("29")
            while True:
                print_center_string(
                    colored(
                        "Please select an option (1 or 2) from the list shown "
                        "and enter it below\n\n",
                        attrs=["bold", "underline"],
                    )
                )
                print_center_string(
                    colored(
                        "CAUTION, selecting option 1 this will delete "
                        "all cards from your portfolio\n",
                        "red",
                        attrs=["bold", "underline"],
                    )
                )
                print("1. Yes delete my portfolio")
                print("2. Return to main menu\n")
                confirm_selection = input("Enter your selection: \n")

                confirm_selection_validated = validate_selection(
                    confirm_selection, list(range(1, 3))
                )
                if confirm_selection_validated == 1:
                    human_user.delete_portfolio()
                    break
                elif confirm_selection_validated == 2:
                    break


# ----------------------- HELPER FUNCTIONS ------------------------


def print_art_font(string):
    """
    Uses pyfiglet library to convert given string into an art font style

    Parameters:
        text (string): Text to be converted
    Returns:
        None
    """
    font = pyf.Figlet(font="big", width=110)
    msg = font.renderText(string)
    msg = msg.rstrip()
    print(msg)


def print_center_string(string):
    """
    Centers and prints the given text to the terminal
    If text contains ascii escape codes for color etc
    the function will stip these out for calculating
    spacing but will still print original text

    Parameters:
        String (string): String to be centered and printed
    Returns:
        None
    """

    terminal_width = os.get_terminal_size().columns

    # If string contains ascii escape chars, use regex
    # to substitute them with " " before calculations
    processed_string = re.sub(r"(\x1b|\033)\[[0-9;]*m", "", string)

    spaces = int((terminal_width - len(processed_string)) / 2)
    centered_string = " " * spaces + string
    print(centered_string)


def clear_terminal():
    """
    Clears text from trminal
    """
    if os.name == "posix":  # Linux and macOS
        os.system("clear")
    elif os.name == "nt":  # Windows
        os.system("cls")


def check_username_in_use(username):
    """
    Check if username is already stored in google sheet

    Parameters:
        username (string): String to search for in gogle sheets
    Returns:
        True or False (boolean): True if username foun, false otherwise

    """
    login_worksheet = SHEET.worksheet("login")
    username_found = login_worksheet.find(username, in_column=1)
    if username_found:
        return True
    else:
        return False


def check_phone_num_in_use(phone_num):
    """
    Check if phone number is already stored in google sheet

    Parameters:
        username (string): String to search for in gogle sheets
    Returns:
        True or False (boolean): True if username found, false otherwise
    """
    login_worksheet = SHEET.worksheet("login")
    phone_num_found = login_worksheet.find(phone_num, in_column=3)
    if phone_num_found:
        return True
    else:
        return False


def hash_password(password):
    """
    Hashes given password using a generated salt

    Parameters:
        password (string): Password to be hashed
    Returns:
        password (string): String representing the hashed password
    """
    salt = bcrypt.gensalt()
    hashed_pass = bcrypt.hashpw(password.encode(), salt)

    # retured as strings for storage in gsheets
    hashed_pass = str(hashed_pass)

    return hashed_pass


def select_from_avail_options(function_to_call, function_text):
    """
    Used to display a list of options to the user
    and allow them to make a selection

    Parameters:
        function_to_call (func): Function to be called if option 1 is selected
    Returns:
        function_text (string): Text to be shown for option 1

    """
    while True:
        print_center_string(
            colored(
                "Please select option (1 or 2) from the list shown "
                "and enter it below\n",
                attrs=["bold", "underline"],
            )
        )

        print("1. " + function_text)
        print("2. Return to home page\n")

        selection = input("Enter your selection: \n")

        validated_selection = validate_selection(selection, list(range(1, 3)))

        if validated_selection == 1:
            function_to_call()
            break
        elif validated_selection == 2:
            display_welcome_banner()
            break


# ----------------------- GSHEETS FUNCTIONS -----------------------


def increment_gsheet_column_value(column):
    """
    Used to increment column values in gsheets.
    Pass in A returns B
    Pass in Z returns AA
    Pass in GZ returns HA etc.

    Parameters:
        column (string): Column to be incremented
    Returns:
        incremented_col (string): Value of the next column

    """
    # use in the case where we reach Z and need to move to AA
    if column == "":
        return "A"

    last_char_in_column = column[-1]
    other_chars = column[:-1]

    if last_char_in_column == "Z":
        # call this function again passing in other_chars
        # to update the letters before the Z and change the Z to A
        return increment_gsheet_column_value(other_chars) + "A"
    else:
        return other_chars + chr(ord(last_char_in_column) + 1)


def add_column_to_sheet(sheet_name):
    """
    Adds a new column to the specified google sheet

    Parameters:
        sheet_name (string): Sheet to add column to
    Returns:
        None:
    """
    worksheet = SHEET.worksheet(sheet_name)
    empty_lists = [[]]
    last_col_index = worksheet.col_count - 1
    worksheet.insert_cols(
        empty_lists,
        col=last_col_index,
        value_input_option="RAW",
        inherit_from_before=True,
    )


# --------------------- VALIDATION FUNCTIONS ----------------------


def validate_selection(selection_str, available_choices):
    """
    Validates user selcection from a choice of numbers
    Validates that it can be converted to an int
    Also validates that user selection was one of the available choices

    Parameters:
        selection_str (string): User selection to be validated
        available_choices (list): List of choices available to user
    Returns:
        int or False: Returns selection value as an int if valid
                      otherwise returns False
    """
    try:
        if not selection_str.isdigit():
            raise ValueError(f"Your selection {selection_str} is not a number")

        selection_value = int(selection_str)
        if selection_value not in available_choices:
            raise ValueError(
                "Available options ("
                f"{available_choices[0]} - {available_choices[-1]}), "
                f"you entered {selection_value}")

    except ValueError as e:
        print()
        print_center_string(
            colored(f"Invalid selection: {e}, please try again\n", "red")
        )
        return False
    return selection_value


def get_valid_username(check_for_match=True):
    """
    Gets a valid username from the user
    Username can be between 5-15 chars long and include _ or -

    Parameters:
        check_for_match (boolean):
            Flag used to control if we check gsheets for matching username
    Returns:
        username (string): Validated username chosen by user

    """
    while True:
        try:
            username = input(
                "\nPlease enter username between 5 and 15 characters "
                "long,\n(You may use letters, numbers, _ or -) : \n"
            )

            if len(username) < 5:
                raise ValueError("Username must be at least 5 characters")

            if len(username) > 15:
                raise ValueError("Username can not be more than 15 characters")

            # Uses regex to check username from start to end and
            # ensures it only contains, letters, numbers, _ and -
            if not re.match("^[a-zA-Z0-9_-]*$", username):
                raise ValueError("Username can only use letters, "
                                 "numbers, _ or -")

            if check_for_match:
                if check_username_in_use(username):
                    raise ValueError("Username aleady in use")
            return username

        except ValueError as e:
            print("")
            print_center_string(
                colored(f"Invalid username: {e}, please try again\n", "red")
            )


def get_valid_password(hash_pass=True):
    """
    Gets a valid password from user
    Password can be between 5 and 15 chars and use  _ , - , & or !
    Hashes password via call to external function

    Parameters:
        hash_pass: Flag to allow password hashing to be skipped
    Returns:
        password (string): Validated, Hashed password"""
    while True:
        try:
            password = input(
                "\nPlease enter a password between 5 and 15 characters "
                "long,\n(You may user letters, numbers, _ , - , & or !) : \n"
            )

            if len(password) < 5:
                raise ValueError("Password must be at least 5 characters")

            if len(password) > 15:
                raise ValueError("Password cannot be more than 15 characters")

            # Uses regex to check password from start to end and ensures
            # it only contains, letters, numbers, _ , & , ! and  -
            if not re.match("^[a-zA-Z0-9_&!-]*$", password):
                raise ValueError("Please only use letters, "
                                 "numbers, _ , - , & or !")

            if hash_pass:
                password = hash_password(password)
                return password
            else:
                return password

        except ValueError as e:
            print("")
            print_center_string(
                colored(f"Invalid Password: {e}, please try again\n", "red")
            )


def get_valid_phone_num(check_for_match=True):
    """
    Gets a valid phone number from user
    Phone number can be between 10 and 15 digits

    Parameters:
        check_for_match (boolean):
        Flag used to control if we check gsheets for matching number
    Returns:
        phone_num (string): Validated phone number chosen by user
    """
    while True:
        try:
            phone_num = input(
                "\nPlease enter your mobile phone number consisting "
                "of 10 to 15 digits: \n"
            )

            if len(phone_num) < 10:
                raise ValueError("Phone number must be at least 10 digits")

            if len(phone_num) > 15:
                raise ValueError("Phone number cannot be more than 15 digits")

            # Uses regex to check phone_num from start to end and
            # ensure it only contains, letters, numbers
            if not re.match("^[0-9]*$", phone_num):
                raise ValueError("Please only use numbers")

            if check_for_match:
                if check_phone_num_in_use(phone_num):
                    raise ValueError("Phone number aleady in use")

            return phone_num

        except ValueError as e:
            print("")
            print_center_string(
                colored(f"Invalid phone number: {e}, "
                        "please try again\n", "red")
            )


# ----------------------------- MAIN -------------------------------


def main():
    """
    Run Pokemon Portfolio terminal application
    """
    display_welcome_banner()


# Ensures main is only excuted when the script is directly run
if __name__ == "__main__":
    main()
