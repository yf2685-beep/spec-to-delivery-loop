def can_book(capacity, booked, requested):
    return (capacity >= 0 and booked >= 0 and requested > 0
            and booked + requested <= capacity)
