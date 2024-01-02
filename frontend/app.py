from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
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
    """


@app.get("/yolo", response_class=HTMLResponse)
async def yolo_page_to_submit_and_get_async_result():
    return """
    <html>
        <head>
            <title>YOLO</title>
        </head>
        <body>
            <h1 style="font-weight:300">YOLO</h1>

            <pre>Upload <strong>image</strong> or <strong>video</strong> to detect objects</pre>
            <div id="upload-container">
                <form action="http://localhost:8001/yolo" method="post" enctype="multipart/form-data">
                    <input type="file" name="file" />
                </form>
                <button onclick="submitForm()">Submit</button>
            </div>
            

            <div id="loading-container" style="display: none;">
                <div class="lds-dual-ring"></div>
                <pre>Loading...</pre>
                <br>
                <pre id="detail"></pre>
            </div>
            <br>
            <div id="result-container">
            
            </div>
                
            <script>
                var job_id = "";
                var loadingContainer = document.getElementById('loading-container');
                var resultContainer = document.getElementById('result-container');
                var detailContainer = document.getElementById('detail');

                async function submitForm() {
                    const url = 'http://localhost:8001/yolo/task';
                    const form = document.querySelector('form');
                    const formData = new FormData(form);
                    const response = await fetch(url, {
                        method: 'POST',
                        body: formData,
                    });
                    const data = await response.json();
                    console.log(data);
                    job_id = data.job_id;

                    // poll for result
                    resultContainer.innerHTML = ""; // clear result
                    detailContainer.innerText = ""; // clear detail

                    loadingContainer.style.display = 'block';
                    pollForResult();
                }

                async function pollForResult(){
                    const url = `http://localhost:8001/yolo/task/${job_id}`;
                    const response = await fetch(url);
                    const data = await response.json();
                    console.log(data);
                    // update detail
                    detailContainer.innerText = `Timestamp: ${new Date().toLocaleString()}\n`;
                    for (const [key, value] of Object.entries(data)) {  
                        detailContainer.innerText += `${key}: ${value}\n`;
                    }

                    if(data.status == "SUCCESS"){
                        // show result
                        showResult();
                    }else{
                        setTimeout(pollForResult, 1000);
                    }
                }

                async function showResult(){
                    const url = `http://localhost:8001/yolo/task/${job_id}/result`;
                    const response = await fetch(url);
                    const data = await response.blob();
                    console.log(data);

                    loadingContainer.style.display = 'none';    

                    const resultContainer = document.getElementById('result-container');
                    const mediaType = response.headers.get('content-type');
                    if(mediaType.startsWith('image')){
                        const img = document.createElement('img');
                        img.style.width = '500px';
                        img.src = URL.createObjectURL(data);
                        resultContainer.appendChild(img);
                    }else if(mediaType.startsWith('video')){
                        const video = document.createElement('video');
                        video.style.width = '500px';
                        video.src = URL.createObjectURL(data);
                        video.controls = true;
                        resultContainer.appendChild(video);
                    }
                }
            </script>

            <style>
                #upload-container {
                    margin: 20px 0 20px 0;
                    display: flex;
                    width: 300px;
                    height: 30px;
                    justify-content: space-between;
                }

                #result-container {
                    width: 500px;
                }
            
                /* loading animation */
                .lds-dual-ring {
                display: inline-block;
                width: 80px;
                height: 80px;
                }
                .lds-dual-ring:after {
                content: " ";
                display: block;
                width: 64px;
                height: 64px;
                margin: 8px;
                border-radius: 50%;
                border: 6px solid #5e5959;
                border-color: #5e5959 transparent #5e5959 transparent;
                animation: lds-dual-ring 1.2s linear infinite;
                }
                @keyframes lds-dual-ring {
                0% {
                    transform: rotate(0deg);
                }
                100% {
                    transform: rotate(360deg);
                }
                }

            </style>
        </body>
    """
