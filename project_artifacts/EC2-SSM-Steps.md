## Step1: Install Session Manager Plugin
winget install --id Amazon.SessionManagerPlugin --accept-package-agreements --accept-source-agreements.

(Or download the 1-click installer: SessionManagerPluginSetup.exe)

## Step2: Start port forwarding (Session Manager)

$env:Path += ";C:\Program Files\Amazon\SessionManagerPlugin\bin"
$params = '{\"portNumber\":[\"8080\"],\"localPortNumber\":[\"18080\"]}'

aws ssm start-session `
  --target i-03e7a9837cadbced6 `
  --profile hv-capstone `
  --region us-east-1 `
  --document-name AWS-StartPortForwardingSession `
  --parameters $params

Once running, it will output: Starting session with SessionId... Port 18080 opened for sessionId... Waiting for connections...

Then open http://localhost:18080 in your browser!