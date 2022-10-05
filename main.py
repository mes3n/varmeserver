from flask import Flask, request, render_template, redirect, url_for, send_file

from pathlib import Path
import json


app = Flask(__name__)


@app.route('/')
def home():
    status = request.args.get('status', '')

    return render_template('home.html', status=status)


@app.route('/add_parameter')
def add_parameter():
    return render_template('add_parameter.html')


@app.route('/list_parameters')
def list_parameters():
    return render_template('list_parameters.html', parameters=global_parameters)  # parameters should load from file


@app.route('/edit_parameter')
def edit_parameter():
    idx = request.args.get('idx', None)

    parameter = [parameter for parameter in global_parameters if parameter['idx'] == idx]  # select the chosen parameter from its idx

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

        for i, parameter in enumerate(global_parameters):
            if parameter['idx'] == idx:  # parameter was found, changing old one
                return redirect(url_for('home', status=f"Removed parameter: {global_parameters.pop(i)['name']}."))

        else:  # parameter was not found, adding new
            return redirect(url_for('home', status=f"Did not find parameter with idx: {idx}."))

    elif request.form['action'] == 'set':
        if len(request.form.get('parameter_idx', type=str)) < 4:
            return redirect(url_for('home', status=f"Invalid idx."))

        new_parameter = {
            'name': request.form.get('parameter_name', type=str),    
            'idx': request.form.get('parameter_idx', type=str),
            'vals': {
                'low': request.form.get('parameter_low', type=int),
                'mid': request.form.get('parameter_mid', type=int),
                'high': request.form.get('parameter_high', type=int)
            }
        }

        for i, parameter in enumerate(global_parameters):
            if parameter['idx'] == new_parameter['idx']:  # parameter was found, changing old one
                global_parameters[i] = new_parameter

                if global_parameters:
                    with open(parameters_path, 'w') as file:
                        file.write(json.dumps(global_parameters, indent=4))

                return redirect(url_for('home', status=f"Updated parameter: {new_parameter['name']}."))

        else:  # parameter was not found, adding new
            global_parameters.append(new_parameter)

            if global_parameters:
                with open(parameters_path, 'w') as file:
                    file.write(json.dumps(global_parameters, indent=4))

            return redirect(url_for('home', status=f"Added parameter: {new_parameter['name']}."))
    
    else:
        return redirect(url_for('home', status=f"Error: method not found."))



@app.route('/settings')
def settings ():
    return render_template('settings.html', config=global_config)  # shouldn't be duplicates 

@app.route('/set_settings', methods=['GET', 'POST'])
def set_settings ():

    if request.form['action'] == 'cancel':
        return redirect(url_for('home'))

    elif request.form['action'] == 'save':

        global_config['TOKEN'] = request.form.get('tibber_token', type=str)
        global_config['low_mid'] = request.form.get('low_mid_price', type=float)
        global_config['mid_high'] = request.form.get('mid_high_price', type=float)

        if global_config:
            with open(varmescript_config, 'w') as file:
                file.write(json.dumps(global_config, indent=4))

        return redirect(url_for('home', status=f"Saved settings."))

    else:
        return redirect(url_for('home', status=f"Error: method not found."))


@app.route('/database')
def database():
    return send_file(database_path)


if __name__ == '__main__':

    varmescript_path = Path('../varmescript/')
    parameters_path = Path(varmescript_path.joinpath('config/parameters.json'))
    
    varmescript_config = Path(varmescript_path.joinpath('config/config.json'))

    database_path = Path(varmescript_path.joinpath('database/husdata.csv'))

    if parameters_path.is_file():
        with open(parameters_path, 'r') as file:
            global_parameters = json.load(file)

    else:
        global_parameters = []

    if varmescript_config.is_file():
        with open(varmescript_config, 'r') as file:
            global_config = json.load(file)

    else:
        global_config = {}


    app.run(host="0.0.0.0", port=5000)
    # from waitress import serve
    # serve(app, host="0.0.0.0", port=5000)
