# Tsunami-demo

The assignment was to build a framework which will utilize Tsunami Security Scanner to scan a list of servers and identify vulnerabilities on them.

## To achieve this task I have done the following: 


1. Wrote simple Python based Flask RestAPI with a POST method which recieves a JSON format payload with a list of targets.<br><br>
The targets can be in the form of IPv4, IPv6 or hostname formats, for example:

    ```
    {
        "targets": [
            "www.walla.co.il",
            "172.0.0.1",
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        ]
    }
    ```
    And example return looks as follows:
    ```
        {
        "172.17.0.2": {
            "scan_duration": "37.371s",
            "scan_findings": [
                {
                    "description": "Jupyter Notebook is not password or token protected",
                    "mainId": {
                        "publisher": "GOOGLE",
                        "value": "JUPYTER_NOTEBOOK_EXPOSED_UI"
                    },
                    "recommendation": "If it is necessary to keep running this instance of Jupyter, DO NOT expose it externally, in favor of using SSH tunnels to access it. In addition, the service should only listen on localhost (127.0.0.1), and consider restrict the access to the Jupyter Notebook using an authentication method. See https://jupyter-notebook.readthedocs.io/en/stable/security.html",
                    "severity": "CRITICAL",
                    "title": "Jupyter Notebook Exposed Ui"
                }
            ],
            "scan_status": "SUCCEEDED"
        },
        "172.17.0.4": {
            "scan_duration": "92.207s",
            "scan_findings": "No vulnerabilities detected",
            "scan_status": "SUCCEEDED"
        }
    }
    ```
    Additionally you can pass a url parameter `?raw_log=true` and it will return the full raw scan log.

2. Created a multistage docker image which fetches the tsunami-scanner and plugins repo, builds them, similar to the Dockerfile in the tsunami-scanner repo, but fetches the sourcecode from git directly. <br>
In the second stages it copies the tsunami compiled binaries and installs the tsunami-restapi requirements. <br>
Then it runs the `tsunami-restapi/tsunami-restapi.py` flask app.

3. Created a simple kubernetes deployment yaml for the app.

## How to deploy

Disclaimer: I was using docker desktop kubernetes for development and testing purposes.

1. If your system doesn't have access to dockerhub, build the Dockerfile, tag and push to your private repo. <br>
    Edit the `deploy/tsunami-demo.yaml file `image: ` section to match the repo and image name.

2. Go to the deploy directory and run: `k deploy -f tsunami-demo.yaml`.

3. Run `k get pods` and copy the name of the pod starting with `tsunami-demo`

4. Run the following command `k port-forward tsunami-demo-858d6b97c5-hg6cp 5000:5000` <br> This will make the pods app port available locally at `127.0.0.1:5000`

5. Use a tool, like Postman to send a POST request with a JSON payload in the following format:

    ```
    {
        "targets": [
            "www.walla.co.il",
            "172.0.0.1",
        ]
    }
    ```



