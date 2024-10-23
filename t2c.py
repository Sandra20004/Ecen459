from flask import Flask, render_template, request
import math

app = Flask(__name__, template_folder='templates')


@app.route('/')
def index():
    return render_template('task2.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # Get input values from the HTML form
        frequency = float(request.form['frequency'])
        CDiameter = float(request.form['CDiameter'])  # Conductor Diameter (m)
        CResistance = float(request.form['CResistance'])  # Conductor Resistance (Ω/m)
        BNumbers = int(request.form['BNumbers'])      # Number of Conductors in the Bundle
        PSpacing = float(request.form['PSpacing'])    # Phase Spacing (m)
        LL= float(request.form['linelength']) #line length
        r = CDiameter / 2  # Radius of the conductor

        # Get the optional GMR input, if given
        CGMR = request.form.get('CGMR', None)  # None if not provided
        GMR = float(CGMR) if CGMR else None

        # Calculate GMR for single conductor case if GMR isn't provided
        if BNumbers == 1 and not GMR:
            GMR = r * math.exp(-1/4)  # GMR for single conductor without GMR provided

        # Check if the line is transposed
        is_transposed = request.form.get('is_transposed')  # This will be None if not checked
        if is_transposed:
            # Get distances for transposed lines
            d12 = float(request.form['d12'])
            d13 = float(request.form['d13'])
            d23 = float(request.form['d23'])
            GMD = (d12 * d13 * d23) ** (1/3)  # GMD Calculation for transposed line
        else:
            GMD = LL  # Use phase spacing if line is not transposed

        # Calculate GMR based on the number of bundles
        if BNumbers == 2:
            GMR_bundle = math.sqrt(PSpacing * GMR)
        elif BNumbers == 3:
            GMR_bundle = (PSpacing**2 * GMR) ** (1/3)
        elif BNumbers == 4:
            GMR_bundle = 1.091 * (PSpacing**3 * GMR) ** (1/4)
        else:
            GMR_bundle = GMR  # Single conductor or default GMR

        # Inductance Calculation (La)
        if is_transposed:
            L_a = 2e-7 * math.log(GMD / GMR_bundle)
        else:
            L_a = 2e-7 * math.log(LL / GMR_bundle)

        # Capacitance Calculation
        epsilon_0 = 8.854e-12  # Permittivity of free space
        epsilon_r = 1  # Relative permittivity (assuming air here)

        if is_transposed:
            C = (2 * math.pi * epsilon_0 * epsilon_r) / math.log(GMD / GMR_bundle)
        else:
            C = (2 * math.pi * epsilon_0 * epsilon_r) / math.log(LL / GMR_bundle)

        # Resistance Calculation
        R = CResistance / BNumbers  # Resistance for the conductor bundle

        # Calculate Reactances
        X_L = 2 * math.pi * frequency * L_a  # Inductive Reactance
        X_C = 1 / (2 * math.pi * frequency * C)  # Capacitive Reactance

        # Return results to the HTML page
        return render_template('task2.html', resultR=R, resultXL=X_L, resultXC=X_C)

    except Exception as e:
        print(f"Error during calculation: {e}")
        return render_template('task2.html', error="An error occurred during calculation.")


if __name__ == '__main__':
    app.run(debug=True)
