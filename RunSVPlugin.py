import sublime
import sublime_plugin
import subprocess

class RunSvScriptCommand(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        if view is None:
            sublime.error_message("No active file.")
            return

        file_path = view.file_name()
        if not file_path or not file_path.endswith(".sv"):
            sublime.error_message("This command can only be used with SV files.")
            return

        # Path to your Python script
        python_script = "/Users/mattreister/Sandbox/eunit_m/src/sv_extract.py"

        try:
            # Run the Python script with the file as an argument
            process = subprocess.Popen(
                ["python", python_script, file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                sublime.message_dialog("Script Output:\n" + stdout)
            else:
                sublime.error_message("Error running script:\n" + stderr)
        except Exception as e:
            sublime.error_message("An error occurred: " + str(e))
