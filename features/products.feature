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


Scenario: Create a Product
    When I visit the "Home Page"
    And I set the "Name" to "AirPods Pro"
    And I set the "SKU" to "SKU1000"
    And I set the "Description" to "Wireless earbuds"
    And I set the "Price" to "249.99"
    And I set the "Image URL" to "https://example.com/airpods.jpg"
    And I press the "Create" button
    Then I should see the message "Success"
    
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "SKU" field should be empty
    And the "Description" field should be empty
    And the "Price" field should be empty
    And the "Image URL" field should be empty
    And the "Likes" field should be empty
    
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "AirPods Pro" in the "Name" field
    And I should see "SKU1000" in the "SKU" field
    And I should see "Wireless earbuds" in the "Description" field
    And I should see "249.99" in the "Price" field
    And I should see "https://example.com/airpods.jpg" in the "Image URL" field
    And I should see "0" in the "Likes" field


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

Scenario: Update a Product
    When I visit the "Home Page"
    And I set the "Name" to "E-Reader"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "E-Reader" in the "Name" field
    And I should see "SKU123456" in the "SKU" field
    And I should see "Digital reader" in the "Description" field
    And I should see "129.99" in the "Price" field
    And I should see "https://www.google.com" in the "Image URL" field
    And I should see "0" in the "Likes" field

    When I change "Name" to "Book"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Book" in the "Name" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Book" in the results
    And I should not see "E-Reader" in the results

delete-product-bdd

Scenario: Delete a Product
    When I visit the "Home Page"
    And I set the "Name" to "Vacuum Cleaner"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Vacuum Cleaner" in the "Name" field

    When I press the "Delete" button
    And I confirm the deletion
    Then I should see the message "Product has been Deleted!"
    
    When I press the "Clear" button
    And I set the "Name" to "Vacuum Cleaner"
    And I press the "Search" button
    Then I should not see "Vacuum Cleaner" in the results
    And I should see the message "No products found matching the search criteria"

Feature: Delete a product
  Scenario: Successfully deleting an existing product
    Given the product exists
    When I delete the product
    Then the product should be removed
    And I should see a flash message "Product has been deleted!"

  Scenario: Deleting a product that does not exist
    Given no product exists with the given ID
    When I delete the product
    Then I should see a flash message "Server error!"



Scenario: View a Product
    When I visit the "Home Page"
    And I set the "Name" to "E-Reader"
    And I press the "Search" button
    And I press the first result
    Then The modal should be visible
    And I should see "E-Reader" in the modal "Name" field
    And I should see "SKU123456" in the modal "SKU" field
    And I should see "Digital reader" in the modal "Description" field
    And I should see "129.99" in the modal "Price" field
    And I should see "https://www.google.com" in the modal "Image URL" field
    And I should see "0" in the modal "Likes" field

    When I press the "Modal Retrieve" button
    Then I should see the message "Success"
    And The modal should be hidden
    And I should see "E-Reader" in the "Name" field
    And I should see "SKU123456" in the "SKU" field
    And I should see "Digital reader" in the "Description" field
    And I should see "129.99" in the "Price" field
    And I should see "https://www.google.com" in the "Image URL" field
    And I should see "0" in the "Likes" field

    When I press the first result
    Then The modal should be visible

    When I press the "Modal Close" button
    Then The modal should be hidden

Scenario: Like a Product
    When I visit the "Home Page"
    And I set the "Name" to "MacBook Air"
    And I set the "SKU" to "SKU1010"
    And I set the "Description" to "Lightweight laptop"
    And I set the "Price" to "1099.99"
    And I set the "Image URL" to "https://example.com/macbook.jpg"
    And I press the "Create" button
    Then I should see the message "Success"

    When I copy the "Id" field
    And I press the "Like" button
    Then I should see the message "Success"
    And I should see "1" in the "Likes" field
master
