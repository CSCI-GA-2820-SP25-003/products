Feature: The product part back-end
    As a Store Owner
    I need a RESTful catalog service
    So that I can keep track of all my Products

Background:
    Given the following products
        | name           | sku       | description      | price  | image_url                | likes |
        | E-Reader       | SKU123456 | Digital reader   | 129.99 | https://www.google.com   | 0     |
        | Vacuum Cleaner | SKU789012 | Powerful cleaner | 199.99 | https://www.nyu.edu      | 2     |
        | Jeans          | SKU345678 | Comfortable fit  | 49.99  | https://www.google.com   | 5     |
        | Potato Chips   | SKU901234 | Crunchy snack    | 3.99   | https://www.nyu.edu      | 10    |


Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Product Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Test all filtering options sequentially
    When I visit the "Home Page"
    Then I should see "Product Demo RESTful Service" in the title
    
    # Search by name
    When I clear all form fields
    And I set the "name" to "Jeans"
    And I press the "Search" button
    Then I should see "Jeans" in the results
    And I should not see "E-Reader" in the results
    And I should not see "Vacuum Cleaner" in the results
    And I should not see "Potato Chips" in the results
    And I should see the message "Success"
    
    # Search by SKU
    When I clear all form fields
    And I set the "sku" to "SKU123456"
    And I press the "Search" button
    Then I should see "E-Reader" in the results
    And I should not see "Vacuum Cleaner" in the results
    And I should not see "Jeans" in the results
    And I should not see "Potato Chips" in the results
    And I should see the message "Success"
    
    # Search by minimum price
    When I clear all form fields
    And I set the "min_price" to "100.00"
    And I press the "Search" button
    Then I should see "E-Reader" in the results
    And I should see "Vacuum Cleaner" in the results
    And I should not see "Jeans" in the results
    And I should not see "Potato Chips" in the results
    And I should see the message "Success"
    
    # Search by maximum price
    When I clear all form fields
    And I set the "max_price" to "50.00"
    And I press the "Search" button
    Then I should see "Jeans" in the results
    And I should see "Potato Chips" in the results
    And I should not see "E-Reader" in the results
    And I should not see "Vacuum Cleaner" in the results
    And I should see the message "Success"
    
    # Search by price range
    When I clear all form fields
    And I set the "min_price" to "40.00"
    And I set the "max_price" to "200.00"
    And I press the "Search" button
    Then I should see "E-Reader" in the results
    And I should see "Vacuum Cleaner" in the results
    And I should see "Jeans" in the results
    And I should not see "Potato Chips" in the results
    And I should see the message "Success"
    
    # Find all products
    When I clear all form fields
    And I press the "Search" button
    Then I should see "E-Reader" in the results
    And I should see "Vacuum Cleaner" in the results
    And I should see "Jeans" in the results
    And I should see "Potato Chips" in the results
    And I should see the message "Success"