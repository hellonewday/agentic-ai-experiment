import re
import streamlit as st
from markdown import markdown
import pdfkit
import json

def show_confetti():
    st.balloons()

def markdown_to_pdf(markdown_text, output_path):
    html_text = markdown(markdown_text, extensions=['markdown.extensions.tables', 'markdown.extensions.extra', 'markdown.extensions.nl2br'])
    styled_html = f"""
    <body>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; margin: 0; padding: 20px;}}
            .report-container {{ max-width: 800px; margin: 0 auto; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); }}
            h1, h2, h3 {{ color: #2c3e50; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background-color: #f4f4f4; color: #2c3e50; font-weight: bold; }}
            td {{ background-color: #fff; }}
            tr:nth-child(odd) td {{ background-color: #f9f9f9; }}
            p, li {{ line-height: 1.6; margin: 10px 0; }}
            ol {{ padding-left: 20px; }}
        </style>
        <div class="report-container">
            {html_text}
        </div>
    </body>
    </html>
    """

    def get_options():
        return {
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'custom-header': [
                ('Accept-Encoding', 'gzip')
            ],
            'no-outline': None
        }
    pdfkit.from_string(styled_html, output_path, options=get_options())

def get_pdf_download_link(pdf_path, filename):
    with open(pdf_path, "rb") as f:
        pdf_data = f.read()
    return st.download_button(
        label="Download PDF",
        data=pdf_data,
        file_name=filename,
        mime="application/pdf",
    )

class StreamToExpander:
    def __init__(self, expander, st):
        self.expander = expander
        self.st = st
        self.buffer = []
        self.logs = []
        self.processed_entries = set() 
        self.log_container = self.expander.empty()
        self.colors = {'task': '#388E3C', 'agent': '#1565C0', 'tool': '#FF8F00', 'completion': '#2E7D32'}

    def write(self, data):
        cleaned_data = re.sub(r'\x1B\[[0-9;]*[mK]', '', data)

        task_match = re.search(r'Task:\s*(.*)', cleaned_data)
        if task_match:
            task_value = task_match.group(1).strip()
            self.st.toast(":robot_face: " + task_value)

        # Buffer the data
        self.buffer.append(cleaned_data)
        if "\n" in data:
            log_entry = ''.join(self.buffer).strip()
            if not re.search(r'[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}', log_entry):
                if log_entry not in self.processed_entries:
                    self.processed_entries.add(log_entry)
                    formatted_log = self.format_log(log_entry)
                    if formatted_log:
                        self.logs.append(formatted_log)
                        self.log_container.markdown(
                            '<div class="log-container">' + ''.join(self.logs) + '</div>',
                            unsafe_allow_html=True
                        )
            self.buffer = []

    def flush(self):
        pass 

    def get_logs(self):
        return '<div class="log-container">' + ''.join(self.logs) + '</div>'

    def format_log(self, log_entry):
        log_entry_normalized = log_entry.title()
        
        if "[📋 TASK STARTED:" in log_entry:
            task = log_entry_normalized.split("Task Started:")[1].split("]")[0].strip()
            return f'<div class="log-entry slideFadeIn" style="color: {self.colors["task"]};">📋 {self.wrap_text(task)}</div>'
        elif "[🤖 AGENT" in log_entry and "STARTED TASK" in log_entry:
            agent = log_entry_normalized.split("'")[1]
            return f'<div class="log-entry slideFadeIn" style="color: {self.colors["agent"]};">🤖 {agent} Started</div>'
        elif "Task:" in log_entry:
            task = log_entry_normalized.replace("Task:", "").strip()
            return f'<div class="log-entry slideFadeIn" style="color: {self.colors["task"]};">📋 {self.wrap_text(task)}</div>'
        elif "[🛠️ TOOL USAGE STARTED:" in log_entry:
            tool = log_entry_normalized.split("'")[1]
            return f'<div class="log-entry slideFadeIn" style="color: {self.colors["tool"]};">🛠️ {tool} Started</div>'
        elif "[✅ TOOL USAGE FINISHED:" in log_entry:
            tool = log_entry_normalized.split("'")[1]
            return f'<div class="log-entry slideFadeIn" style="color: {self.colors["tool"]};">✅ {tool} Finished</div>'
        elif "Tool Input:" in log_entry:
            input_data = log_entry_normalized.replace("Tool Input:", "").strip()
            formatted_input = self.prettify_json(input_data)
            return f'<div class="log-entry slideFadeIn" style="color: {self.colors["tool"]};">🔍 Input: {formatted_input}</div>'
        elif "Tool Output:" in log_entry:
            output = log_entry_normalized.replace("Tool Output:", "").strip()
            formatted_output = self.prettify_json(output)
            return f'<div class="log-entry slideFadeIn" style="color: {self.colors["tool"]};">📦 Output: {formatted_output}</div>'
        elif "Final Answer:" in log_entry:
            answer = log_entry_normalized.replace("Final Answer:", "").strip()
            formatted_answer = self.prettify_json(answer)
            return f'<div class="log-entry slideFadeIn" style="color: {self.colors["completion"]};">🎯 {formatted_answer}</div>'
        elif "[✅ TASK COMPLETED:" in log_entry:
            task = log_entry_normalized.split("Completed:")[1].split("]")[0].strip()
            return f'<div class="log-entry slideFadeIn" style="color: {self.colors["completion"]};">✅ {self.wrap_text(task)}</div>'
        elif "[✅ CREW 'CREW' COMPLETED" in log_entry:
            return f'<div class="log-entry slideFadeIn" style="color: {self.colors["completion"]};">✅ Process Completed</div>'
        return None 

    def wrap_text(self, text, max_length=50):
        """Wrap long text into multiple lines for readability."""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 <= max_length:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word) + 1
        if current_line:
            lines.append(" ".join(current_line))
        return " ".join(lines)

    def prettify_json(self, text):
        try:
            if text.strip().replace("## ", "").startswith(('{', '[')):
                json_data = json.loads(text)
                pretty_json = json.dumps(json_data, indent=2, ensure_ascii=False)
                return f'<pre style="margin: 0; padding: 5px; background-color: #f5f5f5; border-radius: 4px;">{pretty_json}</pre>'
            return 'All data fetched!'
        except json.JSONDecodeError:
            return 'All data fetched!'