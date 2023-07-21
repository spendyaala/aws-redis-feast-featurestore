from datetime import timedelta

import pandas as pd

from feast import (
    Entity,
    FeatureService,
    FeatureView,
    Field,
    FileSource,
    PushSource,
    RequestSource,
    ValueType,
    RedshiftSource,
)
from feast.on_demand_feature_view import on_demand_feature_view
from feast.types import Float32, Float64, Int64, PrimitiveFeastType

zipcode = Entity(name="zipcode", value_type=ValueType.INT64)

zipcode_source =  RedshiftSource(
    table="zipcode_features",
    timestamp_field="event_timestamp",
    schema="spectrum",
    created_timestamp_column="created_timestamp",
    database="dev",
)

zipcode_features = FeatureView(
    name="zipcode_features",
    entities=[zipcode],
    ttl=timedelta(days=3650),
    schema=[
        Field(name="city", dtype=PrimitiveFeastType.STRING),
        Field(name="state", dtype=PrimitiveFeastType.STRING),
        Field(name="location_type", dtype=PrimitiveFeastType.STRING),
        Field(name="tax_returns_filed", dtype=PrimitiveFeastType.INT64),
        Field(name="population", dtype=PrimitiveFeastType.INT64),
        Field(name="total_wages", dtype=PrimitiveFeastType.INT64),
    ],
    online=True,
    source=zipcode_source,
)

dob_ssn = Entity(
    name="dob_ssn",
    value_type=ValueType.STRING,
    description="Date of birth and last four digits of social security number",
)

credit_history_source =  RedshiftSource(
    table="credit_history",
    timestamp_field="event_timestamp",
    schema="spectrum",
    created_timestamp_column="created_timestamp",
    database="dev",
)

credit_history = FeatureView(
    name="credit_history",
    entities=[dob_ssn],
    ttl=timedelta(days=90),
    schema=[
        Field(name="credit_card_due", dtype=PrimitiveFeastType.INT64),
        Field(name="mortgage_due", dtype=PrimitiveFeastType.INT64),
        Field(name="student_loan_due", dtype=PrimitiveFeastType.INT64),
        Field(name="vehicle_loan_due", dtype=PrimitiveFeastType.INT64),
        Field(name="hard_pulls", dtype=PrimitiveFeastType.INT64),
        Field(name="missed_payments_2y", dtype=PrimitiveFeastType.INT64),
        Field(name="missed_payments_1y", dtype=PrimitiveFeastType.INT64),
        Field(name="missed_payments_6m", dtype=PrimitiveFeastType.INT64),
        Field(name="bankruptcies", dtype=PrimitiveFeastType.INT64),
    ],
    online=True,
    source=credit_history_source,
)
