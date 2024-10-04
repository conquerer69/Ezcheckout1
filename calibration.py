import RPi.GPIO as GPIO
from hx711 import HX711
import time

try:
    # Set up GPIO pins
    GPIO.setmode(GPIO.BCM)
    hx = HX711(dout_pin=20, pd_sck_pin=21)  # Define the pins for HX711

    # Tare the scale (zero the scale)
    print("Taring the scale... Make sure it's empty.")
    err = hx.zero()
    if err:
        raise ValueError('Tare was unsuccessful.')

    # Get raw data to confirm initialization
    reading = hx.get_raw_data_mean()
    if reading:
        print('Data subtracted by offset but still not converted to units:', reading)
    else:
        print('Invalid data:', reading)

    # Prompt user for a known weight for calibration
    input('Place a known weight on the scale (up to 10 kg) and press Enter...')
    reading = hx.get_data_mean()
    if reading:
        print('Mean value from HX711 subtracted by offset:', reading)

        # Error handling for known weight input
        while True:
            known_weight_grams = input('Enter the known weight in grams (e.g., 1000 for 1 kg): ')
            try:
                value = float(known_weight_grams)
                if value <= 0 or value > 10000:  # Limit the weight to a reasonable range
                    print('Please enter a positive number less than or equal to 10,000.')
                else:
                    print(f'Entered known weight: {value} grams')
                    break
            except ValueError:
                print('Invalid input. Expected an integer or float.')

        # Use the last reading as the fixed reading value
        fixed_reading = reading  
        ratio = abs(fixed_reading / value)  # Calculate ratio based on the known weight
        hx.set_scale_ratio(ratio)  # Set the calculated ratio
        print(f'Calibration successful. Your calculated ratio is: {ratio}')

        # Continuous weight display loop
        print('Starting continuous weight reading. Press Ctrl+C to exit.')
        while True:
            try:
                # Get a new reading to display the current weight
                weight = hx.get_weight_mean(10)  # Read 10 samples and get the average
                if weight:
                    print(f'Current weight on the scale: {weight:.2f} grams')
                    
                    # Update the fixed reading if the current weight is closer to the known weight
                    if abs(weight - value) < abs(fixed_reading - value):
                        fixed_reading = weight
                        print(f'Updated fixed reading value: {fixed_reading:.2f} grams')

                else:
                    print('Invalid data when reading current weight.')

                # Wait for a short interval before reading again
                time.sleep(1)

            except (KeyboardInterrupt, SystemExit):
                print('Exiting continuous reading loop.')
                break

except (KeyboardInterrupt, SystemExit):
    print('Program interrupted by the user.')

except ValueError as ve:
    print(f'Error: {ve}')

finally:
    GPIO.cleanup()  # Clean up GPIO to avoid warnings on subsequent runs
    print('GPIO cleaned up and program terminated.')
