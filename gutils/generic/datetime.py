from datetime import date, timedelta


def first_day_of_month(dt, year_delta=0, month_delta=0):
    y, m = dt.year + year_delta, dt.month + month_delta
    a, m = divmod(m - 1, 12)
    return date(y + a, m + 1, 1)


def last_day_of_month(dt):
    return first_day_of_month(dt, 0, 1) + timedelta(-1)


def calculate_age(born):
    today = date.today()
    try:
        birthday = born.replace(year=today.year)
    except ValueError:  # raised when birth date is February 29 and the current year is not a leap year
        birthday = born.replace(year=today.year, month=born.month+1, day=1)
    if birthday > today:
        return today.year - born.year - 1
    else:
        return today.year - born.year