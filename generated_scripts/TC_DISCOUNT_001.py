from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

html_file_path = "file:///D:/Personal/Projects/qa-agent/autonomous-qa-agent/data/html/checkout.html"

driver = webdriver.Chrome()
driver.get(html_file_path)
wait = WebDriverWait(driver, 10)

try:
    # Step 1: Add Item A to cart.
    add_item1_button = wait.until(EC.element_to_be_clickable((By.ID, "add-item1")))
    add_item1_button.click()

    # Step 2: Enter 'SAVE15' in the discount code input.
    discount_code_input = wait.until(EC.visibility_of_element_located((By.ID, "discount-code")))
    discount_code_input.send_keys("SAVE15")

    # Step 3: Click 'Apply' button.
    apply_discount_button = wait.until(EC.element_to_be_clickable((By.ID, "apply-discount")))
    apply_discount_button.click()

    # Expected Result Verification:
    # Discount message 'Discount applied!' is displayed in green.
    discount_message = wait.until(EC.visibility_of_element_located((By.ID, "discount-msg")))
    assert discount_message.text == "Discount applied!"
    assert "success" in discount_message.get_attribute("class")

    # Total price is reduced by 15%.
    # First, get the original total before discount (assuming Item A is $20)
    # The script applies the discount and updates the total. We need to check the final total.
    # The JS calculates the total as 20 * 0.85 = 17.00 after discount.
    final_total_element = wait.until(EC.visibility_of_element_located((By.ID, "total")))
    final_total_text = final_total_element.text
    assert final_total_text == "17.00"

    print("TEST PASSED: Discount code 'SAVE15' applied successfully, discount message displayed in green, and total price reduced by 15%.")

except Exception as e:
    print("TEST FAILED:", e)
finally:
    print("Test completed.")
    input("Press ENTER to close browser...")
    driver.quit()