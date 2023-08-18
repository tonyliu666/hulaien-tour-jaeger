# FROM fluent/fluentd:edge
# FROM fluent/fluentd:v1.8-debian
FROM fluent/fluentd:v1.12.0-debian-1.0
# FROM fluent/fluentd:v1.14.5-1.1
USER root
# RUN fluent-gem install fluent-plugin-elasticsearch -v 5.2.0
# RUN gem install faraday-net_http -v 2.1.0
# RUN gem install fluent-plugin-elasticsearch -v 4.3.3 
RUN gem uninstall -I elasticsearch && gem install elasticsearch -v 7.17.0
RUN ["gem", "install", "fluent-plugin-elasticsearch", "--no-document", "--version", "5.0.3"]
#RUN fluent-gem install fluent-plugin-elasticsearch 
# RUN fluent-gem install elasticsearch -v 7.12
# RUN gem install fluent-plugin-rewrite-tag-filter
RUN fluent-gem install fluent-plugin-multi-format-parser
USER fluent
