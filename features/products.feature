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