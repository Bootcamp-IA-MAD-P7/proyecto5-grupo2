from app.backend.schemas import PredictionRequest
from app.backend.services.model_service import predict_cancellation


def sample_prediction_request() -> PredictionRequest:
    return PredictionRequest(
        lead_time=120,
        arrival_year=2018,
        arrival_month=7,
        arrival_date=15,
        no_of_special_requests=0,
        avg_price_per_room=156.0,
        market_segment_type="Online",
        no_of_weekend_nights=1,
        no_of_week_nights=2,
        type_of_meal_plan="Meal Plan 1",
        room_type_reserved="Room_Type 1",
        no_of_adults=2,
        no_of_children=0,
        required_car_parking_space=0,
        repeated_guest=0,
        no_of_previous_cancellations=0,
        no_of_previous_bookings_not_canceled=0,
    )


def test_risk_factors_are_ranked_by_local_impact() -> None:
    prediction = predict_cancellation(sample_prediction_request())

    assert 1 <= len(prediction.risk_factors) <= 3
    impacts = [factor.impact_percentage_points for factor in prediction.risk_factors]
    assert impacts == sorted(impacts, reverse=True)
    assert all(impact >= 0.1 for impact in impacts)
    assert prediction.main_factors == [factor.label for factor in prediction.risk_factors]


def test_risk_factor_explanation_contains_operational_context() -> None:
    prediction = predict_cancellation(sample_prediction_request())
    principal_factor = prediction.risk_factors[0]

    assert principal_factor.feature
    assert principal_factor.label
    assert principal_factor.current_value
    assert principal_factor.reference_value
    assert principal_factor.action.endswith(".")
