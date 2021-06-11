sudo docker build -t score_calc .
sudo docker login -u AWS -p $(aws ecr get-login-password --region us-east-1) 624397731385.dkr.ecr.us-east-1.amazonaws.com
sudo docker tag score_calc:latest 624397731385.dkr.ecr.us-east-1.amazonaws.com/score_calc:latest
sudo docker push 624397731385.dkr.ecr.us-east-1.amazonaws.com/score_calc:latest