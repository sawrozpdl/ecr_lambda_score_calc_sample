Docker name and lambda name chosen: score_calc

Create a ECR repository
After creation, a repository URL will be obtained such as
`624397731385.dkr.ecr.us-east-1.amazonaws.com/score_calc`
which will be used in the following deploy commands.

Then, build the docker image
> sudo docker build -t score_calc .

Add a tag to the image matching the repo URL
> sudo docker tag score_calc:latest 624397731385.dkr.ecr.us-east-1.amazonaws.com/score_calc:latest

Login to the docker repository with the AWS ECR credentials
> sudo docker login -u AWS -p $(aws ecr get-login-password --region us-east-1) 624397731385.dkr.ecr.us-east-1.amazonaws.com

Deploy the container to the repository
> sudo docker push 624397731385.dkr.ecr.us-east-1.amazonaws.com/score_calc:latest

Create a lambda function with this created image
Or,
Just update it with this deployed image.

Link the lambda with AWS Gateway REST api with Lambda proxy integration: ON

For quick deployment,
use:
> sh ./deploy.sh
after tweaking the values with respective created ones.