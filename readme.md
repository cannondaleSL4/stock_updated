For using application:

1.1 `pip3 install flask flask_bootstrap numpy pandas`

1.2 for analyse i have used `talib` lib and have some problem with. for non-docker solution should use that [link](https://github.com/otassel/docker-python-talib/blob/master/python-3.7-alpine/Dockerfile#L14)

1.3 `export FLASK_APP=./application/views.py`

1.4 `python3 -m flask run`

1.5 Set env `MAIL_USERNAME` and `EMAIL_PASSWORD` for sending result of analysis

Or just use docker 

2.1 `docker build --network host -t my-quotes .`

2.2 `docker run -itd --name my-quotes --net=host -p 8080:8080 my-quotes -e MAIL_USERNAME="${MAIL_USERNAME}" -e MAIL_PASSWORD="${MAIL_PASSWORD}"`

2.2.1 `docker run -itd --name my-quotes --net=host -v $HOME/dq:/dq -p 8080:8080 my-quotes -e MAIL_USERNAME="${MAIL_USERNAME}" -e MAIL_PASSWORD="${MAIL_PASSWORD}"` - in case you need data for export to mt 4/5


https://mrjbq7.github.io/ta-lib/install.html