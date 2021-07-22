# gcs-cas_page-monitor-service
Page monitor microservice in GCS Acquisition

## Prerequisites:

### IBM MQ Libraries setup
Everyone will need to set this up - you will get pip errors on pymqi or build errors if it isn't
#### local development setup
You will need to download and unzip the correct redistributable IBM MQ Library for your local system 
(check the `layers/ibm_mq/ibm_mq_docker_build` `TAR_GZ_FILE` variable for the correct current version number)

Mac:
- lib: https://public.dhe.ibm.com/ibmdl/export/pub/software/websphere/messaging/mqdev/mactoolkit/
- unpack to whatever file location you want locally
- add these environment variables to your .bashrc or appropriate terminal profile:
```shell script
export PATH="[your-mq-lib-directory]/bin:/path-to-lib/[your-mq-lib-directory]/samp/bin:$PATH"
export DYLD_FALLBACK_LIBRARY_PATH=[your-mq-lib-directory]/lib64
```  
- Mac El Capitan+ locks down use of the various `*_LIBRARY_PATH` environment variables 
so in order to enable them you will need to follow these directions to turn off that restriction:
https://osxdaily.com/2015/10/05/disable-rootless-system-integrity-protection-mac-os-x/
- also xcode should be setup by default on your Mac but if for some reason you don't have it installed and you get compiler errors you may need to install it (or some sort of C compiler)

Win:
- lib: https://public.dhe.ibm.com/ibmdl/export/pub/software/websphere/messaging/mqdev/redist/
    - you'll want Win64 not Java
- unzip to : `C:\Program Files (x86)\IBM\WebSphere MQ`
    - also note - if you already have MQ installed you may have something already installed to that directory - 
    this is probably ok as long as you have the correct version and the the dirs `tools\Lib64` and `tools\c\include` exist under `WebSphere MQ` 
- the *_LIBRARY_PATH env var isn't used on Win so you may need to add the Lib64 to your PATH param ENV in .bashrc or .bash_profile:
 ```shell script
export PATH="C:\Program Files (x86)\IBM\WebSphere MQ\tools\Lib64:$PATH"
```
- add MQ_FILE_PATH ENV variable with 'WebSphere MQ' directory path as value
```shell script
export MQ_FILE_PATH="C:\Program Files (x86)\IBM\WebSphere MQ"
```
- you'll likely see an error about pymqe not found if this isn't set correctly

### To run this app:
1. Create a copy of "config/local" folder in the config directory. Call it "local-<your-initials>", e.g. local-skal
2. Create a copy of "local_variables.yaml" folder. Call it "local_variables_<your-initials>.yaml", e.g. local_variables_skal.yaml
and update with your local stack specific values
3. Install all all_requirements
```
pip install -r all_requirements.txt
```
4. Verify existing unit tests pass by running:
```
python -m pytest tests/unit -v
```
5. Verify existing integration tests pass by running:
```
python -m pytest tests/integration -v
```
Login to cloud-tool. You may or may not have to run the export.
```
cloud-tool -r us-east-1 -p tr-gcs-acquisition-preprod login
export AWS_PROFILE=tr-gcs-acquisition-preprod
```
4. Run sam full build
```
./sam_full_build.sh
```
5. Run sam package
```
sam package --output-template-file templates/packaged-sam-template.yaml --s3-bucket <your-s3-bucket> --profile tr-gcs-acquisition-preprod
```
6. Run sceptre command to deploy your local resources (queues, mock APIs)
```
sceptre --var-file=local_variables_<your-initials>.yaml --ignore-dependencies --debug launch -y local-<your-initials>
```
7. Create a copy of properties-local.ini under properties folder. Call it "properties-<your-initials>" e.g. properties-skal.ini
Update with your local queue arn, local API gateway endpoints for entitlement, credentials, distribution and storage
NOTE: entitlement will be its own API gateway endpoint; the other three will all be the monitor-mock-services one.
8. Start initiate_monitor.py with environment variable "ENVIRONMENT" set to your-initials
9. Drop this message on your page_monitor_request_queue_arn defined in the properties file.
NOTE: this will dedupe if the same message is rerun with 5 min, so update the "test" number.
```
{

}
```
10. Verify that the expected file is FTPed to the location specified in the eclipse_ftp_domain_map in the properties file.
The location is an s3 bucket in the CICD prod account.


### To run this app in a Docker container:
1. Install Docker on local system
2. Build docker image with command:
    docker build --build-arg ARTIFACTORY_USER={tr artifactory user id} --build-arg ARTIFACTORY_TOKEN={tr artifactory token} -t monitor-service .

3. Run docker container with command:
    docker run -v c:/Users/UXXXXXXX:/user -e AWS_DEFAULT_REGION=us-east-1 -e AWS_PROFILE=tr-gcs-acquisition-preprod -e AWS_SHARED_CREDENTIALS_FILE=/user/.aws/credentials -E ENVIRONMENT=<your-initials> --name monitor-service monitor-service

4. Clean up:
    * Stop the docker container:  docker stop monitor-service
    * Remove the docker container:  docker rm monitor-service
    * Remove the image: docker rmi monitor-service
    
### To run APITESTS:
1) Run initiate_monitor and edit configurations and add environment variables 
    page_monitor_response_queue_arn=
        arn:aws:sqs:us-east-1:732776733977:a205813-monitor-monitor-response_-<your-initials>-use1;
        ENVIRONMENT=<your-initials>;VERSION=1 e.g. ENVIRONMENT=akat
3) Run this command: pip install pytest-env
2) Open pytest.ini and add \
    env = \
        ENVIRONMENT=<your-initials> \
        VERSION=1 \
    DO NOT CHECKIN pytest.ini after making these changes. \
Or run in terminal: 
```
set ENVIRONMENT=<your-initials>
set VERSION=1
```
3) Run this command: 'pytest tests -v tests/api -n 4'


