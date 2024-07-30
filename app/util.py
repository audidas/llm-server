from datetime import datetime, timedelta


def kst_now() -> datetime:
    kst = datetime.utcnow() + timedelta(hours=9)
    kst_timestamp = kst.timestamp()
    from_timestamp = datetime.fromtimestamp(kst_timestamp)

    return kst
