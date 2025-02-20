from skyfield.api import load, Topos, Star
from skyfield.data import hipparcos
from skyfield import almanac

def main():
    # Load ephemeris data for accurate astronomical calculations
    print("Loading ephemeris data...")
    eph = load('de421.bsp')  # Ephemeris file for celestial body positions

    # Load Polaris data from Skyfield's cache or Hipparcos catalog
    print("Loading Polaris data from Skyfield's cache...")
    with load.open(hipparcos.URL) as f:
        hipparcos_data = hipparcos.load_dataframe(f)
    polaris = Star.from_dataframe(hipparcos_data.loc[11767])

    # Define observer location (latitude, longitude)
    observer_lat = 38.478752
    observer_lon = -107.877739
    observer = Topos(latitude_degrees=observer_lat, longitude_degrees=observer_lon)

    # Define celestial objects to observe
    sun = eph['sun']
    moon = eph['moon']
    mars = eph['mars']

    # Get the current time using Skyfield's timescale
    ts = load.timescale()
    now = ts.now()

    # Calculate ideal time based on longitude
    ideal_offset_hours = round(observer_lon / 15.0)  # Convert longitude to hour offset
    ideal_time_tt = now.tt + (ideal_offset_hours / 24.0)  # Apply offset in fractional days
    ideal_time = ts.tt_jd(ideal_time_tt)  # Convert back to a Skyfield Time object

    # Format times using Skyfield's time formatting
    zulu_time = now.utc_iso(places=0)
    ideal_time_formatted = ideal_time.utc_iso(places=0).replace("Z", "")  # Remove "Z"

    # Calculate positions of celestial bodies
    print("\nCalculating positions of celestial objects:")
    print(f"Current Time:")
    print(f"Zulu: {zulu_time}")
    print(f"Ideal: {ideal_time_formatted}")

    # Observer's position at the current time
    observer_location = eph['earth'] + observer

    # Apparent positions of celestial objects
    sun_position = observer_location.at(now).observe(sun).apparent()
    moon_position = observer_location.at(now).observe(moon).apparent()
    mars_position = observer_location.at(now).observe(mars).apparent()
    polaris_position = observer_location.at(now).observe(polaris).apparent()

    # Compute altitudes and azimuths
    sun_alt, sun_az, _ = sun_position.altaz()
    moon_alt, moon_az, _ = moon_position.altaz()
    mars_alt, mars_az, _ = mars_position.altaz()
    polaris_alt, polaris_az, _ = polaris_position.altaz()

    # Display results
    print("\nCelestial Object Positions:")
    print(f"Sun - Altitude: {sun_alt.degrees:.2f}°, Azimuth: {sun_az.degrees:.2f}°")
    print(f"Moon - Altitude: {moon_alt.degrees:.2f}°, Azimuth: {moon_az.degrees:.2f}°")
    print(f"Mars - Altitude: {mars_alt.degrees:.2f}°, Azimuth: {mars_az.degrees:.2f}°")
    print(f"Polaris - Altitude: {polaris_alt.degrees:.2f}°, Azimuth: {polaris_az.degrees:.2f}°")

    # Calculate sunrise, sunset, moonrise, and moonset times
    print("\nNext Rise and Set Times:")

    # Define time range for calculations (using Skyfield's timescale)
    t0 = now  # Start at the current time
    t1 = now + (18 / 24)  # 18 hours from now (fraction of a day)

    # Sunrise and sunset times
    f = almanac.sunrise_sunset(eph, observer)
    times, events = almanac.find_discrete(t0, t1, f)
    
    for t, e in zip(times, events):
        if e == 1:
            print(f"Sunrise: {t.utc_iso()}")
        elif e == 0:
            print(f"Sunset: {t.utc_iso()}")

    # Moonrise and moonset times
    f = almanac.risings_and_settings(eph, eph['moon'], observer)
    times, events = almanac.find_discrete(t0, t1, f)
    
    for t, e in zip(times, events):
        if e == True:
            print(f"Moonrise: {t.utc_iso()}")
        elif e == False:
            print(f"Moonset: {t.utc_iso()}")

if __name__ == "__main__":
    main()