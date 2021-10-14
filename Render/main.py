from flask import Flask, render_template, request, flash, jsonify
from jinja2 import Environment, FileSystemLoader, BaseLoader, Template
import yaml


app = Flask(__name__)


@app.route('/convert', methods=['GET', 'POST'])
def convert():
    if request.method == 'POST':
        if request.form.get('template_names'):
            if request.form.get('template_names') == 'selects':
                template_names = check_template_filenames()
                return render_template('convert.html', configresult='', jin='Wrong Selection', yamlt='your values here',template_names=template_names)
            file_name = request.form.get('template_names')
            template_file = open('configtemp/'+file_name, 'r')
            template_content = template_file.read()
            yinput = request.form.get('yamlt')
            template_names = check_template_filenames()
            return render_template('convert.html', configresult='', jin=template_content, yamlt='Please write your values in Yaml or Json', template_names=template_names)
        else:
            yinput = request.form.get('yamlt')
            yamlt = yaml.safe_load(yinput)
            jin = Template(request.form.get('jin'))
            configresult = jin.render(yamlt, Template = jin)
            template_names = check_template_filenames()
            return render_template('convert.html', configresult=configresult, jin = request.form['jin'], yamlt = yinput, template_names=template_names)
    elif request.method == 'GET':
        template_names = check_template_filenames()
        jin= "Select a template file or write your own Jinja2 template here"
        yamlt = "Your YAML or JSON values here"
        return render_template('convert.html', jin = jin, yamlt=yamlt, template_names = template_names)

def check_template_filenames():
    import os
    files = os.listdir('configtemp/')
    template_names = []
    for file in files:
        template_names.append(file)
    return template_names
if __name__ == "__main__":
    app.run(host = "0.0.0.0")
