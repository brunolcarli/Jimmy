import pandas as pd


def get_sentiment_week_progress(queryset):
    """
    Calculates the sentiment positivity to last 7 days.
    param: queryset -> Answer QuerySet
    return: list[float]
    """
    data = [[int(i.sentiment), i.datetime.day] for i in queryset]
    df = pd.DataFrame(data, columns=['SENT', 'DAY'])
    counts = df.value_counts()
    df['COUNT'] = 0

    for meta, count in zip(counts.index, counts.values):
        sent, day = meta
        df.loc[(df.SENT==sent) & (df.DAY==day), 'COUNT'] = count

    return list(df.groupby('DAY').SENT.mean())
