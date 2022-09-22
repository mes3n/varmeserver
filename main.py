from flask import Flask, request, render_template, redirect, url_for
import json

app = Flask(__name__)

parameters = [
    {
        "name": "Heat set 1, CurvL",    
        "idx": "2205",
        "vals": {
            "low": 80,
            "mid": 40,
            "high": 10
        }
    }, 
    {
        "name": "Heat set 3, Parallel", 
        "idx": "0207",
        "vals": {
            "low": 50,
            "mid": 20,
            "high": 0
        }
    }, 
    {
        "name": "Warm Water temp",      
        "idx": "0208",
        "vals": {
            "low": 550,
            "mid": 450,
            "high": 350
        }
    }
]



@app.route('/')
def home():
    return render_template('home.html', status=request.args.get('status', ''))


@app.route('/add_parameter', methods=['GET', 'POST'])
def add_parameter():
    return render_template('add_parameter.html')


@app.route('/list_parameters', methods=['GET', 'POST'])
def list_parameters():
    return render_template('list_parameters.html', parameters=parameters)  # parameters should load from file


@app.route('/edit_parameter', methods=['GET', 'POST'])
def edit_parameter():
    idx = request.args.get('idx', None)

    parameter = [parameter for parameter in parameters if parameter['idx'] == idx]  # select the chosen parameter from its idx

    if (len(parameter)):
        return render_template('edit_parameter.html', parameter=parameter[0])  # shouldn't be duplicates 
    else: 
        return redirect(url_for('/list_parameters'))


@app.route('/set_parameter', methods=['GET', 'POST'])
def set_parameter():

    if request.form['action'] == 'cancel':
        return redirect(url_for('home'))
    
    elif request.form['action'] == 'delete':
        idx = request.form.get('parameter_idx', type=str)

        for i, parameter in enumerate(parameters):
            if parameter['idx'] == idx:  # parameter was found, changing old one
                return redirect(url_for('home', status=f"Removed parameter: {parameters.pop(i)['name']}"))

        else:  # parameter was not found, adding new
            return redirect(url_for('home', status=f"Did not find parameter with idx: {idx}"))

    elif request.form['action'] == 'set':
        new_parameter = {
            "name": request.form.get('parameter_name', type=str),    
            "idx": request.form.get('parameter_idx', type=str),
            "vals": {
                "low": request.form.get('parameter_low', type=int),
                "mid": request.form.get('parameter_mid', type=int),
                "high": request.form.get('parameter_high', type=int)
            }
        }

        for i, parameter in enumerate(parameters):
            if parameter['idx'] == new_parameter['idx']:  # parameter was found, changing old one
                parameters[i] = new_parameter
                return redirect(url_for('home', status=f"Changed parameter: {new_parameter['name']}"))

        else:  # parameter was not found, adding new
            parameters.append(new_parameter)
            return redirect(url_for('home', status=f"Added parameter: {new_parameter['name']}"))


if __name__ == '__main__':
    app.run()
