def handle_mean_count(records):
    count = len(records)

    total_pressure = sum(record.pressure for record in records)
    total_temperature = sum(record.temperature for record in records)
    total_velocity = sum(record.velocity for record in records)

    avg_pressure = total_pressure / count
    avg_temperature = total_temperature / count
    avg_velocity = total_velocity / count

    return avg_pressure, avg_temperature, avg_velocity
