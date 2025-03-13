import re
import streamlit as st
from markdown import markdown
import pdfkit
import json

def show_confetti():
    st.balloons()

def markdown_to_pdf(markdown_text, output_path):
    html_text = markdown(markdown_text)
    pdfkit.from_string(html_text, output_path)

def get_pdf_download_link(pdf_path, filename):
    with open(pdf_path, "rb") as f:
        pdf_data = f.read()
    return st.download_button(
        label="Download PDF",
        data=pdf_data,
        file_name=filename,
        mime="application/pdf",
    )

I understand the issue: the StreamToExpander class is causing duplicate log entries in the "Processing Log" expander. When a new log entry is added, instead of appending only the new entry, the entire list of logs (self.logs) is re-rendered, which can lead to duplicates if the same log entry is processed multiple times or if the rendering logic in Streamlit doesn’t handle updates correctly. This makes the log output hard to read and cluttered.

Let’s analyze the root cause and fix the logic to ensure:

Only new log entries are added to the expander without duplicating previous entries.
The rendering process avoids re-rendering the entire log history in a way that causes duplicates.
Step 1: Analyze the Bug
The write method in StreamToExpander buffers incoming data (self.buffer) until a newline (\n) is detected, at which point it processes the buffered data as a log_entry. Here’s the relevant part of the write method:

python

Thu gọn

Bọc lại

Sao chép
self.buffer.append(cleaned_data)
if "\n" in data:
    log_entry = ''.join(self.buffer).strip()
    if not re.search(r'[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}', log_entry):
        formatted_log = self.format_log(log_entry)
        if formatted_log:
            self.logs.append(formatted_log)
            self.expander.markdown(
                '<div class="log-container">' + ''.join(self.logs) + '</div>',
                unsafe_allow_html=True
            )
    self.buffer = []
Root Cause of Duplicates
Re-rendering Entire Log List: Every time a new log entry is processed, self.logs.append(formatted_log) adds the new entry to the self.logs list, and then self.expander.markdown re-renders the entire self.logs list (''.join(self.logs)) inside the <div class="log-container">. Streamlit’s markdown method isn’t designed for incremental updates—it overwrites the previous content in the expander. However, due to how Streamlit handles state and rendering, the old content might not be fully cleared, leading to duplicates.
Streamlit Rendering Behavior: Streamlit re-renders the entire app on every state change. If expander.markdown is called multiple times with overlapping content, Streamlit might append the new rendering to the previous one instead of replacing it, especially if the expander’s internal state isn’t managed correctly.
Potential for Duplicate Processing: If the same log_entry is processed multiple times (e.g., due to how data is streamed or if run_analysis outputs overlapping log entries), it will be appended to self.logs multiple times, exacerbating the duplication issue.
Expected Behavior
When a new log entry is detected, it should be formatted and added to the self.logs list only once.
The expander should display the new log entry without re-rendering or duplicating previous entries.
Step 2: Fix the Logic to Avoid Duplicates
To fix this, we’ll modify the StreamToExpander class to:

Track Processed Log Entries: Use a set to track unique log entries and avoid adding duplicates to self.logs.
Incremental Rendering: Instead of re-rendering the entire self.logs list every time, we’ll use Streamlit’s expander.markdown in a way that appends only the new log entry, leveraging Streamlit’s delta mechanism (e.g., using expander.empty() and container to manage updates).
Here’s the updated StreamToExpander class with these fixes:

Updated StreamToExpander
python

Thu gọn

Bọc lại

Sao chép
import re
import json

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
            return text
        except json.JSONDecodeError:
            return text