################################################################################
# variables
################################################################################

# pyenv env
ENVIRONMENT=backend
# region
GCP_REG=
# project id
GCP_PROJ_ID
# image
IM_NAME=secret-box
# artifact registry
GCP_AR=
# memory
GAR_MEM=

################################################################################
# unicorn
################################################################################

uvicorn_run_service:
	uvicorn api:fast_api_app --host 0.0.0.0 --port 8000

################################################################################
# pyenv
################################################################################

pyenv_list_environments:
	pyenv virtualenvs

pyenv_install_python_version:
	pyenv install 3.10.13

pyenv_set_local_python_version:
	pyenv local 3.10.13

pyenv create_virtualenv:
	python -m venv venv

pyenv_create_virtualenv_with_python_version:
	pyenv virtualenv 3.10.13 ${ENVIRONMENT}

pyenv_activate_env:
	pyenv activate ${ENVIRONMENT}

pyenv_uninstall_env:
	pyenv uninstall ${ENVIRONMENT}

pyenv_deactivate:
	pyenv deactivate

pyenv_local: # associates env with current directory
	pyenv local ${ENVIRONMENT}

################################################################################
# shell
################################################################################

shell_restart:
	exec "$SHELL"

################################################################################
# curl
################################################################################

curl_get_response:
	curl -X POST http://localhost:8000/get-response \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello MemoryBot"}'

curl_get_mp3:
	curl -X POST http://localhost:8000/tts_gtts \
	 -H "Content-Type: application/json" \
	 -d '{"text": "Hello MemoryBot"}' \
	 --output response_output.mp3

curl_ask:
	curl -X POST http://localhost:8000/ask \
	-H "Content-Type: application/json" \
	-d '{"text": "Que sait tu de moi ?"}'

curl_isalive_check:
	curl http://0.0.0.0:8000

################################################################################
# Docker
################################################################################

### local

docker_local_build_image_arm:
	docker build \
	-f "docker/Dockerfile_AllInOne" \
	--tag=${IM_NAME}:dev \
	.

docker_local_start_interactive:
	docker run \
	-it \
	-e PORT=8000 \
	-p 8000:8000 \
	${IM_NAME}:dev \
	bash

docker_local_start:
	docker run \
	-e "PORT=8000" \
	-p 8000:8000 \
	${IM_NAME}:dev

docker_local_build_image_amd64:
	docker build \
	-f "docker/Dockerfile_AllInOne" \
	--platform linux/amd64 \
	--tag=${IM_NAME}:dev \
	.

### GCP

docker_build_api_machine_amd64_prod:
	docker build \
	--platform linux/amd64 \
	--tag=${GCP_REG}-docker.pkg.dev/${GCP_PROJ_ID}/${GCP_AR}/${IM_NAME}:prod \
	.

docker_push_prod:
	docker push \
	${GCP_REG}-docker.pkg.dev/${GCP_PROJ_ID}/${GCP_AR}/${IM_NAME}:prod

docker_run_prod:
	gcloud run deploy \
	--image ${GCP_REG}-docker.pkg.dev/${GCP_PROJ_ID}/${GCP_AR}/${IM_NAME}:prod \
	--memory ${GAR_MEM} \
	--region ${GCP_REG}

# GCP CONFIG ###################################################################

gcp_auth_configure_docker:
	gcloud auth configure-docker ${GCP_REG}-docker.pkg.dev

gcp_ar_create_repo:
	gcloud artifacts repositories create ${GCP_AR} \
	--repository-format=docker \
	--location=${GCP_REG} \
	--description="tiab repo"

# GCP BUILD, PUSH, DEPLOY ######################################################

# gcp_docker_build:
# 	docker build \
# 	--platform linux/amd64 \
# 	-t ${GCP_REG}-docker.pkg.dev/${GCP_PROJ_ID}/${GCP_AR}/${GCP_AR_IMAGE}:prod .

# gcp_docker_push:
# 	docker push ${GCP_REG}-docker.pkg.dev/${GCP_PROJ_ID}/${GCP_AR}/${GCP_AR_IMAGE}:prod

# gcp_cloud_run_deploy:
# 	gcloud run deploy \
# 	--image ${GCP_REG}-docker.pkg.dev/${GCP_PROJ_ID}/${GCP_AR}/${GCP_AR_IMAGE}:prod \
# 	--memory ${GAR_MEM} \
# 	--region ${GCP_REG}
