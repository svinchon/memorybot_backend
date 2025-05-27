################################################################################
# variables
################################################################################
# pyenv env
ENVIRONMENT=backend
# region
GCP_REG=europe-west1
# project
GCP_PROJ=to-infinity-and-beyond
# project id
GCP_PROJ_ID=to-infinity-and-beyond-425409
# image
IM_NAME=secret-box
# artifact registry
GCP_AR=to-infinity-and-beyond-repo
# memory
GAR_MEM=2Gi
# intermediate image with all needed packages
BASE_IMAGE_NAME=python-ia-base-machine-amd64
# curl target url
CURL_TARGET_URL=http://0.0.0.0:8000
# CURL_TARGET_URL=https://secret-box-456003509969.europe-west1.run.app/
#
################################################################################
# unicorn
################################################################################
#
uvicorn_run_service:
	uvicorn api:fast_api_app --host 0.0.0.0 --port 8000
#
################################################################################
# pyenv
################################################################################
#
pyenv_list_environments:
	pyenv virtualenvs
#
pyenv_install_python_version:
	pyenv install 3.10.13
#
pyenv_set_local_python_version:
	pyenv local 3.10.13
#
pyenv create_virtualenv:
	python -m venv venv
#
pyenv_create_virtualenv_with_python_version:
	pyenv virtualenv 3.10.13 ${ENVIRONMENT}
#
pyenv_activate_env:
	pyenv activate ${ENVIRONMENT}
#
pyenv_uninstall_env:
	pyenv uninstall ${ENVIRONMENT}
#
pyenv_deactivate:
	pyenv deactivate
#
pyenv_local: # associates env with current directory
	pyenv local ${ENVIRONMENT}
#
################################################################################
# shell
################################################################################
#
shell_restart:
	exec "$SHELL"
#
################################################################################
# curl
################################################################################
#
curl_get_response:
	curl -X POST http://localhost:8000/get-response \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello MemoryBot"}'
#
curl_get_mp3:
	curl -X POST http://localhost:8000/tts_gtts \
	 -H "Content-Type: application/json" \
	 -d '{"text": "Hello MemoryBot"}' \
	 --output response_output.mp3
#
curl_ask:
	curl -X POST http://localhost:8000/ask \
	-H "Content-Type: application/json" \
	-d '{"text": "Que sait tu de moi ?"}'
#
curl_isalive_check:
	curl http://0.0.0.0:8000
#
curl_store_v2_kyan:
	curl http://0.0.0.0:8000/v2/store \
	-H "Content-Type: application/json" \
	-d '{ \
	"user_id": "kyan", \
	"user_context": "test", \
	"infrag": "je suis une jeune homme promis à un grand avenir." \
	}'
#
curl_ask_v2_kyan:
	curl http://0.0.0.0:8000/v2/ask \
	-H "Content-Type: application/json" \
	-d '{ \
	"user_id": "kyan", \
	"user_context": "test", \
	"instructions": "Répond au mieux à la question.", \
	"question": "qui suis-je?" \
	}'
#
curl_store_v2_toto:
	curl http://0.0.0.0:8000/v2/store \
	-H "Content-Type: application/json" \
	-d '{ \
	"user_id": "toto", \
	"user_context": "test", \
	"infrag": "On a ecrit plein de blagues sur ma vie" \
	}'
#
curl_ask_v2_toto:
	curl http://0.0.0.0:8000/v2/ask \
	-H "Content-Type: application/json" \
	-d '{ \
	"user_id": "toto", \
	"user_context": "test", \
	"instructions": "Répond au mieux à la question.", \
	"question": "qui suis-je?" \
	}'
#
curl_ask_v2_svinchon:
	curl http://0.0.0.0:8000/v2/ask \
	-H "Content-Type: application/json" \
	-d '{ \
	"user_id": "svinchon@gmail.com", \
	"user_context": "souvenirs", \
	"instructions": "Répond au mieux à la question.", \
	"question": "detectes tu des incoherences dans mes souvenirs?" \
	}'
#
curl_debug:
	curl http://0.0.0.0:8000/debug
#
curl_get_infrags:
	curl http://0.0.0.0:8000/infrags
#
curl_post_infrags:
	curl http://0.0.0.0:8000/infrags \
	-F "file=@infrags_mgr/data/infrags.json"
#
curl_post_infrags_gcp:
	curl https://secret-box-456003509969.europe-west1.run.app/infrags \
	-F "file=@infrags_mgr/data/infrags.json"
#
curl_reload_infrags_gcp:
	curl https://secret-box-456003509969.europe-west1.run.app/reload-infrags
#
curl_ask_v2_svinchon_gcp:
	curl https://secret-box-456003509969.europe-west1.run.app/v2/ask \
	-H "Content-Type: application/json" \
	-d '{ \
	"user_id": "svinchon@gmail.com", \
	"user_context": "souvenirs", \
	"instructions": "Répond au mieux à la question.", \
	"question": "detectes tu des incoherences dans mes souvenirs?" \
	}'
#
#################################################################################
# Docker
################################################################################
#
##### One Step & local
docker_local_build_image_arm:
	docker build \
	-f "docker/Dockerfile_AllInOne" \
	--tag=${IM_NAME}:dev \
	.

docker_local_run_interactive:
	docker run \
	-it \
	-e PORT=8000 \
	-p 8000:8000 \
	${IM_NAME}:dev \
	bash

docker_local_run:
	docker run \
	-e "PORT=8000" \
	-p 8000:8000 \
	${IM_NAME}:dev

#
##### One Step & GCP
docker_gcp_build_image_amd64:
	docker build \
	--file "docker/Dockerfile_AllInOne" \
	--platform linux/amd64 \
	--tag=${GCP_REG}-docker.pkg.dev/${GCP_PROJ_ID}/${GCP_AR}/${IM_NAME}:prod \
	.

docker_gcp_push_image_amd64:
	docker push \
	${GCP_REG}-docker.pkg.dev/${GCP_PROJ_ID}/${GCP_AR}/${IM_NAME}:prod

docker_gcp_run_image:
	gcloud run deploy \
	--image ${GCP_REG}-docker.pkg.dev/${GCP_PROJ_ID}/${GCP_AR}/${IM_NAME}:prod \
	--memory ${GAR_MEM} \
	--region ${GCP_REG}

docker_gcp_one_step_do_it_all:
	make docker_gcp_build_image_amd64
	make docker_gcp_push_image_amd64
	make docker_gcp_run_image

#
##### Two Steps & GCP
# Step 1 of 2 GCP
docker_2_steps_build_base_machine_amd64:
	docker build \
	--file "docker/Dockerfile_Base" \
	--platform linux/amd64 \
	--tag=${BASE_IMAGE_NAME}:dev \
	.

# Step 2 of 2 GCP
docker_2_steps_write_datetime_to_file:
	@echo $(shell date '+%Y-%m-%d @ %H:%M:%S') > version.txt
docker_2_steps_build_final_machine_amd64_prod:
	docker build \
	--file "docker/Dockerfile_Final" \
	--platform linux/amd64 \
	--tag=${GCP_REG}-docker.pkg.dev/${GCP_PROJ_ID}/${GCP_AR}/${IM_NAME}:prod \
	.

docker_2_steps_push_final_machine_prod:
	docker push \
	${GCP_REG}-docker.pkg.dev/${GCP_PROJ_ID}/${GCP_AR}/${IM_NAME}:prod

docker_2_steps_gcp_run_deploy_final_machine_prod:
	gcloud run deploy \
	--image ${GCP_REG}-docker.pkg.dev/${GCP_PROJ_ID}/${GCP_AR}/${IM_NAME}:prod \
	--memory ${GAR_MEM} \
	--region ${GCP_REG}
# Do it all
docker_2_steps_1_of_2_do_it_all:
	make docker_2_steps_build_base_machine_amd64
docker_2_steps_2_of_2_do_it_all:
	make docker_2_steps_write_datetime_to_file
	make docker_2_steps_build_final_machine_amd64_prod
	make docker_2_steps_push_final_machine_prod
	make docker_2_steps_gcp_run_deploy_final_machine_prod
#
################################################################################
# GCP Admin
################################################################################
#
gcp_auth_login:
	gcloud auth login
	gcloud config set project ${GCP_PROJ_ID}
#
gcp_auth_configure_docker:
	gcloud auth configure-docker ${GCP_REG}-docker.pkg.dev
#
gcp_artifacts_repo_create:
	gcloud artifacts repositories create ${GCP_AR} \
	--repository-format=docker \
	--location=${GCP_REG} \
	--description="tiab repo"
#
gcp_set_service_timeout:
	gcloud run services update ${IM_NAME} \
	--timeout=900 \
	--region=${GCP_REG}
#
