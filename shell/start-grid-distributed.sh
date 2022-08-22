#!/bin/bash -x
export PATH="$PATH:/home/seluser/.local/share/coursier/bin"
./cs install cs 
./cs install coursier
cs setup --yes
java -Dotel.traces.exporter=jaeger \
     -Dotel.exporter.jaeger.endpoint=http://Jaeger:14250 \
     -Dotel.resource.attributes=service.name=selenium-event-bus \
     -jar /opt/selenium/selenium-server.jar \
     --ext $(coursier fetch -p \
          io.opentelemetry:opentelemetry-exporter-jaeger:1.15.0 \
          io.grpc:grpc-netty:1.45.0) \
     event-bus &
sleep 2
java -Dotel.traces.exporter=jaeger \
     -Dotel.exporter.jaeger.endpoint=http://Jaeger:14250 \
     -Dotel.resource.attributes=service.name=selenium-sessions \
     -jar /opt/selenium/selenium-server.jar \
     --ext $(coursier fetch -p \
          io.opentelemetry:opentelemetry-exporter-jaeger:1.15.0 \
          io.grpc:grpc-netty:1.45.0) \
     sessions &
sleep 2
java -Dotel.traces.exporter=jaeger \
     -Dotel.exporter.jaeger.endpoint=http://Jaeger:14250 \
     -Dotel.resource.attributes=service.name=selenium-session-queue \
     -jar /opt/selenium/selenium-server.jar \
     --ext $(coursier fetch -p \
          io.opentelemetry:opentelemetry-exporter-jaeger:1.15.0 \
          io.grpc:grpc-netty:1.45.0) \
     sessionqueue &
sleep 2
java -Dotel.traces.exporter=jaeger \
     -Dotel.exporter.jaeger.endpoint=http://Jaeger:14250 \
     -Dotel.resource.attributes=service.name=selenium-distributor \
     -jar /opt/selenium/selenium-server.jar \
     --ext $(coursier fetch -p \
          io.opentelemetry:opentelemetry-exporter-jaeger:1.15.0 \
          io.grpc:grpc-netty:1.45.0) \
     distributor --sessions http://localhost:5556 --sessionqueuer http://localhost:5559 --bind-bus false &
sleep 2
java -Dotel.traces.exporter=jaeger \
     -Dotel.exporter.jaeger.endpoint=http://Jaeger:14250 \
     -Dotel.resource.attributes=service.name=selenium-router \
     -jar /opt/selenium/selenium-server.jar \
     --ext $(coursier fetch -p \
          io.opentelemetry:opentelemetry-exporter-jaeger:1.15.0 \
          io.grpc:grpc-netty:1.45.0) \
     router --sessions http://localhost:5556 --distributor http://localhost:5553 &
sleep 2
java -Dotel.traces.exporter=jaeger \
     -Dotel.exporter.jaeger.endpoint=http://Jaeger:14250 \
     -Dotel.resource.attributes=service.name=selenium-node \
     -jar /opt/selenium/selenium-server.jar \
     --ext $(coursier fetch -p \
          io.opentelemetry:opentelemetry-exporter-jaeger:1.15.0 \
          io.grpc:grpc-netty:1.45.0) \
     node -D selenium/standalone-chrome:latest '{"browserName": "chrome"}' &