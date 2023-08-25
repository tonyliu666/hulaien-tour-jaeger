FROM python:3.10.0-alpine3.15
WORKDIR /app
COPY . . 
RUN python -m venv myproject
# ENTRYPOINT ../../app/myproject/Scripts/activate
# CMD ["Activate.ps1","/app/Scripts"]
RUN source myproject/bin/activate
RUN apk add build-base 
RUN apk add curl unzip libexif udev chromium chromium-chromedriver xvfb && \
	pip install selenium && \
	pip install pyvirtualdisplay
RUN apk add linux-headers
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r web/requirements.txt 
RUN pip install flask 
RUN pip install psycopg2-binary
RUN pip install opentelemetry-api
RUN pip install opentelemetry-sdk
RUN pip install opentelemetry-instrumentation-flask
RUN pip install opentelemetry-instrumentation-requests
RUN pip install psutil 
# RUN pip install jaeger_client
# opentelemtry-distro install API,SDK
# for auto instrumentation
RUN pip install opentelemetry-distro
RUN pip install opentelemetry-instrumentation  
RUN pip install opentelemetry-exporter-jaeger
# RUN pip install opentelemetry-ext-jaeger
# RUN pip install opentelemetry-exporter-otlp
# RUN pip install -Iv protobuf==3.20.1
#####

HEALTHCHECK --interval=5s --timeout=5s --start-period=30s --retries=3 CMD curl --fail localhost || exit 1
# ENTRYPOINT ["python","/app/src/main.py"]
