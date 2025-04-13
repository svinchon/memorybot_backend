activate_venv:
	source .venv/bin/activate

list_libs:
	pip freeze > libs.txt

install_libs:
	pip install pyaudio
	pip install SpeechRecognition
	pip install python-dotenv
	pip install openai
	pip install sentence-transformers
	pip install faiss-cpu

run_memorybot:
	.venv/bin/python ./main.py

create_venv:
	python3 -m venv .venv
