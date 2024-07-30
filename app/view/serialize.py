from datetime import datetime


def created_at_serializer(created_at: datetime):
    year, month, day = map(int, created_at.strftime("%Y.%m.%d").split('.'))

    if day == 1 and month == 1:
        return f"{year}년"

    if day == 1:
        return f"{year}년 {month}월"

    else:
        return f"{year}년 {month}월 {day}일"
