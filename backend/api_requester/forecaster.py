import numpy as np
import pandas
import statsmodels.api as statsmodels


def create_features(t, period, harmonics_count):
    features = {"trend": t}

    for k in range(1, harmonics_count+1):
        angle = (2 * np.pi) * k * t / period

        features[f"sin_{k}"] = np.sin(angle)
        features[f"cos_{k}"] = np.cos(angle)

    return statsmodels.add_constant(pandas.DataFrame(features))


def forecast_modelling(data, forecast_duration, max_date, period=12, harmonics_count=2):
    y = np.asarray(data, dtype=float)

    if not np.all(np.isfinite(y)) or np.any(y < 0):
        raise ValueError("Error: Data values shall be finite and positive")

    t = np.arange(len(y))
    x = create_features(t, period, harmonics_count)

    model = statsmodels.GLM(
        y,
        x,
        family=statsmodels.families.Tweedie()
    ).fit()

    future_t = np.arange(len(y), len(y) + forecast_duration)
    future_x = create_features(future_t, period, harmonics_count)

    prediction = model.get_prediction(future_x)
    df = pandas.DataFrame(prediction.summary_frame())

    forecast_start = (
            pandas.Timestamp(max_date).to_period("M") + 1
    )

    months = pandas.period_range(
        start=forecast_start,
        periods=forecast_duration,
        freq="M"
    )

    df["month"] = months.strftime("%B")
    print(model.params)
    df["year"] = months.year

    return df.to_dict(orient="records")