import os
import click
import importlib

def register_commands(app):
    commands_dir = os.path.dirname(__file__)
    
    # Walk through all subdirectories and files
    for root, _, files in os.walk(commands_dir):
        for filename in files:
            if not filename.endswith('.py') or filename.startswith('__'):
                continue
            
            # Construct the module name relative to the commands directory
            relative_path = os.path.relpath(os.path.join(root, filename), commands_dir)
            # Replace path separators with dots and remove the '.py' extension
            module_name = relative_path.replace(os.sep, '.')[:-3]
            
            # Import the module
            module = importlib.import_module(f'commands.{module_name}')
            for item in dir(module):
                item = getattr(module, item)
                if isinstance(item, click.Command):
                    app.cli.add_command(item)