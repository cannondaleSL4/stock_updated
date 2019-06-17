FROM nickgryg/alpine-pandas:latest
COPY ./application /my-quotes/application

RUN apk add musl-dev wget git build-base && \
    pip3 install -r /my-quotes/application/requirements.txt

# TA-Lib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
  cd ta-lib/ && \
  ./configure --prefix=/usr && \
  make && \
  make install
RUN git clone https://github.com/mrjbq7/ta-lib.git /ta-lib-py && cd ta-lib-py && python setup.py install && \
    apk del musl-dev wget git build-base
RUN rm ./ta-lib-0.4.0-src.tar.gz

ENTRYPOINT ["python3"]
CMD ["/my-quotes/application/start.py" ]