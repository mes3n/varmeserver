from flask import Flask, request, render_template, redirect, url_for, send_file

from pathlib import Path
import json

import threading
import asyncio

import subprocess


app = Flask(__name__)


class ScriptThread():
    def __init__(self, script_directory):
        self.process: subprocess.Popen = None
        self.script_dir: str = script_directory
        self.pid = '0'

        self.running = False

    def start(self):
        commands = f'cd {self.script_dir}; python main.py'
        self.process = subprocess.Popen(commands, stdout=subprocess.PIPE, shell=True)
        self.pid = self.process.pid

        self.running = True

    def stop(self):
        commands = f'kill {self.pid}'
        self.process = subprocess.Popen(commands, stdout=subprocess.PIPE, shell=True)
        
        self.running = False



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
                    with open(script_parameters, 'w') as file:
                        file.write(json.dumps(global_parameters, indent=4))

                return redirect(url_for('home', status=f"Updated parameter: {new_parameter['name']}."))

        else:  # parameter was not found, adding new
            global_parameters.append(new_parameter)

            if global_parameters:
                with open(script_parameters, 'w') as file:
                    file.write(json.dumps(global_parameters, indent=4))

            return redirect(url_for('home', status=f"Added parameter: {new_parameter['name']}."))
    
    else:
        return redirect(url_for('home', status=f"Error: method not found."))


@app.route('/settings')
def settings ():
    return render_template('settings.html', config=global_config, script_should_run=script_should_run)  # shouldn't be duplicates 


@app.route('/set_settings', methods=['GET', 'POST'])
def set_settings ():
    global script_should_run

    if request.form['action'] == 'cancel':
        return redirect(url_for('home'))

    elif request.form['action'] == 'save':

        global_config['TOKEN'] = request.form.get('tibber_token', type=str)
        global_config['husdata_ip'] = request.form.get('husdata_ip', type=str)
        global_config['low_mid'] = request.form.get('low_mid_price', type=float)
        global_config['mid_high'] = request.form.get('mid_high_price', type=float)
        script_should_run = request.form.get('script_toggle_on') != None

        if global_config:
            with open(script_config, 'w') as file:
                file.write(json.dumps(global_config, indent=4))

        if script_should_run and not script_thread.running:
            script_thread.start()
        elif not script_should_run and script_thread.running:
            script_thread.stop()

        return redirect(url_for('home', status=f"Saved settings."))

    else:
        return redirect(url_for('home', status=f"Error: method not found."))


@app.route('/database')
def database():
    return send_file(script_database)


def start_script():
    subprocess.run([f'cd {script_dir};', 'python main.py &'], shell=True)
    pid = int(subprocess.run(['echo $!'], capture_output=True, shell=True))

if __name__ == '__main__':

    paths = Path('paths.json')
    if paths.is_file():
        with open(paths, 'r') as file:
            paths_dict = json.load(file)
            script_dir = Path(paths_dict['script_dir'])    
            script_config = Path(paths_dict['script_config'])
            script_database = Path(paths_dict['script_database'])
            script_parameters = Path(paths_dict['script_parameters'])    
    else:
        script_dir = Path('')    
        script_config = Path('')
        script_database = Path('')
        script_parameters = Path('')

    if script_parameters.is_file():
        with open(script_parameters, 'r') as file:
            global_parameters = json.load(file)
    else:
        global_parameters = []

    if script_config.is_file():
        with open(script_config, 'r') as file:
            global_config = json.load(file)
    else:
        global_config = {}

    script_should_run: bool = False
    script_thread: ScriptThread = ScriptThread(script_dir)

    app.run(host="0.0.0.0", port=5000, debug=True)
    # from waitress import serve
    # serve(app, host="0.0.0.0", port=5000)
