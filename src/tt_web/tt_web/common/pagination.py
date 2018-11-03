

def normalize_page(page, records_number, records_on_page):
    total_pages = records_number // records_on_page

    if total_pages * records_on_page < records_number:
        total_pages += 1

    if total_pages <= 0:
        total_pages = 1

    page = page if page <= total_pages else total_pages

    if page <= 0:
        page = 1

    return page
