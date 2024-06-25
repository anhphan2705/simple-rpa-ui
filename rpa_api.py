from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import rpa as r
import uuid

app = FastAPI()

# Ensure the 'screenshots' and 'written_files' directories exist
os.makedirs('screenshots', exist_ok=True)
os.makedirs('written_files', exist_ok=True)

# Serve the static files in the 'screenshots' and 'written_files' directories
app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")
app.mount("/written_files", StaticFiles(directory="written_files"), name="written_files")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
    <html>
        <head>
            <title>Simple RPA UI</title>
            <script>
                var loopCounter = 0;
                var inLoop = false;

                // Function to add an action to the form
                function addAction(indentLevel = 0) {
                    var actionDiv = document.createElement('div');
                    actionDiv.classList.add('action-group');
                    actionDiv.style.marginLeft = `${indentLevel * 20}px`;
                    actionDiv.innerHTML = `
                        <label for="action">Choose an action:</label>
                        <select class="action" name="actions" required onchange="toggleSelectorInput(this, ${indentLevel})">
                            <option value="">Select an action</option>
                            <option value="url">Connect to URL</option>
                            <option value="click">Click on Button</option>
                            <option value="right_click">Right Click on Element</option>
                            <option value="double_click">Double Click on Element</option>
                            <option value="hover">Hover on Element</option>
                            <option value="read">Read Text from Element</option>
                            <option value="type">Type into Input Field</option>
                            <option value="snap">Snap Screenshot</option>
                            <option value="select">Select from Dropdown</option>
                            <option value="load_file">Load Data from File</option>
                            <option value="write">Append to File</option>
                            <option value="loop">Start Loop</option>
                            <option value="loop_times">Loop Amount</option>
                            <option value="exit_loop">End Loop</option>
                            <option value="done">Done!</option>
                        </select><br><br>
                        <div class="selectorInput" style="display: none;">
                            <label for="selector">Enter the element identifier (optional):</label>
                            <input type="text" class="selector" name="selectors"><br><br>
                            <div class="typeInput" style="display: none;">
                                <label for="text">Enter the text to type:</label>
                                <input type="text" class="text" name="texts"><br><br>
                            </div>
                            <div class="selectInput" style="display: none;">
                                <label for="option">Enter the option to select:</label>
                                <input type="text" class="option" name="options"><br><br>
                            </div>
                        </div>
                        <div class="writeInput" style="display: none;">
                            <label for="write_text">Enter the text to append:</label>
                            <input type="text" class="write_text" name="write_texts"><br><br>
                            <label for="file_name">Enter the file name to append to (optional):</label>
                            <input type="text" class="file_name" name="file_names"><br><br>
                        </div>
                        <div class="fileInput" style="display: none;">
                            <label for="load_file">Upload a file to load data:</label>
                            <input type="file" class="load_file" name="load_files" accept=".txt, .csv, .json" onchange="loadFileData(this)"><br><br>
                        </div>
                        <div class="loopInput" style="display: none;">
                            <label for="loop_count">Enter the number of times to loop:</label>
                            <input type="number" class="loop_count" name="loop_counts" min="1"><br><br>
                        </div>
                    `;
                    document.getElementById('actionsContainer').appendChild(actionDiv);
                }

                // Function to show/hide input fields based on selected action
                function toggleSelectorInput(selectElement, indentLevel) {
                    var action = selectElement.value;
                    var selectorInput = selectElement.parentElement.querySelector('.selectorInput');
                    var selectorLabel = selectorInput.querySelector('label[for="selector"]');
                    var typeInput = selectElement.parentElement.querySelector('.typeInput');
                    var selectInput = selectElement.parentElement.querySelector('.selectInput');
                    var writeInput = selectElement.parentElement.querySelector('.writeInput');
                    var fileInput = selectElement.parentElement.querySelector('.fileInput');
                    var loopInput = selectElement.parentElement.querySelector('.loopInput');

                    // Show or hide input fields based on the selected action
                    if (action === 'url' || action === 'click' || action === 'right_click' || action === 'double_click' || action === 'hover' || action === 'read' || action === 'type' || action === 'select') {
                        selectorInput.style.display = 'block';
                        fileInput.style.display = 'none';
                        writeInput.style.display = 'none';
                        loopInput.style.display = 'none';
                        if (action === 'url') {
                            selectorLabel.textContent = 'Enter URL:';
                        } else {
                            selectorLabel.textContent = 'Enter the element identifier (optional):';
                        }
                        if (action === 'type') {
                            typeInput.style.display = 'block';
                            selectInput.style.display = 'none';
                        } else if (action === 'select') {
                            selectInput.style.display = 'block';
                            typeInput.style.display = 'none';
                        } else {
                            typeInput.style.display = 'none';
                            selectInput.style.display = 'none';
                        }
                        addAction(indentLevel);
                    } else if (action === 'snap') {
                        selectorInput.style.display = 'none';
                        fileInput.style.display = 'none';
                        writeInput.style.display = 'none';
                        loopInput.style.display = 'none';
                        addAction(indentLevel);
                    } else if (action === 'write') {
                        selectorInput.style.display = 'none';
                        writeInput.style.display = 'block';
                        fileInput.style.display = 'none';
                        loopInput.style.display = 'none';
                        addAction(indentLevel);
                    } else if (action === 'load_file') {
                        selectorInput.style.display = 'none';
                        fileInput.style.display = 'block';
                        writeInput.style.display = 'none';
                        loopInput.style.display = 'none';
                        addAction(indentLevel);
                    } else if (action === 'loop') {
                        selectorInput.style.display = 'none';
                        fileInput.style.display = 'none';
                        writeInput.style.display = 'none';
                        loopInput.style.display = 'none';
                        inLoop = true;
                        loopCounter++;
                        addAction(indentLevel + 1);
                    } else if (action === 'loop_times') {
                        selectorInput.style.display = 'none';
                        fileInput.style.display = 'none';
                        writeInput.style.display = 'none';
                        loopInput.style.display = 'block';
                        addAction(indentLevel);
                    } else if (action === 'exit_loop') {
                        selectorInput.style.display = 'none';
                        fileInput.style.display = 'none';
                        writeInput.style.display = 'none';
                        loopInput.style.display = 'none';
                        inLoop = false;
                        loopCounter--;
                        if (loopCounter > 0) {
                            addAction(indentLevel - 1);
                        } else {
                            addAction();
                        }
                    } else if (action === 'done') {
                        document.getElementById('submitBtn').style.display = 'block';
                    } else {
                        selectorInput.style.display = 'none';
                        fileInput.style.display = 'none';
                        writeInput.style.display = 'none';
                        loopInput.style.display = 'none';
                    }
                }

                // Function to handle file upload and load data
                function loadFileData(input) {
                    var file = input.files[0];
                    var formData = new FormData();
                    formData.append("file", file);

                    fetch("/load_file", {
                        method: "POST",
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('result').innerHTML = `<pre style="white-space: pre-wrap;">${data.content}</pre>`;
                    })
                    .catch(error => {
                        console.error("Error loading file:", error);
                        document.getElementById('result').innerHTML = "Error loading file.";
                    });
                }

                // Add initial action on page load
                window.onload = function() {
                    addAction();
                    document.getElementById('submitBtn').style.display = 'none';
                }
            </script>
        </head>
        <body>
            <h1>Welcome to Simple RPA UI</h1>
            <p>This is a simplified process planner for your RPA.</p>
            <div style="display: flex;">
                <form action="/result" method="post" enctype="multipart/form-data" style="flex: 1;">
                    <div id="actionsContainer"></div>
                    <button type="submit" id="submitBtn">Submit</button>
                </form>
                <div id="result" style="flex: 1; padding: 20px; overflow-wrap: break-word;">
                </div>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Endpoint to handle file upload and load data
@app.post("/load_file")
async def load_file(file: UploadFile = File(...)):
    try:
        content = file.file.read().decode('utf-8')
        return JSONResponse(content={"content": content})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

# Endpoint to handle form submission and execute actions
@app.post("/result", response_class=HTMLResponse)
async def submit_url(
    actions: list[str] = Form(...),
    selectors: list[str] = Form(None),
    texts: list[str] = Form(None),
    options: list[str] = Form(None),
    loop_counts: list[str] = Form(None),
    load_files: list[UploadFile] = Form(None),
    write_texts: list[str] = Form(None),
    file_names: list[str] = Form(None)
):
    try:
        r.init(turbo_mode=True, headless_mode=False)
        action_messages = []
        screenshots = []
        written_files = []

        # Function to execute individual actions
        def execute_action(action, selector, text, option, file, write_text, file_name):
            if action == "url" and selector:
                r.url(selector)
                return f"Connected to URL: {selector}"
            elif action == "click" and selector:
                r.click(selector)
                return f"Clicked on button ID: {selector}"
            elif action == "right_click" and selector:
                r.rclick(selector)
                return f"Right-clicked on element ID: {selector}"
            elif action == "double_click" and selector:
                r.dclick(selector)
                return f"Double-clicked on element ID: {selector}"
            elif action == "hover" and selector:
                r.hover(selector)
                return f"Hovered over element ID: {selector}"
            elif action == "read" and selector:
                read_text = r.read(selector)
                return f"Read text from ID {selector}: {read_text}"
            elif action == "type" and selector and text:
                r.type(selector, text)
                return f"Typed text into ID {selector}: {text}"
            elif action == "snap":
                filename = f"screenshot_{uuid.uuid4().hex}.png"
                file_path = os.path.join("screenshots", filename)
                r.wait(0.5)
                r.snap('page', file_path)
                screenshots.append(file_path)
                return f"Screenshot saved as {filename}"
            elif action == "select" and selector and option:
                r.select(selector, option)
                return f"Selected option {option} from ID {selector}"
            elif action == "load_file" and file:
                content = file.file.read().decode('utf-8')
                return f"Loaded data from file: {file.filename} with content: {content}"
            elif action == "write" and write_text:
                if file_name:
                    file_path = os.path.join("written_files", file_name)
                else:
                    file_path = f"written_files/written_{uuid.uuid4().hex}.txt"
                r.write(file_path, write_text)
                written_files.append(file_path)
                return f"Appended text to file: {file_path}"

        i = 0
        while i < len(actions):
            action = actions[i]
            selector = selectors[i] if i < len(selectors) else None
            text = texts[i] if i < len(texts) else None
            option = options[i] if i < len(options) else None
            file = load_files[i] if i < len(load_files) else None
            write_text = write_texts[i] if i < len(write_texts) else None
            file_name = file_names[i] if i < len(file_names) else None
            loop_count = int(loop_counts[i]) if i < len(loop_counts) and loop_counts[i].isdigit() else 1

            # Handle looping actions
            if action == "loop_times":
                loop_actions = []
                loop_selectors = []
                loop_texts = []
                loop_options = []
                loop_files = []
                loop_write_texts = []
                loop_file_names = []
                i += 1
                while i < len(actions) and actions[i] != "exit_loop":
                    loop_actions.append(actions[i])
                    loop_selectors.append(selectors[i] if i < len(selectors) else None)
                    loop_texts.append(texts[i] if i < len(texts) else None)
                    loop_options.append(options[i] if i < len(options) else None)
                    loop_files.append(load_files[i] if i < len(load_files) else None)
                    loop_write_texts.append(write_texts[i] if i < len(write_texts) else None)
                    loop_file_names.append(file_names[i] if i < len(file_names) else None)
                    i += 1

                for _ in range(loop_count):
                    for loop_action, loop_selector, loop_text, loop_option, loop_file, loop_write_text, loop_file_name in zip(loop_actions, loop_selectors, loop_texts, loop_options, loop_files, loop_write_texts, loop_file_names):
                        result = execute_action(loop_action, loop_selector, loop_text, loop_option, loop_file, loop_write_text, loop_file_name)
                        if result:
                            action_messages.append(result)

                action_messages.append(f"Executed loop {loop_count} times with actions: {', '.join(loop_actions)}")
            elif action != "exit_loop":
                result = execute_action(action, selector, text, option, file, write_text, file_name)
                if result:
                    action_messages.append(result)
            i += 1

        # Generate HTML content for the result page
        screenshot_html = "".join(f'<img src="/screenshots/{os.path.basename(screenshot)}" alt="{screenshot}" style="max-width:100%"><br>' for screenshot in screenshots)
        written_files_html = "".join(f'<a href="/written_files/{os.path.basename(written_file)}" download>{os.path.basename(written_file)}</a><br>' for written_file in written_files)

        html_content = f"""
        <html>
            <head>
                <title>Actions Executed</title>
            </head>
            <body>
                <h1>Actions Executed</h1>
                {"".join(f"<p>{msg}</p>" for msg in action_messages if not msg.startswith('Executed loop'))}
                <p>{', '.join([msg for msg in action_messages if msg.startswith('Executed loop')])}</p>
                <a href="/">Perform another action</a><br>
                {screenshot_html}
                <h2>Written Files</h2>
                {written_files_html}
            </body>
        </html>
        """
    except Exception as e:
        html_content = f"""
        <html>
            <head>
                <title>Error</title>
            </head>
            <body>
                <h1>Error</h1>
                <p>There was an error processing the actions.</p>
                <p>Error details: {str(e)}</p>
                <a href="/">Perform another action</a>
            </body>
        </html>
        """
    finally:
        r.close()
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)