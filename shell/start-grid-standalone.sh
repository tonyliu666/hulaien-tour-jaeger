#!/bin/bash -x
export PATH="$PATH:/home/seluser/.local/share/coursier/bin"
./cs install cs 
./cs install coursier
cs setup --yes
java -Dotel.traces.exporter=jaeger \
       -Dotel.exporter.jaeger.endpoint=http://Jaeger:14250 \
       -Dotel.resource.attributes=service.name=selenium-standalone \
       -jar /opt/selenium/selenium-server.jar \
       --ext $(coursier fetch -p \
          io.opentelemetry:opentelemetry-exporter-jaeger:1.15.0 \
          io.grpc:grpc-netty:1.45.0) \
       standalone