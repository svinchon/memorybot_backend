# VENV #########################################################################
# included in python 3.3+
# https://docs.python.org/3/library/venv.html
# https://docs.python.org/3/library/venv.html#creating-virtual-environments
# storage in local .venv directory
# uses currenrt python version
create_venv:
	python -m venv .venv
activate_venv:
	source .venv/bin/activate
deactivate_venv:
	deactivate
# PYENV ########################################################################
# requires installation of pyenv-virtualenv
# storage in ~/.pyenv
# uses python version specified in .python-version
# separate python version and virtualenv
pyenv_create: # assocites env with pyhton version
	pyenv virtualenv 3.10.12 local_llm
pyenv_activate:
	pyenv activate local_llm
pyenv_deactivate:
	pyenv deactivate
pyenv_local: # associates env with current directory
	pyenv local local_llm
# PIP ##########################################################################
list_libs:
	pip freeze > libs.txt
install_libs:
	pip install pyaudio
	pip install SpeechRecognition
	pip install python-dotenv
	pip install openai
	pip install sentence-transformers
	pip install faiss-cpu
	pip install virtualenv

# RUN ##########################################################################
run_memorybot:
	.venv/bin/python ./main.py
# VARIOUS ######################################################################
where_am_i:
	@echo $(shell pwd)

	pyenv deactivate
