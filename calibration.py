import RPi.GPIO as GPIO
from hx711 import HX711

try:
    GPIO.setmode(GPIO.BCM)
    hx = HX711(dout_pin=20, pd_sck_pin=21)

    # Tare the scale (zero the scale)
    if hx.zero():
        raise ValueError('Tare is unsuccessful.')

    # Get raw data to confirm initialization
    reading = hx.get_raw_data_mean()
    if reading:
        print('Data subtracted by offset but still not converted to units:', reading)
    else:
        print('Invalid data', reading)

    # Prompt user for a known weight for calibration
    input('Put known weight on the scale (up to 10 kg) and then press Enter')
    reading = hx.get_data_mean()
    if reading:
        print('Mean value from HX711 subtracted by offset:', reading)
        
        # Get the known weight from user input
        while True:
            known_weight_grams = input('Write how many grams it was (e.g., 1000 for 1 kg) and press Enter: ')
            try:
                value = float(known_weight_grams)
                print(value, 'grams')
                break  # Exit loop on valid input
            except ValueError:
                print('Expected integer or float. Please try again.')

        # Set a fixed reading value close to the known weight
        fixed_reading = reading  # You can adjust this to a specific value if needed
        print('Using fixed reading for calibration:', fixed_reading)

        # Calculate the scale ratio using the fixed reading
        ratio = abs(fixed_reading / value)
        hx.set_scale_ratio(ratio)
        print('Your ratio is', ratio)
    else:
        raise ValueError('Cannot calculate mean value. Try debug mode. Variable reading:', reading)

    # Final reading display
    input('Press Enter to show reading')
    reading = hx.get_data_mean()
    if reading:
        print('Current weight on the scale in grams is:', reading)
    else:
        print('Invalid data when reading current weight.')

except (KeyboardInterrupt, SystemExit):
    print('Bye :)')

except Exception as e:
    print('An unexpected error occurred:', e)

finally:
    GPIO.cleanup()
