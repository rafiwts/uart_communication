# Clone project

This is the README for the project. It explains how to set up and run the app locally and with Docker.

## Prerequisites

Before you begin, make sure you have the following installed:

- **Python 3.13**
- **Docker** for installation refer to docker's [documentation](https://docs.docker.com/engine/install/)
- **`pip`** package manager
- **`socat`** installed on the server

---

## Running the App Locally

Follow the steps below to run the app locally:

### Step 1: Clone the Repository

If you haven't already, clone the repository to your local machine and go to the project:

```bash
git clone https://github.com/rafiwts/uart_communication

cd uart_communication
```

Ensure that you have socat installed on your Ubuntu server and that logs folder is in the root directory:

```bash
sudo apt install socat

mkdir logs
```

### Step 2: Set Up a Virtual Environment
Run the following commands to create a virtual environment and activate it:

```bash
python3 -m venv venv

source venv/bin/activate
```

### Step 3: Install dependencies
Ensure that you have the requirements.txt file in the project directory. Install all the necessary dependencies with the following command:

```bash
pip install -r requirements.txt
```

### Step 4: Start app
#### 4.1 Starting with default parameters:
You can start the application using commands that set up a virtual UART device and run the necessary app components. Please note that this will run the app with default parameters. Running the app with cli parameters and environment variables will be described in the next section. Follow the steps below.

Run a command to simulate the serial communication between the app and device. It will use a default port `/dev/ttyUSB0` if the environment variable is not defined:

```bash
sudo socat PTY,link=${DEVICE:-/dev/ttyUSB0},raw,echo=0 PTY,link=/tmp/virtual_uart2,raw,echo=0
```
As a next step, start the virtual sensor from the root directory that will handle all commands sent from our app.

```bash
sudo python3 -m app.device.device
```

At last, start app from the root project directory:

```bash
python3 -m app.main
```

You can access the application providing it the port open for connections. Once you open the website, the GUI should be self-explanatory to use. All client and device logs are stored in `logs/app.log` directory. To track logs, you can run the following command from the project's root directory:

```bash
tail -f logs/app.log
```

#### 4.2 Starting with custom parameters
It is possible to start the application with custom parameters which can be defined in environment variables or in cli commands. The list of default parameters is as follows:
For client
host - 0.0.0.0 - to run locally and on docker
port - 7100
baudrate - 152000
virtual serial port - /dev/ttyUSB0
sqlite db path - database.db

For device:
baudrate - 152000
sqlite db path - database.db

If you want to configure the app so that it runs on port 8888 with database path in `app/data.db`, baudrate 50, and device port `/dev/mockport` you can define environment variables:

```bash
export PORT=8888
export DATABASE_PATH=app/data.db
export BAUDRATE=50
export DEVICE=/dev/mockport
```
and then run commands as in the previous section or you can do it via cli commands:

```bash
sudo socat PTY,link=${DEVICE:-/dev/mockport},raw,echo=0 PTY,link=/tmp/virtual_uart2,raw,echo=0

sudo python3 -m app.device.device --baudrate 50 --database /app/data.db

python3 -m app.main --port 8888 ---database /app/data.db --baudrate 50 --device /dev/mockport
```

## Using docker
### 1.1 Running container with default parameters:
If you want to run the app in the docker with default values, you can simply make use of a `Dockerfile` defined in the project's root directory.

```bash
docker build -t clone-app .

docker run -p 7100:7100 --name clone clone-app
```
For following logs use:

```bash
docker exec -it clone tail -f logs/app.log
```

### 1.2 Running containers with custom parameters

## 1.2.1 Environment variables:

In the project, it is possible to find the `.env` folder with pre-defined environment variables that you can customize. Example:

```bash
HOST=0.0.0.0
PORT=8888
BAUDRATE=50
DATABASE_PATH=app/data.db
DEVICE=/dev/mockport
```

After customizing environment variables build an image and run the container as follows:

```bash
docker build -t clone-app .

docker run --env-file .env -p 8888:8888 --name=clone clone-app
```

Alternatively, you can pass all environment variables in the command:

```bash
docker run -p 8888:8888 --name clone \
-e PORT=8888 \
-e BAUDRATE=50 \
-e DATABASE_PATH=app/data.db \
-e DEVICE=/dev/mockport \
clone-app
```

## 1.2.2 Cli parameters:

For parameters passed upon running cli commands the syntax is as follows:

```bash
docker build -t clone-app .

docker run -p 8888:8888 -e DEVICE=/dev/mockport --name clone clone-app --port 8888 --database app/data.db --baudrate 50
```

Note that an extra environment variable has to be passed to match `--device` parameter.

You can run client tests for endpoints with

```bash
docker exec -it clone pytest
,,,
