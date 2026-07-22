from datetime import date, datetime

DATE_FORMATS = (
    '%Y-%m-%d',
    '%d/%m/%Y',
    '%d-%m-%Y',
    '%d-%b-%Y',
    '%d-%b-%y',
)


def parse_date(raw_date: object, row_number: int) -> date:
    """Parse DOB from supported ERP formats into a date object."""
    text = str(raw_date).strip()
    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(text, date_format).date()
        except ValueError:
            continue

    raise ValueError(
        f'Row {row_number}: could not parse date_of_birth {text!r}'
    )


def parse_class(raw_class: object, row_number: int) -> int:
    """Parse the class column as an integer."""
    try:
        return int(str(raw_class).strip())
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f'Row {row_number}: invalid class value {raw_class!r}'
        ) from exc
