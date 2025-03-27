FROM public.ecr.aws/lambda/python:3.11

RUN yum -y update && yum -y upgrade
RUN yum install git -y
RUN pip3 install --upgrade pip

WORKDIR ${LAMBDA_TASK_ROOT}

RUN git clone -b master https://github.com/OptiQuantTeam/Trader.git .

COPY requirement.txt ${LAMBDA_TASK_ROOT}
RUN pip3 install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirement.txt


CMD [ "lambda_function.lambda_handler" ]