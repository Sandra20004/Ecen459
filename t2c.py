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
        BNumbers = int(request.form['BNumbers'])  # Number of Conductors in the Bundle
        BSpacing = float(request.form['Bspacing'])  # Spacing between conductors in the bundle 
        LL = float(request.form['linelength'])  # Line Length (m)
        r = CDiameter / 2  # Radius of the conductor

        # Get the optional GMR input, if given
        CGMR = request.form.get('CGMR', None)  # None if not provided
        GMR = float(CGMR) if CGMR else None

        # Check if the line is transposed
        is_transposed = request.form.get('is_transposed')  # This will be None if not checked
        if is_transposed:
            # Get distances for transposed lines
            d12 = request.form.get('d12', '')
            d13 = request.form.get('d13', '')
            d23 = request.form.get('d23', '')

            # Ensure all distances are provided for transposed lines
            if not d12 or not d13 or not d23:
                raise ValueError("All distance values (d12, d13, d23) must be provided when the line is transposed.")

            # Convert to float after validation
            d12 = float(d12)
            d13 = float(d13)
            d23 = float(d23)
            GMD = (d12 * d13 * d23) ** (1/3)  # GMD Calculation for transposed line
        else:
            PSpacing = request.form.get('PSpacing', '')
            if not PSpacing:
                raise ValueError("Phase Spacing must be provided when the line is not transposed.")
            PSpacing = float(PSpacing)
            GMD = PSpacing  # Use phase spacing if the line is not transposed

        # Calculate GMR based on the number of bundles
        if BNumbers == 2:
            GMR_bundle = math.sqrt(BSpacing * GMR)
        elif BNumbers == 3:
            GMR_bundle = (BSpacing ** 2 * GMR) ** (1/3)
        elif BNumbers == 4:
            GMR_bundle = 1.091 * (BSpacing ** 3 * GMR) ** (1/4)
        else:
            GMR_bundle = GMR  # Single conductor or default GMR

        # Inductance Calculation (L_a)
        L_a = 2e-7 * math.log(GMD / GMR_bundle)

        # Capacitance Calculation
        epsilon_0 = 8.854e-12  # Permittivity of free space
        epsilon_r = 1  # Relative permittivity (assuming air here)

        # Calculate CGMR for capacitance based on the number of bundles
        if BNumbers == 2:
            CGMR_bundle = math.sqrt(BSpacing * r)
        elif BNumbers == 3:
            CGMR_bundle = (BSpacing ** 2 * r) ** (1/3)
        elif BNumbers == 4:
            CGMR_bundle = 1.091 * (BSpacing ** 3 * r) ** (1/4)
        else:
            CGMR_bundle = r  # Single conductor or default r

        C = ((2 * math.pi * epsilon_0 * epsilon_r) / math.log(GMD / CGMR_bundle))

        # Resistance Calculation
        R = (CResistance/BNumbers) * LL   # Resistance for the conductor bundle

        # Calculate Reactances
        X_L = 2 * math.pi * frequency * L_a * LL   # Inductive Reactance
        X_C = (1 / (2 * math.pi * frequency * C)) * LL # Capacitive Reactance

        # Return results to the HTML page
        return render_template('task2.html', resultR=round(R,2), resultXL=round(X_L,2), resultXC=round(X_C,2))

    except Exception as e:
        print(f"Error during calculation: {e}")
        return render_template('task2.html', error=f"An error occurred during calculation: {e}")


if __name__ == '__main__':
    app.run(debug=True)
