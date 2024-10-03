import RPi.GPIO as GPIO
from hx711 import HX711

try:
    GPIO.setmode(GPIO.BCM)
    hx = HX711(dout_pin=20, pd_sck_pin=21)  # Retaining the same pin configuration

    # Tare the scale (zero the scale)
    err = hx.zero()
    if err:
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
        known_weight_grams = input('Write how many grams it was (e.g., 1000 for 1 kg) and press Enter: ')
        try:
            value = float(known_weight_grams)
            print(value, 'grams')
        except ValueError:
            print('Expected integer or float and I have got:', known_weight_grams)

        # Calculate the scale ratio based on known weight
        ratio = abs(reading / value)  # Using absolute value for the ratio
        hx.set_scale_ratio(15.12)
        print('Your ratio is', ratio)
    else:
        raise ValueError('Cannot calculate mean value. Try debug mode. Variable reading:', reading)

    # Final reading display
    input('Press Enter to show reading')
    reading = hx.get_data_mean()  # Get a new reading to display
    if reading:
        print('Current weight on the scale in grams is:', reading)
    else:
        print('Invalid data when reading current weight.')

except (KeyboardInterrupt, SystemExit):
    print('Bye :)')

finally:
    GPIO.cleanup()
