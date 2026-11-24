def can_book(capacity, booked, requested):
    return requested >= 0 and booked + requested <= capacity
