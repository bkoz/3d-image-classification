FROM registry.access.redhat.com/ubi8/python-36:1-170.1648121369 
USER root
COPY . /app
WORKDIR /app
EXPOSE 5000
RUN pip install --upgrade pip && pip install -r requirements.txt

ENV MODEL_NAME MyModel
ENV API_TYPE REST
ENV SERVICE_TYPE MODEL
ENV PERSISTENCE 0

# CMD exec seldon-core-microservice $MODEL_NAME $API_TYPE --service-type $SERVICE_TYPE --persistence $PERSISTENCE --log-level DEBUG
CMD exec seldon-core-microservice $MODEL_NAME --service-type $SERVICE_TYPE --persistence $PERSISTENCE --log-level INFO
