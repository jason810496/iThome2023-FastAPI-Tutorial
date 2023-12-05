from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/",response_class=HTMLResponse)
async def root():
    return '''
    <html>
        <head>
            <title>Frontend</title>
        </head>
        <body>
            <h1>Test Frontend Fetch</h1>
            <p>Enter the route of the backend to fetch data from:</p>
            <input id="url" value="/api/users" />
            <button onclick="fetchData()">Fetch Data</button>
            <pre id="result"></pre>
            
            <script>
                async function fetchData() {
                    const url = 'http://localhost:8001' + document.getElementById('url').value;
                    const response = await fetch(url);
                    const data = await response.text();
                    document.getElementById('result').innerText = data;
                }
            </script>
        </body>
    '''