################################################################################
# variables
################################################################################

ENVIRONMENT=backend

################################################################################
# unicorn
################################################################################

uvicorn_run_service:
	uvicorn main:app --host 0.0.0.0 --port 8000

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
# python
################################################################################

python_install_libs:
	pip install fastapi
	pip install pyttsx3
	pip install uvicorn
	pip install gtts
	pip install python-multipart

python_run_main:
	python main.py

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

curl_test:
	curl -X POST http://localhost:8000/stt \
	-H "Content-Type: multipart/form-data" \
	-F "file=@audio.wav;type=audio/mpeg"
