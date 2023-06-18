"""Automating ordering a Robot from Robot Spare Bin Industries"""
from RPA.Archive import Archive
from RPA.Browser.Selenium import Selenium
from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.Tables import Tables, Table

browser = Selenium()
pdf = PDF()
archive = Archive()


ORDERS_FILE_URL = "https://robotsparebinindustries.com/orders.csv"

def open_the_robot_orders_website():
    browser.open_available_browser("https://robotsparebinindustries.com/#/robot-order")

def get_orders() -> Table:
    http = HTTP()
    tables = Tables()
    http.download(ORDERS_FILE_URL,"./output/orders.csv", overwrite=True)
    orders = tables.read_table_from_csv('./output/orders.csv', True)
    tables.filter_empty_rows(orders)
    return orders

def place_orders(orders: Table):
    for order in orders:
        if order:
            close_modal()
            order_id = order["Order number"]
            head = order["Head"]
            body = order["Body"]
            legs = order["Legs"]
            address = order["Address"]
            browser.select_from_list_by_value("head", head)
            browser.select_radio_button("body", body)
            browser.input_text("class:form-control", legs)
            browser.input_text("address", address)
            screenshot_order(order_id)
            while not browser.is_element_visible("id:receipt", True):
                browser.click_button("order")
            save_pdf_receipt(order)
            browser.wait_until_element_is_visible("id:order-another")
            browser.click_button("id:order-another")

def close_modal():
    try:
        browser.wait_until_element_is_visible("class:btn.btn-danger")
        browser.click_button("class:btn.btn-danger")
    except:
        pass

def screenshot_order(order_id: str):
    browser.wait_until_element_is_visible("preview")
    browser.click_button("preview")
    browser.wait_until_element_is_visible("id:robot-preview-image")
    browser.screenshot("id:robot-preview-image", f"./output/order{order_id}.png")

def save_pdf_receipt(order: Table):
    browser.wait_until_element_is_visible("id:receipt")
    receipt_html = browser.get_element_attribute("id:receipt", "outerHTML")
    pdf.html_to_pdf(receipt_html, f"./output/receipts/order{order['Order number']}_receipt.pdf")
    embed_screenshot(order)

def embed_screenshot(order: Table):
    order_id = order["Order number"]
    pdf.open_pdf(f"./output/receipts/order{order_id}_receipt.pdf")
    pdf.add_watermark_image_to_pdf(image_path=f"./output/order{order_id}.png", output_path=f"./output/receipts/order{order_id}_receipt.pdf")

if __name__ == "__main__":
    try:
        open_the_robot_orders_website()
        orders = get_orders()
        place_orders(orders)
        archive.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")
    finally:
        browser.close_browser()