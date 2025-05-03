import processor

def start_program():
        """
        Top level logic for the scraping program, begins all calls to terminal to ask for user specifications.
        """

        # User chooses Headless Mode Option
        headless = input("HEADLESS mode allows Selenium to run the Congressional Scraper Tool without pop-up windows showing up on your screen." + "\n" + "Would you like to run script in HEADLESS mode? (Y/N)")

        # Checks if user input is viable
        if headless.upper() not in ["Y", "N"]:
            print("Character not recognized ... Please try again")
            #aprint("\n" + "\n" + "\n" + "\n")
            start_program()
            return

        # Loading buffer warning
        print("Loading pages at a rapid speed can cause the Congress.gov website to limit requests from your IP. \nTo prevent this, it is recommended that you input a buffer between loading each page to prevent your IP from being logged and limited, possibly impacting performance.")

        # Logic to ask for user input for custom buffer, ensures input is a valid integer.
        while True:
            waitTime = input("Please specify a integer how long you want to wait between each page request (Recommended 1 or 2 seconds): ")
            try:
                waitTime = int(waitTime)      
                break
            except ValueError:
                print("Error: Unable to parse your response, please ensure you are inputting an INTEGER...")

        print("Buffer has successfully been parsed and implemented.")


        # Checks whether user wanted Headless mode or not, delegates to processor.
        if headless.upper() == "Y":
            headless = True
            print("Fetching latest user agent...")
            print("Please Wait...")
        else:
             headless = False

        processor.Processor(waitTime, headless)