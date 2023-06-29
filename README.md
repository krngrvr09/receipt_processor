# Receipt Processor

### Running Instructions

1. If Docker is installed on the system and the OS is Linux, run `./run_server.sh`. It will build the docker image and run it. The server will be serving requests at `127.0.0.1:8000`.
2. If you are running the application on an OS other than Linux, then you can look at the two docker commands inside `run_server.sh` and run them on your own.
2. If docker is not installed, run `python3 server.py`. This will run the server, and it will be serving requests at `127.0.0.1:8000`.

### Dependencies
1. Python3 - [Installation Instructions](https://docs.python-guide.org/starting/install3/linux/)


### Notes
1. The regex for `retailer` is possibly incorrect in the `api.yaml` file. The given regex is `^\\S+$`. This does not accept spaces. However, one of the examples is `M&M Corner Market`. I think the correct regex could be: `^[\ \S]+$`. This is what I have used in `utils.py`
2. I have created two classes `Receipt` and `Item` in `receipt.py` to encapsulate incoming data into an object.
3. I have added all regex patterns to `utils.py` which is used in both `server.py` and `receipt.py`
4. For the GET request, I am doing input validation even though input is just a string that is being checked in the dictionary. This is because, in reality we would have a database and it's good practice to do input validation before querying the database.
