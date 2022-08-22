# hualien-tour
the first python flask project using docker-compose 

### how to use ?
> command:
1. docker build -t main .(current working directory:./hulaien-tour) or using **docker pull tonyliu666/hualien-flask:latest** to pull down from docker hub
2. docker-compose -f docker-compose.yml up --build (if you would like to use detached mode ,you can add -d flag)
3. open your browser and type **localhost:8080** and enjoy using it 

*Write down my learning notes:*
>1. don't initialize your sql data using python SQLAlchemy(ORM) because of effectiveness ,instead using the original sql command(insert ,create) is much effective
>2. The environment variables in docker compose file can be stored as env file to keep secure data 
>3. docker file CMD vs ENTRYPOINT command . There are some tricks between them . 
>4. The kind of ports in docker compose file(host port and container port). Each of them has its own timing to be used.Which is better used in the certain scenario is also a key point.
>5. The use method of volumes in docker compose file should be handled carefully.Depending on your demands to decide where you store these data(host machine or docker vol.)
