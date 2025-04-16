"""
Web Steps

Steps file for web interactions with Selenium

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""

import re

import logging
from typing import Any

from behave import when, then  # pylint: disable=no-name-in-module

from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait  # , Select
from selenium.webdriver.support import expected_conditions

ID_PREFIX = "product_"


def save_screenshot(context: Any, filename: str) -> None:
    """Takes a snapshot of the web page for debugging and validation

    Args:
        context (Any): The session context
        filename (str): The message that you are looking for
    """
    # Remove all non-word characters (everything except numbers and letters)
    filename = re.sub(r"[^\w\s]", "", filename)
    # Replace all runs of whitespace with a single dash
    filename = re.sub(r"\s+", "-", filename)
    context.driver.save_screenshot(f"./captures/{filename}.png")


@when('I visit the "Home Page"')
def step_impl(context: Any) -> None:
    """Make a call to the base URL"""
    context.driver.get(context.base_url)
    # Uncomment next line to take a screenshot of the web page
    # save_screenshot(context, "Home_Page.png")


@then('I should see "{message}" in the title')
def step_impl(context: Any, message: str) -> None:
    """Check the document title for a message"""
    assert message in context.driver.title


@then('I should not see "{text_string}"')
def step_impl(context: Any, text_string: str) -> None:
    element = context.driver.find_element(By.TAG_NAME, "body")
    assert text_string not in element.text


@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context: Any, element_name: str, text_string: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(text_string)


@when("I clear all form fields")
def step_impl(context: Any) -> None:
    """Clears all form fields"""
    # Get a list of all input fields with the product prefix
    input_fields = context.driver.find_elements(
        By.CSS_SELECTOR, f"input[id^='{ID_PREFIX}']"
    )
    # Also get textarea fields if you have them
    textarea_fields = context.driver.find_elements(
        By.CSS_SELECTOR, f"textarea[id^='{ID_PREFIX}']"
    )

    # Clear each input field
    for field in input_fields:
        field.clear()

    # Clear each textarea field
    for field in textarea_fields:
        field.clear()


# @when('I select "{text}" in the "{element_name}" dropdown')
# def step_impl(context: Any, text: str, element_name: str) -> None:
#     element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
#     element = Select(context.driver.find_element(By.ID, element_id))
#     element.select_by_visible_text(text)


# @then('I should see "{text}" in the "{element_name}" dropdown')
# def step_impl(context: Any, text: str, element_name: str) -> None:
#     element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
#     element = Select(context.driver.find_element(By.ID, element_id))
#     assert element.first_selected_option.text == text


@then('the "{element_name}" field should be empty')
def step_impl(context: Any, element_name: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    assert element.get_attribute("value") == ""


##################################################################
# These two function simulate copy and paste
##################################################################
@when('I copy the "{element_name}" field')
def step_impl(context: Any, element_name: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute("value")
    logging.info("Clipboard contains: %s", context.clipboard)


@when('I paste the "{element_name}" field')
def step_impl(context: Any, element_name: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)


# ##################################################################
# # This code works because of the following naming convention:
# # The buttons have an id in the html hat is the button text
# # in lowercase followed by '-btn' so the Clear button has an id of
# # id='clear-btn'. That allows us to lowercase the name and add '-btn'
# # to get the element id of any button
# ##################################################################


@when('I press the "{button}" button')
def step_impl(context: Any, button: str) -> None:
    button_id = button.lower().replace(" ", "_") + "-btn"
    context.driver.find_element(By.ID, button_id).click()


@then('I should see "{name}" in the results')
def step_impl(context: Any, name: str) -> None:
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "search_results"), name
        )
    )
    assert found


@then('I should not see "{name}" in the results')
def step_impl(context: Any, name: str) -> None:
    element = context.driver.find_element(By.ID, "search_results")
    assert name not in element.text


@then('I should see the message "{message}"')
def step_impl(context: Any, message: str) -> None:
    # Uncomment next line to take a screenshot of the web page for debugging
    # save_screenshot(context, message)
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "flash_message"), message
        )
    )
    assert found


# ##################################################################
# # This code works because of the following naming convention:
# # The id field for text input in the html is the element name
# # prefixed by ID_PREFIX so the Name field has an id='product_name'
# # We can then lowercase the name and prefix with product_ to get the id
# ##################################################################


@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context: Any, text_string: str, element_name: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id), text_string
        )
    )
    assert found


@when('I change "{element_name}" to "{text_string}"')
def step_impl(context: Any, element_name: str, text_string: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)

###

@when("I press the first result")
def step_impl(context: Any) -> None:
    element_id = "row_0"
    context.driver.find_element(By.ID, element_id).click()

@then('I should see "{text_string}" in the modal "{element_name}" field')
def step_impl(context: Any, text_string: str, element_name: str) -> None:
    element_id = "modal_" + element_name.lower().replace(" ", "_")
    print(element_id)
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, element_id), text_string
        )
    )
    assert found

@then("The modal should be visible")
def step_impl(context: Any):
    element = context.driver.find_element(By.ID, "overlay")
    style = element.get_attribute("style")
    assert "display: flex" in style

@then("The modal should be hidden")
def step_impl(context: Any):
    element = context.driver.find_element(By.ID, "overlay")
    style = element.get_attribute("style")
    assert "display: none" in style



# ##################################################################
# ##################################################################

@when('I press the "Delete" button')
def step_impl(context: Any) -> None:
    # Use the generic button press step to handle the "Delete" button
    context.execute_steps('When I press the "Delete" button')

@when('I confirm the deletion')
def step_impl(context) -> None:
    alert = context.driver.switch_to.alert
    alert.accept()

@then('I should see the message "{message}"')
def step_impl(context: Any, message: str) -> None:
    flash_message = context.driver.find_element(By.ID, "flash_message").text
    assert message in flash_message, f"Expected '{message}' in flash message but got '{flash_message}'"

@then('I should not see "{product_name}" in the results')
def step_impl(context: Any, product_name: str) -> None:
    body = context.driver.find_element(By.TAG_NAME, "body").text
    assert product_name not in body, f"Expected not to find '{product_name}' in the results"
