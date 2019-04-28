Feature: The store service back-end
    As a customer
    I need a RESTful catalog service
    So that I can keep track of all my wishlists

Background:
    Given the following wishlists
        | name   | customer_id |
        | A      | 100         |
        | B      | 101         |
        | C      | 102         |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Wishlist Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Wishlist
    When I visit the "Home Page"
    And I set the "Name" to "D"
    And I set the "Customer_id" to "104"
    And I press the "Create" button
    Then I should see the message "Success"

Scenario: List all wishlists
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "A" in the results
    And I should see "B" in the results
    And I should see "C" in the results

Scenario: Update a Wishlist
    When I visit the "Home Page"
    And I set the "Name" to "A"
    And I press the "Search" button
    Then I should see "A" in the "Name" field
    And I should see "100" in the "CustomerId" field
    When I change "Name" to "AB"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see "AB" in the "Name" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see "AB" in the results
    Then I should not see "A" in the results

