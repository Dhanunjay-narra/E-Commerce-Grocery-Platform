from app.modules.iot.cold_chain import evaluate_cold_chain_telemetry

def test_cold_chain_temperature_breach():
    res = evaluate_cold_chain_telemetry(7.2)
    assert res["is_breach"] is True
    assert res["status"] == "TEMPERATURE_BREACH_ALERT"
