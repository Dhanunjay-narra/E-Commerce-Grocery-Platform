def evaluate_cold_chain_telemetry(temp_c: float, max_safe_c: float = 4.0) -> dict:
    breach = temp_c > max_safe_c
    status = "TEMPERATURE_BREACH_ALERT" if breach else "SAFE_OPTIMAL"
    return {"temperature_c": temp_c, "is_breach": breach, "status": status}
