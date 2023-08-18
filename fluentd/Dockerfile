FROM fluent/fluentd:edge
# FROM fluent/fluentd:v1.14.5-1.1
USER root
# RUN fluent-gem install fluent-plugin-elasticsearch -v 5.2.0
RUN fluent-gem install fluent-plugin-elasticsearch 
# RUN fluent-gem install elasticsearch -v 7.12
# RUN gem install fluent-plugin-rewrite-tag-filter
RUN fluent-gem install fluent-plugin-multi-format-parser
USER fluent
