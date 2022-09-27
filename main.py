from flask import Flask, request, render_template, redirect, url_for, send_file

from pathlib import Path
import json


app = Flask(__name__)


@app.route('/')
def home():
    status = request.args.get('status', '')

    if status and global_parameters and parameters_path.is_file():
        with open(parameters_path, 'w') as file:
            file.write(json.dumps(global_parameters, indent=4))

    return render_template('home.html', status=status)


@app.route('/add_parameter', methods=['GET', 'POST'])
def add_parameter():
    return render_template('add_parameter.html')


@app.route('/list_parameters', methods=['GET', 'POST'])
def list_parameters():
    return render_template('list_parameters.html', parameters=global_parameters)  # parameters should load from file


@app.route('/edit_parameter', methods=['GET', 'POST'])
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
                return redirect(url_for('home', status=f"Removed parameter: {global_parameters.pop(i)['name']}"))

        else:  # parameter was not found, adding new
            return redirect(url_for('home', status=f"Did not find parameter with idx: {idx}"))

    elif request.form['action'] == 'set':
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
                return redirect(url_for('home', status=f"Changed parameter: {new_parameter['name']}"))

        else:  # parameter was not found, adding new
            global_parameters.append(new_parameter)
            return redirect(url_for('home', status=f"Added parameter: {new_parameter['name']}"))


@app.route('/database')
def database():
    return send_file(database_path)


if __name__ == '__main__':

    varmescript_path = Path('../varmescript/')
    parameters_path = Path(varmescript_path.joinpath('config/parameters.json'))
    parameters_backup_path = Path(varmescript_path.joinpath('config/parameters.bak.json'))

    database_path = Path(varmescript_path.joinpath('database/husdata.csv'))

    if parameters_path.is_file():
        with open(parameters_path, 'r') as file:
            global_parameters = json.load(file)

    elif parameters_backup_path.is_file():
        with open(parameters_backup_path, 'r') as file:
            global_parameters = json.load(file)

    else:
        global_parameters = []
    

    app.run(host="0.0.0.0", port=5000)  # localhost and on local network
